from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Mapping, Optional, Union

from .exceptions import WebhookSignatureError

from .response import APIResponse, wrap_response_payload

RawBody = Union[str, bytes, bytearray, Mapping[str, Any]]
Headers = Mapping[str, Any]

EVENT_TYPES = {
    "SESSION-CONNECTED",
    "SESSION-DISCONNECTED",
    "MESSAGE-RECEIVED",
    "MESSAGE-SENT",
    "MESSAGE-DELIVERED",
    "MESSAGE-READ",
    "MESSAGE-DISCARDED",
}


def _ensure_str(body: RawBody) -> str:
    if isinstance(body, (bytes, bytearray)):
        return body.decode("utf-8")
    if isinstance(body, str):
        return body
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False)


class WebhookVerifier:
    """Valida a assinatura enviada pelo Loce Zap."""

    @staticmethod
    def verify_signature(
        signature_header: str,
        *,
        body: RawBody,
        secret: str,
        tolerance: int = 5 * 60,
    ) -> bool:
        if not signature_header:
            raise WebhookSignatureError("Missing x-locezap-signature header")
        if not secret:
            raise WebhookSignatureError("Secret is required to validate webhook payloads")

        parts = {}
        for chunk in signature_header.split(","):
            if "=" in chunk:
                key, value = chunk.split("=", 1)
                parts[key.strip()] = value.strip()

        timestamp = parts.get("t")
        provided_signature = parts.get("v1")

        if not timestamp or not provided_signature:
            raise WebhookSignatureError("Assinatura mal formatada")

        now = int(time.time())
        try:
            ts = int(timestamp)
        except ValueError as exc:
            raise WebhookSignatureError("Invalid webhook timestamp") from exc

        if tolerance > 0 and abs(now - ts) > tolerance:
            raise WebhookSignatureError("Timestamp fora da janela permitida")

        raw_body = _ensure_str(body)
        data = f"{ts}.{raw_body}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), data, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, provided_signature):
            raise WebhookSignatureError("Invalid webhook signature")

        return True

    @staticmethod
    def verify_request(
        headers: Headers,
        *,
        raw_body: RawBody,
        secret: str,
        tolerance: int = 5 * 60,
    ) -> bool:
        """
        Extrai o cabeçalho x-locezap-signature e valida contra o corpo recebido.
        Compatível com o exemplo Express/Next: zap.webhooks.verifySignature({ headers, rawBody }).
        """
        signature_header = _find_signature_header(headers)
        return WebhookVerifier.verify_signature(
            signature_header,
            body=raw_body,
            secret=secret,
            tolerance=tolerance,
        )

    @staticmethod
    def parse_event(raw_body: RawBody) -> APIResponse:
        """
        Converte o webhook bruto em um objeto (dict-like) com type/payload/etc.
        Não força o tipo do evento, mas deixa EVENT_TYPES disponível para validação externa.
        """
        raw_str = _ensure_str(raw_body)
        try:
            payload = json.loads(raw_str)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid webhook body: expected JSON") from exc
        return wrap_response_payload(payload)

    @staticmethod
    def sign_payload(raw_body: RawBody, *, secret: str, timestamp: Optional[int] = None) -> str:
        """
        Gera uma assinatura válida (útil para testes locais).
        Retorna no formato t=<timestamp>,v1=<signature>.
        """
        if not secret:
            raise WebhookSignatureError("Secret is required to sign webhook payloads")
        ts = int(timestamp or time.time())
        raw = _ensure_str(raw_body)
        data = f"{ts}.{raw}".encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), data, hashlib.sha256).hexdigest()
        return f"t={ts},v1={signature}"


def _find_signature_header(headers: Headers) -> str:
    for key, value in (headers or {}).items():
        if isinstance(key, str) and key.lower() == "x-locezap-signature":
            return str(value)
    return ""
