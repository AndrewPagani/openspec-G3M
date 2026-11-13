from __future__ import annotations

from typing import Any

import reflex as rx

from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState


def _client_value(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return "Não informado"


class ClientDetailState(rx.State):
    client: dict[str, str] = {}
    loading: bool = False
    error: str = ""

    async def load(self) -> None:
        client_id = str(self.router.page.params.get("id", "")).strip()
        if not client_id.isdigit() or int(client_id) < 1:
            self.error = "Identificador de cliente inválido."
            return
        self.loading, self.error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            response = client.request(
                "GET",
                f"/clientes/{client_id}",
                token=auth_state.token,
            )
            if not isinstance(response, dict) or response.get("id") is None:
                raise XanoError("A API retornou dados de cliente em formato inválido.")
            self.client = {
                "id": str(response["id"]),
                "name": _client_value(response, "CNome", "Nome", "nome"),
                "cpf": _client_value(response, "CPF", "cpf"),
                "phone": _client_value(response, "Telefone", "telefone"),
                "email": _client_value(response, "Email", "email"),
                "created_at": _client_value(response, "created_at", "Created_at"),
            }
        except XanoError as exc:
            self.client = {}
            self.error = str(exc)
        finally:
            self.loading = False
