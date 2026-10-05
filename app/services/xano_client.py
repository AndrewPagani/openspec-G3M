"""Small, configurable Xano HTTP client.

The UI never contains business fixtures. When Xano is not configured, methods
return a clear configuration error so every screen can show an actionable state.
"""
from __future__ import annotations

import os
from typing import Any

import httpx


DEFAULT_XANO_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io"


class XanoError(RuntimeError):
    """An expected API/configuration failure safe to show to an operator."""


class XanoClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("XANO_BASE_URL", DEFAULT_XANO_BASE_URL).rstrip("/")
        self.api_groups = {
            "auth": os.getenv("XANO_API_GROUP_AUTH", "autenticacao"),
            "cadastros": os.getenv("XANO_API_GROUP_CADASTROS", "cadastros"),
            "vendas": os.getenv("XANO_API_GROUP_VENDAS", "Q9GErvvS"),
            "gerenciamento": os.getenv("XANO_API_GROUP_GERENCIAMENTO", "gerenciamento"),
        }
        self.timeout = float(os.getenv("XANO_TIMEOUT", "12"))

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    def _url(self, path: str) -> str:
        if not self.configured:
            raise XanoError(
                "Xano não configurado. Defina XANO_BASE_URL para carregar dados reais."
            )
        route = path.strip("/")
        if (
            route.startswith("webhooks/")
            or route.endswith("/link-pagamento")
            or route.endswith("/pagamento/atualizar")
            or route.endswith("/pagamento/notificar")
        ):
            raise XanoError(
                "Rotas de gateway e cobrança externa foram desativadas neste app."
            )
        if route.startswith("auth/"):
            group_key = "auth"
        elif route.startswith(("clientes", "veiculos", "pecas", "perfis", "status-", "formas-", "veiculo-areas")):
            group_key = "cadastros"
        elif route.startswith("vendas"):
            group_key = "vendas"
        elif route.startswith(("gerenciamento", "usuarios")):
            group_key = "gerenciamento"
            if route.startswith("gerenciamento/"):
                route = route.removeprefix("gerenciamento/")
        else:
            raise XanoError(f"Rota Xano sem grupo configurado: {route}")

        base = self.base_url
        if "/api:" in base:
            base = base.split("/api:", 1)[0].rstrip("/")
        group = self.api_groups[group_key].strip("/")
        parts = [base, f"api:{group}", route]
        return "/".join(parts)

    def request(
        self, method: str, path: str, *, token: str = "", json: Any = None, params: Any = None
    ) -> Any:
        headers = {"Accept": "application/json"}
        if token:
            # Xano returns the raw token, but some deployments return the
            # complete scheme-prefixed value. Never send "Bearer Bearer ...".
            normalized = token.strip()
            if normalized.lower().startswith("bearer "):
                normalized = normalized[7:].strip()
            headers["Authorization"] = f"Bearer {normalized}"
        if token:
            headers["Authorization"] = "Bearer " + normalized
        try:
            response = httpx.request(
                method, self._url(path), headers=headers, json=json, params=params, timeout=self.timeout
            )
            if response.status_code == 401:
                raise XanoError("Sua sessão expirou. Entre novamente.")
            if response.status_code == 403:
                raise XanoError("Você não tem permissão para esta operação.")
            if response.status_code >= 400:
                detail = response.text[:240] or "erro sem detalhes"
                raise XanoError(f"Xano recusou a operação ({response.status_code}): {detail}")
            return response.json() if response.content else {}
        except httpx.HTTPError as exc:
            raise XanoError("Não foi possível conectar ao Xano. Verifique a URL e a rede.") from exc

    def login(self, email: str, password: str) -> Any:
        return self.request("POST", "/auth/login", json={"email": email, "senha": password})


client = XanoClient()
