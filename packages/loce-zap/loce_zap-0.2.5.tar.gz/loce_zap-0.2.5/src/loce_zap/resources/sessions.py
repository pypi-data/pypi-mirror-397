from __future__ import annotations

from typing import Mapping, cast

from ..http import AsyncHttpClient, SyncHttpClient
from ..types import SessionConnectResponse, SessionDisconnectResponse, SessionListResponse, SessionUpdateResponse


class SessionResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def connect(
        self,
        session_name: str,
        webhook_url: str,
        webhook_messages: bool = True,
        *,
        mode: str = "qr",
        pairing_number: str | None = None
    ) -> SessionConnectResponse:
        body = _build_connect_payload(
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages,
            mode=mode,
            pairing_number=pairing_number
        )
        data = self._http.request("POST", "/v1/session/connect", json=body)
        return cast(SessionConnectResponse, data)

    def disconnect(self, session_id: str) -> SessionDisconnectResponse:
        data = self._http.request("DELETE", f"/v1/session/disconnect/{session_id}")
        return cast(SessionDisconnectResponse, data)

    def list_sessions(self) -> SessionListResponse:
        data = self._http.request("GET", "/v1/session/all")
        return cast(SessionListResponse, data)

    def edit(
        self,
        session_id: str,
        *,
        session_name: str | None = None,
        webhook_url: str | None = None,
        webhook_messages: bool | None = None
    ) -> SessionUpdateResponse:
        body = _build_update_payload(
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages,
        )
        data = self._http.request("PATCH", f"/v1/session/{session_id}", json=body)
        return cast(SessionUpdateResponse, data)


class AsyncSessionResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def connect(
        self,
        session_name: str,
        webhook_url: str,
        webhook_messages: bool = True,
        *,
        mode: str = "qr",
        pairing_number: str | None = None
    ) -> SessionConnectResponse:
        body = _build_connect_payload(
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages,
            mode=mode,
            pairing_number=pairing_number
        )
        data = await self._http.request("POST", "/v1/session/connect", json=body)
        return cast(SessionConnectResponse, data)

    async def disconnect(self, session_id: str) -> SessionDisconnectResponse:
        data = await self._http.request("DELETE", f"/v1/session/disconnect/{session_id}")
        return cast(SessionDisconnectResponse, data)

    async def list_sessions(self) -> SessionListResponse:
        data = await self._http.request("GET", "/v1/session/all")
        return cast(SessionListResponse, data)

    async def edit(
        self,
        session_id: str,
        *,
        session_name: str | None = None,
        webhook_url: str | None = None,
        webhook_messages: bool | None = None
    ) -> SessionUpdateResponse:
        body = _build_update_payload(
            session_name=session_name,
            webhook_url=webhook_url,
            webhook_messages=webhook_messages,
        )
        data = await self._http.request("PATCH", f"/v1/session/{session_id}", json=body)
        return cast(SessionUpdateResponse, data)


def _build_connect_payload(
    *,
    session_name: str,
    webhook_url: str,
    webhook_messages: bool,
    mode: str,
    pairing_number: str | None,
) -> Mapping[str, object]:
    if not webhook_url or not isinstance(webhook_url, str):
        raise ValueError("webhookUrl is required when connecting a session")

    resolved_name = session_name.strip() if isinstance(session_name, str) else ""
    if not resolved_name:
        resolved_name = "Loce Zap Session"

    resolved_mode = (mode or "").lower() if isinstance(mode, str) else ""
    if resolved_mode not in {"qr", "pairing"}:
        raise ValueError("mode must be either 'qr' or 'pairing'")

    sanitized_pairing = None
    if pairing_number is not None:
        digits_only = "".join(ch for ch in str(pairing_number) if ch.isdigit())
        if not digits_only:
            raise ValueError("pairing_number must contain digits")
        sanitized_pairing = digits_only

    if resolved_mode == "pairing":
        if not sanitized_pairing:
            raise ValueError("pairing_number is required when mode='pairing'")
        if len(sanitized_pairing) < 11 or len(sanitized_pairing) > 13:
            raise ValueError("pairing_number must have between 11 and 13 digits (include DDI)")
    elif sanitized_pairing:
        raise ValueError("pairing_number is only accepted when mode='pairing'")

    payload = {
        "sessionName": resolved_name,
        "webhookUrl": webhook_url,
        "webhookMessages": webhook_messages,
        "mode": resolved_mode,
    }

    if sanitized_pairing:
        payload["pairingNumber"] = sanitized_pairing

    return payload


def _build_update_payload(
    *,
    session_name: str | None,
    webhook_url: str | None,
    webhook_messages: bool | None,
) -> Mapping[str, object]:
    payload: dict[str, object] = {}

    if session_name is not None:
        if not isinstance(session_name, str):
            raise ValueError("session_name must be a string when provided")
        trimmed_name = session_name.strip()
        if not trimmed_name:
            raise ValueError("session_name cannot be empty when provided")
        payload["sessionName"] = trimmed_name

    if webhook_url is not None:
        if not webhook_url or not isinstance(webhook_url, str):
            raise ValueError("webhook_url must be a non-empty string when provided")
        payload["webhookUrl"] = webhook_url

    if webhook_messages is not None:
        payload["webhookMessages"] = webhook_messages

    if not payload:
        raise ValueError("Provide at least one of session_name, webhook_url or webhook_messages")

    return payload
