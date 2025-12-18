# Loce Zap Python SDK

SDK oficial em Python para integrar com a API Loce Zap.

## Instalação

```bash
pip install loce-zap
```

## Uso rápido

```python
from loce_zap import LoceZap

api = LoceZap("SUA_API_KEY")

connect_resp = api.connect(
    session_name="sessao-123",
    webhook_url="https://seu-webhook.com/evento",
    webhook_messages=True,
    mode="qr",  # ou "pairing" com pairing_number
)

edit_resp = api.edit_session(
    "sessao-123",
    session_name="sessao-renomeada",
    webhook_url="https://seu-webhook.com/novo",
    webhook_messages=False,
)

list_resp = api.list_sessions()

disconnect_resp = api.disconnect("sessao-123")

api.close()
```

## Assíncrono

```python
import asyncio
from loce_zap import AsyncLoceZap

async def main() -> None:
    api = AsyncLoceZap("SUA_API_KEY")

    await api.connect(
        session_name="sessao-123",
        webhook_url="https://seu-webhook.com/evento",
        webhook_messages=True,
        mode="qr",  # ou "pairing" com pairing_number
    )

    await api.edit_session(
        "sessao-123",
        session_name="sessao-renomeada",
        webhook_url="https://seu-webhook.com/novo",
        webhook_messages=False,
    )

    await api.list_sessions()
    await api.disconnect("sessao-123")

    await api._http.aclose()

asyncio.run(main())
```

## Envio de mensagens (exemplos)

```python
send_resp = api.send_message_text(
    session_id="sessao-123",
    to="+5511999999999",
    text="Olá!",
)

api.delete_message(
    session_id="sessao-123",
    message_id="msg-123",
)

api.edit_message(
    session_id="sessao-123",
    message_id="msg-123",
    text="Corrigido",
)
```

Outras opções: `send_message_image`, `send_message_audio`, `send_message_document`, `send_message_location`, `send_message_video`, `send_message_sticker`, `send_message_buttons`, `send_message_list`, `delete_message`, `edit_message`.

## Sessões

- `connect(session_name, webhook_url, webhook_messages=True, *, mode="qr", pairing_number=None)` → cria/conecta sessão (use `mode="pairing"` e `pairing_number` de 11–13 dígitos para login por número).
- `edit_session(session_id, *, session_name=None, webhook_url=None, webhook_messages=None)` → atualiza sessão. É obrigatório enviar pelo menos um campo.
- `list_sessions()` → lista sessões.
- `disconnect(session_id)` → desconecta sessão.

Exemplo de login por número (pairing):

```python
api.connect(
    session_name="Meu WhatsApp",
    webhook_url="https://minhaapp.com/webhook",
    webhook_messages=True,
    mode="pairing",
    pairing_number="5511999999999",
)
```

## Validação de webhooks

```python
from loce_zap import WebhookVerifier

verifier = WebhookVerifier()
is_valid = verifier.verify(signature, payload_bytes, api_key="SUA_API_KEY")
```

## Exemplo completo (sync e async com `session_id`)

```python
"""Exemplo rapido de uso da SDK (sync e async) com session_id."""

import asyncio
import os
from typing import Iterable

from LoceZap import AsyncLoceZap, LoceZap

API_KEY = os.getenv("LOCE_ZAP_API_KEY", "SUA_API_KEY")
SESSION_ID = os.getenv("LOCE_ZAP_SESSION_ID", "sessao-123")

def _print_sessions(sessions: Iterable) -> None:
    names = [s.name for s in sessions or []]
    print("Sessoes atuais:", names)

    ids = [s.id for s in sessions or []]
    print("id:", ids)


def simple_homepage_example() -> None:
    api_key = os.getenv("LOCE_ZAP_API_KEY")
    zap = LoceZap(api_key)

    zap.connect(session_name=HOMEPAGE_SESSION_NAME, webhook_url=HOMEPAGE_WEBHOOK_URL)

    zap.send_message_text(session_id=HOMEPAGE_SESSION_ID, to=HOMEPAGE_PHONE, text="Olá 👋")


def run_sync() -> None:
    if not API_KEY:
        raise SystemExit("Defina a variavel de ambiente LOCE_ZAP_API_KEY")
    if not SESSION_ID:
        raise SystemExit("Defina a variavel de ambiente LOCE_ZAP_SESSION_ID com o id da sessao")

    zap = LoceZap(API_KEY)
    # Se precisar criar/atualizar o webhook da sessao, use connect informando o nome.
    # Ex.: zap.connect("Support Session", WEBHOOK_URL, webhook_messages=True)

    _print_sessions(zap.list_sessions().sessions)

    if PHONE:
        resp = zap.send_message_text(SESSION_ID, PHONE, "Hello from Loce Zap Python SDK (sync)")
        print("Texto enviado, id:", resp.messageId or resp.message_id)

        resp_img = zap.send_message_image(SESSION_ID, PHONE, IMAGE_URL, caption="Imagem de exemplo")
        print("Imagem enviada, id:", resp_img.messageId or resp_img.message_id)

        resp_audio = zap.send_message_audio(SESSION_ID, PHONE, AUDIO_URL)
        print("Audio enviado, id:", resp_audio.messageId or resp_audio.message_id)

        resp_video = zap.send_message_video(SESSION_ID, PHONE, VIDEO_URL, caption="Video de exemplo")
        print("Video enviado, id:", resp_video.messageId or resp_video.message_id)

        resp_doc = zap.send_message_document(
            SESSION_ID, PHONE, DOC_URL, file_name=DOC_NAME, caption="Documento exemplo"
        )
        print("Documento enviado, id:", resp_doc.messageId or resp_doc.message_id)

        resp_loc = zap.send_message_location(SESSION_ID, PHONE, latitude=-23.55052, longitude=-46.633308)
        print("Localizacao enviada, id:", resp_loc.messageId or resp_loc.message_id)

        resp_btn = zap.send_message_buttons(
            SESSION_ID,
            PHONE,
            "Escolha uma opcao",
            buttons=[{"id": "op1", "text": "Opcao 1"}, {"id": "op2", "text": "Opcao 2"}],
            footer="Selecione abaixo",
        )
        print("Botoes enviados, id:", resp_btn.messageId or resp_btn.message_id)

        resp_list = zap.send_message_list(
            SESSION_ID,
            PHONE,
            "Escolha uma opcao",
            "Abrir menu",
            sections=[
                {
                    "title": "Menu principal",
                    "rows": [
                        {"title": "Ver pedidos", "rowId": "pedidos"},
                        {"title": "Ver cobrancas", "rowId": "cobrancas"},
                    ],
                }
            ],
            footer="Selecione uma das opcoes",
        )
        print("Lista enviada, id:", resp_list.messageId or resp_list.message_id)

        zap.delete_message(session_id=SESSION_ID, message_id=resp.messageId or resp.message_id or "msg-id")
        zap.edit_message(session_id=SESSION_ID, message_id=resp.messageId or resp.message_id or "msg-id", text="Corrigido")
    else:
        print("LOCE_ZAP_PHONE nao definida; pulando envio.")


async def run_async() -> None:
    if not API_KEY:
        raise SystemExit("Defina a variavel de ambiente LOCE_ZAP_API_KEY")
    if not SESSION_ID:
        raise SystemExit("Defina a variavel de ambiente LOCE_ZAP_SESSION_ID com o id da sessao")

    zap = AsyncLoceZap(API_KEY)
    # Se precisar criar/atualizar o webhook da sessao, use connect informando o nome.
    # Ex.: await zap.connect("Support Session", WEBHOOK_URL, webhook_messages=True)

    sessions = await zap.list_sessions()
    _print_sessions(sessions.sessions)

    if PHONE:
        resp = await zap.send_message_text(SESSION_ID, PHONE, "Hello from Loce Zap Python SDK (async)")
        print("Texto enviado, id:", resp.messageId or resp.message_id)

        resp_img = await zap.send_message_image(SESSION_ID, PHONE, IMAGE_URL, caption="Imagem de exemplo")
        print("Imagem enviada, id:", resp_img.messageId or resp_img.message_id)

        resp_audio = await zap.send_message_audio(SESSION_ID, PHONE, AUDIO_URL)
        print("Audio enviado, id:", resp_audio.messageId or resp_audio.message_id)

        resp_video = await zap.send_message_video(SESSION_ID, PHONE, VIDEO_URL, caption="Video de exemplo")
        print("Video enviado, id:", resp_video.messageId or resp_video.message_id)

        resp_doc = await zap.send_message_document(
            SESSION_ID, PHONE, DOC_URL, file_name=DOC_NAME, caption="Documento exemplo"
        )
        print("Documento enviado, id:", resp_doc.messageId or resp_doc.message_id)

        resp_loc = await zap.send_message_location(SESSION_ID, PHONE, latitude=-23.55052, longitude=-46.633308)
        print("Localizacao enviada, id:", resp_loc.messageId or resp_loc.message_id)

        resp_btn = await zap.send_message_buttons(
            SESSION_ID,
            PHONE,
            "Escolha uma opcao (async)",
            buttons=[{"id": "op1", "text": "Opcao 1"}, {"id": "op2", "text": "Opcao 2"}],
            footer="Selecione abaixo",
        )
        print("Botoes enviados, id:", resp_btn.messageId or resp_btn.message_id)

        resp_list = await zap.send_message_list(
            SESSION_ID,
            PHONE,
            "Escolha uma opcao (async)",
            "Abrir menu",
            sections=[
                {
                    "title": "Menu principal",
                    "rows": [
                        {"title": "Ver pedidos", "rowId": "pedidos"},
                        {"title": "Ver cobrancas", "rowId": "cobrancas"},
                    ],
                }
            ],
            footer="Selecione uma das opcoes",
        )
        print("Lista enviada, id:", resp_list.messageId or resp_list.message_id)

        await zap.delete_message(session_id=SESSION_ID, message_id=resp.messageId or resp.message_id or "msg-id")
        await zap.edit_message(session_id=SESSION_ID, message_id=resp.messageId or resp.message_id or "msg-id", text="Corrigido")
    else:
        print("LOCE_ZAP_PHONE nao definida; pulando envio.")

    await zap.close()


if __name__ == "__main__":
    simple_homepage_example()
    # run_sync()
    # asyncio.run(run_async())
```

## Licença

MIT
