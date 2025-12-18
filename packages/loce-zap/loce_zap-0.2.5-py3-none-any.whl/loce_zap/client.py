from __future__ import annotations

from typing import Optional

from .http import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncHttpClient,
    SyncHttpClient,
    TransportConfig,
)
from .resources import AsyncMessageResource, AsyncSessionResource, MessageResource, SessionResource
from .types import (
    DeleteOrEditMessageResponse,
    SendMessageResponse,
    SessionConnectResponse,
    SessionDisconnectResponse,
    SessionListResponse,
    SessionUpdateResponse,
)
from .webhooks import WebhookVerifier


class LoceZap:
    """Synchronous client exposing snake_case helpers (connect, send_message_text, ...)."""

    def __init__(self, api_key: str) -> None:
        if not api_key or not isinstance(api_key, str):
            raise ValueError("api_key is required")

        config = TransportConfig()
        self._http = SyncHttpClient(api_key, config=config)
        self._sessions = SessionResource(self._http)
        self._messages = MessageResource(self._http)
        self.sessions = self._sessions
        self.messages = self._messages
        self.webhooks = WebhookVerifier()

    def connect(
        self,
        session_name: str,
        webhook_url: str,
        webhook_messages: bool = True,
        *,
        mode: str = "qr",
        pairing_number: Optional[str] = None
    ) -> SessionConnectResponse:
        return self._sessions.connect(
            session_name,
            webhook_url,
            webhook_messages,
            mode=mode,
            pairing_number=pairing_number
        )

    def disconnect(self, session_id: str) -> SessionDisconnectResponse:
        return self._sessions.disconnect(session_id)

    def edit_session(
        self,
        session_id: str,
        *,
        session_name: Optional[str] = None,
        webhook_url: Optional[str] = None,
        webhook_messages: Optional[bool] = None,
    ) -> SessionUpdateResponse:
        return self._sessions.edit(
            session_id,
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages,
        )

    def list_sessions(self) -> SessionListResponse:
        return self._sessions.list_sessions()

    def send_message_text(
        self,
        session_id: str,
        to: str,
        text: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_text(session_id, to, text, external_id=external_id, quote_id=quote_id)

    def send_message_image(
        self,
        session_id: str,
        to: str,
        image_url: str,
        *,
        caption: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_image(session_id, to, image_url, caption=caption, external_id=external_id, quote_id=quote_id)

    def send_message_audio(
        self,
        session_id: str,
        to: str,
        audio_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_audio(session_id, to, audio_url, external_id=external_id, quote_id=quote_id)

    def send_message_document(
        self,
        session_id: str,
        to: str,
        file_url: str,
        *,
        file_name: Optional[str] = None,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_document(
            session_id,
            to,
            file_url,
            file_name=file_name,
            caption=caption,
            mimetype=mimetype,
            external_id=external_id,
            quote_id=quote_id,
        )

    def send_message_location(
        self,
        session_id: str,
        to: str,
        *,
        latitude: float,
        longitude: float,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_location(
            session_id,
            to,
            latitude=latitude,
            longitude=longitude,
            external_id=external_id,
            quote_id=quote_id,
        )

    def send_message_video(
        self,
        session_id: str,
        to: str,
        video_url: str,
        *,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        gif_playback: Optional[bool] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_video(
            session_id,
            to,
            video_url,
            caption=caption,
            mimetype=mimetype,
            gif_playback=gif_playback,
            external_id=external_id,
            quote_id=quote_id,
        )

    def send_message_sticker(
        self,
        session_id: str,
        to: str,
        sticker_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_sticker(session_id, to, sticker_url, external_id=external_id, quote_id=quote_id)

    def send_message_buttons(
        self,
        session_id: str,
        to: str,
        message: str,
        buttons: list[dict[str, str]],
        *,
        footer: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_buttons(
            session_id,
            to,
            message,
            buttons,
            footer=footer,
            external_id=external_id,
            quote_id=quote_id,
        )

    def send_message_list(
        self,
        session_id: str,
        to: str,
        text: str,
        button_text: str,
        sections: list[dict],
        *,
        title: Optional[str] = None,
        footer: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return self._messages.send_message_list(
            session_id,
            to,
            text,
            button_text,
            sections,
            title=title,
            footer=footer,
            external_id=external_id,
            quote_id=quote_id,
        )

    def delete_message(self, session_id: str, message_id: str) -> DeleteOrEditMessageResponse:
        return self._messages.delete_message(session_id, message_id)

    def edit_message(self, session_id: str, message_id: str, text: str) -> DeleteOrEditMessageResponse:
        return self._messages.edit_message(session_id, message_id, text)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "LoceZap":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


class AsyncLoceZap:
    """Async variant exposing the same snake_case helpers."""

    def __init__(self, api_key: str) -> None:
        if not api_key or not isinstance(api_key, str):
            raise ValueError("api_key is required")

        config = TransportConfig()
        self._http = AsyncHttpClient(api_key, config=config)
        self._sessions = AsyncSessionResource(self._http)
        self._messages = AsyncMessageResource(self._http)
        self.sessions = self._sessions
        self.messages = self._messages
        self.webhooks = WebhookVerifier()

    async def connect(
        self,
        session_name: str,
        webhook_url: str,
        webhook_messages: bool = True,
        *,
        mode: str = "qr",
        pairing_number: Optional[str] = None
    ) -> SessionConnectResponse:
        return await self._sessions.connect(
            session_name,
            webhook_url,
            webhook_messages,
            mode=mode,
            pairing_number=pairing_number
        )

    async def disconnect(self, session_id: str) -> SessionDisconnectResponse:
        return await self._sessions.disconnect(session_id)

    async def edit_session(
        self,
        session_id: str,
        *,
        session_name: Optional[str] = None,
        webhook_url: Optional[str] = None,
        webhook_messages: Optional[bool] = None,
    ) -> SessionUpdateResponse:
        return await self._sessions.edit(
            session_id,
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages,
        )

    async def list_sessions(self) -> SessionListResponse:
        return await self._sessions.list_sessions()

    async def send_message_text(
        self,
        session_id: str,
        to: str,
        text: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_text(session_id, to, text, external_id=external_id, quote_id=quote_id)

    async def send_message_image(
        self,
        session_id: str,
        to: str,
        image_url: str,
        *,
        caption: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_image(session_id, to, image_url, caption=caption, external_id=external_id, quote_id=quote_id)

    async def send_message_audio(
        self,
        session_id: str,
        to: str,
        audio_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_audio(session_id, to, audio_url, external_id=external_id, quote_id=quote_id)

    async def send_message_document(
        self,
        session_id: str,
        to: str,
        file_url: str,
        *,
        file_name: Optional[str] = None,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_document(
            session_id,
            to,
            file_url,
            file_name=file_name,
            caption=caption,
            mimetype=mimetype,
            external_id=external_id,
            quote_id=quote_id,
        )

    async def send_message_location(
        self,
        session_id: str,
        to: str,
        *,
        latitude: float,
        longitude: float,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_location(
            session_id,
            to,
            latitude=latitude,
            longitude=longitude,
            external_id=external_id,
            quote_id=quote_id,
        )

    async def send_message_video(
        self,
        session_id: str,
        to: str,
        video_url: str,
        *,
        caption: Optional[str] = None,
        mimetype: Optional[str] = None,
        gif_playback: Optional[bool] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_video(
            session_id,
            to,
            video_url,
            caption=caption,
            mimetype=mimetype,
            gif_playback=gif_playback,
            external_id=external_id,
            quote_id=quote_id,
        )

    async def send_message_sticker(
        self,
        session_id: str,
        to: str,
        sticker_url: str,
        *,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_sticker(session_id, to, sticker_url, external_id=external_id, quote_id=quote_id)

    async def send_message_buttons(
        self,
        session_id: str,
        to: str,
        message: str,
        buttons: list[dict[str, str]],
        *,
        footer: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_buttons(
            session_id,
            to,
            message,
            buttons,
            footer=footer,
            external_id=external_id,
            quote_id=quote_id,
        )

    async def send_message_list(
        self,
        session_id: str,
        to: str,
        text: str,
        button_text: str,
        sections: list[dict],
        *,
        title: Optional[str] = None,
        footer: Optional[str] = None,
        external_id: Optional[str] = None,
        quote_id: Optional[str] = None,
    ) -> SendMessageResponse:
        return await self._messages.send_message_list(
            session_id,
            to,
            text,
            button_text,
            sections,
            title=title,
            footer=footer,
            external_id=external_id,
            quote_id=quote_id,
        )

    async def delete_message(self, session_id: str, message_id: str) -> DeleteOrEditMessageResponse:
        return await self._messages.delete_message(session_id, message_id)

    async def edit_message(self, session_id: str, message_id: str, text: str) -> DeleteOrEditMessageResponse:
        return await self._messages.edit_message(session_id, message_id, text)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> "AsyncLoceZap":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()
