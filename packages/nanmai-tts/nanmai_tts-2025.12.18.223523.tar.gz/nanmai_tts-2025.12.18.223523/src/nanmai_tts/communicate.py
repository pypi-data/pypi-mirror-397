"""Communicate with the Nanmai TTS service."""

import aiohttp
import asyncio
import re
import random
from typing import AsyncGenerator, Dict, Union, Optional
from contextlib import asynccontextmanager

from .auth import generate_headers
from .constants import API_URL
from .exceptions import (
    NanmaiAPIError, NetworkError, NoAudioReceived, SessionExpiredError,
    RetryExhaustedError, SPEAKABLE_PATTERN
)


class Communicate:
    """
    Communicate with the Nanmai TTS service.
    Mimics the interface of edge-tts Communicate class.
    """

    def __init__(
        self,
        text: str,
        voice: str = "DeepSeek",
        proxy: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the Communicate instance.

        Args:
            text: Text to synthesize
            voice: Voice to use (DeepSeek or Kimi)
            proxy: Proxy URL (e.g., "http://127.0.0.1:7890")
            session: Existing aiohttp ClientSession for connection pooling
        """
        if not isinstance(text, str):
            raise TypeError("text must be str")
        if not isinstance(voice, str):
            raise TypeError("voice must be str")

        # Validate voice
        if voice not in ["DeepSeek", "Kimi"]:
            raise ValueError(f"Invalid voice: {voice}. Must be 'DeepSeek' or 'Kimi'")

        self.text = self._convert_fullwidth_to_halfwidth(text)
        self.voice = voice
        self.proxy = proxy
        self._external_session = session

    def _convert_fullwidth_to_halfwidth(self, text: str) -> str:
        """Convert full-width ASCII characters to half-width equivalents."""
        result = []
        for char in text:
            code = ord(char)
            # Full-width ASCII range: U+FF01 to U+FF5E
            if 0xFF01 <= code <= 0xFF5E:
                # Convert to half-width by subtracting 0xFEE0
                halfwidth_code = code - 0xFEE0
                result.append(chr(halfwidth_code))
            elif code == 0x3000:  # Full-width space
                result.append(" ")
            else:
                result.append(char)
        return "".join(result)

    def _get_speakable_count(self, text: str) -> int:
        """Count speakable characters (CJK, Alphanumeric)."""
        return len(re.findall(r'[a-zA-Z0-9\u4e00-\u9fff]', text))

    def _smart_sanitize(self, text: str) -> str:
        """
        Smart sanitization for short texts.
        Removes non-standard symbols if text length is short to prevent API errors.
        """
        # Whitelist: CJK, Alphanumeric, Standard Punctuation, Whitespace
        whitelist_pattern = r'[^a-zA-Z0-9\u4e00-\u9fff,\.!?:;，。！？：；\s]'
        return re.sub(whitelist_pattern, '', text)

    @asynccontextmanager
    async def _get_session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """Context manager to handle internal vs external session."""
        if self._external_session:
            # Check if external session is still valid
            if self._external_session.closed:
                raise SessionExpiredError("External session has been closed")
            # Use external session, do not close it
            yield self._external_session
        else:
            # Create new session, close it afterwards
            async with aiohttp.ClientSession() as session:
                yield session

    async def stream(self) -> AsyncGenerator[Dict[str, Union[str, bytes]], None]:
        """
        Stream audio data from the Nanmai TTS service.
        """
        # 1. Pre-check: Content Validity
        if not self.text or not SPEAKABLE_PATTERN.search(self.text):
            raise NoAudioReceived("Text contains no speakable characters")

        speakable_count = self._get_speakable_count(self.text)

        # 2. Smart Sanitization for short texts
        text_to_send = self.text
        if speakable_count < 3:
            text_to_send = self._smart_sanitize(self.text)
            if not text_to_send.strip():
                text_to_send = self.text  # Fallback if sanitization removed everything

        # 3. Prepare Request
        data = aiohttp.FormData()
        data.add_field("text", text_to_send)
        data.add_field("audio_type", "mp3")
        data.add_field("format", "stream")

        headers = generate_headers()
        url = f"{API_URL}?roleid={self.voice}"

        # Retry configuration
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            # Track if streaming has started to prevent data duplication on retry
            stream_started = False

            try:
                async with self._get_session() as session:
                    async with session.post(
                        url,
                        data=data,
                        headers=headers,
                        proxy=self.proxy
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise NanmaiAPIError(f"Nanmai API Error {response.status}: {error_text}")

                        # True streaming - once we start yielding, don't retry on errors
                        chunk_count = 0
                        async for chunk in response.content.iter_chunked(4096):
                            if chunk:
                                stream_started = True  # Mark that streaming has begun
                                chunk_count += 1
                                yield {"type": "audio", "data": chunk}

                        if chunk_count == 0:
                            raise NoAudioReceived("Empty audio data received from API")

                        return  # Success, exit retry loop

            except (aiohttp.ServerDisconnectedError, aiohttp.ClientPayloadError,
                    aiohttp.ClientConnectionError, asyncio.TimeoutError) as e:
                # Check if streaming already started - if so, don't retry to prevent data duplication
                if stream_started:
                    raise NetworkError("Connection interrupted during streaming") from e

                # Retryable connection errors (only if streaming hasn't started)
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise RetryExhaustedError(f"Connection failed after {max_retries} attempts") from e

            except aiohttp.ClientError as e:
                # Other network errors, don't retry
                raise NetworkError(f"Network error: {e}") from e

            except SessionExpiredError as e:
                # External session expired, don't retry
                raise e

        # Should not reach here
        raise RetryExhaustedError(f"Unexpected error after {max_retries} attempts")

    async def _execute_with_retry(self, operation_coro_factory):
        """
        [新增] 統一的內部重試控制器
        Args:
            operation_coro_factory: 一個函式，每次呼叫會回傳一個全新的 coroutine
        """
        max_retries = 3
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # 執行傳入的操作
                return await operation_coro_factory()

            except (NetworkError, asyncio.TimeoutError) as e:
                last_error = e
                # 如果是最後一次嘗試，就不等待了，直接拋出異常
                if attempt == max_retries:
                    break

                # 記錄日誌 (如果有的話) 或僅作等待
                delay = 2.0 * (attempt + 1)
                await asyncio.sleep(delay)
                continue

        # 重試耗盡
        raise last_error

    async def save(self, audio_fname: str) -> None:
        """
        Save the audio to a file. (具備自動重試能力)

        Args:
            audio_fname: Output filename
        """
        async def _do_save():
            # ⚠️ 關鍵：每次重試都要重新 open file，確保從頭寫入 (覆蓋舊的失敗檔案)
            with open(audio_fname, "wb") as f:
                async for chunk in self.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])  # type: ignore

        # 使用統一重試機制
        await self._execute_with_retry(_do_save)

    async def get_audio_data(self) -> bytes:
        """
        Get complete audio data. (具備自動重試能力)

        Returns:
            Complete audio data as bytes
        """
        async def _do_get():
            chunks = []
            # ⚠️ 關鍵：每次重試 chunks 都是空的 list (確保資料淨空)
            async for chunk in self.stream():
                if chunk["type"] == "audio":
                    chunks.append(chunk["data"])

            if not chunks:
                 raise NoAudioReceived("No audio chunks received")
            return b"".join(chunks)

        # 使用統一重試機制
        return await self._execute_with_retry(_do_get)
