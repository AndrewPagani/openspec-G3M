"""Small, configurable Xano HTTP client.

The UI never contains business fixtures. When Xano is not configured, methods
return a clear configuration error so every screen can show an actionable state.
"""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
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
        self._session: httpx.AsyncClient | None = None
        self._reads: asyncio.Semaphore | None = None
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
                if path.strip("/").lower() == "auth/login":
                    raise XanoError("E-mail ou senha inválidos.")
                raise XanoError("Sua sessão expirou. Entre novamente.")
            if response.status_code == 403:
                raise XanoError("Você não tem permissão para esta operação.")
            if response.status_code >= 400:
                detail = response.text[:240] or "erro sem detalhes"
                raise XanoError(f"Xano recusou a operação ({response.status_code}): {detail}")
            return response.json() if response.content else {}
        except httpx.HTTPError as exc:
            raise XanoError("Não foi possível conectar ao Xano. Verifique a URL e a rede.") from exc

    async def async_request(
        self, method: str, path: str, *, token: str = "", json: Any = None, params: Any = None
    ) -> Any:
        headers = {"Accept": "application/json"}
        if token:
            normalized = token.strip()
            if normalized.lower().startswith("bearer "):
                normalized = normalized[7:].strip()
            headers["Authorization"] = "Bearer " + normalized
        try:
            if self._session is None:
                raise XanoError("Transporte Xano indisponível. Reinicie o servidor.")
            async def send():
                return await self._session.request(
                    method, self._url(path), headers=headers, json=json, params=params,
                    timeout=self.timeout,
                )
            if method.upper() in {"GET", "HEAD"}:
                async with self._reads:
                    response = await send()
            else:
                response = await send()
            if response.status_code == 401:
                if path.strip("/").lower() == "auth/login":
                    raise XanoError("E-mail ou senha inválidos.")
                raise XanoError("Sua sessão expirou. Entre novamente.")
            if response.status_code == 403:
                raise XanoError("Você não tem permissão para esta operação.")
            if response.status_code >= 400:
                detail = response.text[:240] or "erro sem detalhes"
                raise XanoError(f"Xano recusou a operação ({response.status_code}): {detail}")
            result = response.json() if response.content else {}
            if method.upper() not in {"GET", "HEAD"}:
                from app.services.catalogs import CATALOGS, catalogs
                if "/" + path.strip("/").split("/", 1)[0] in CATALOGS:
                    catalogs.invalidate()
            return result
        except httpx.HTTPError as exc:
            raise XanoError("Não foi possível conectar ao Xano. Verifique a URL e a rede.") from exc

    async def start(self) -> None:
        if self._session is None:
            self._session = httpx.AsyncClient(timeout=self.timeout)
            self._reads = asyncio.Semaphore(3)

    async def close(self) -> None:
        session, self._session = self._session, None
        if session is not None:
            await session.aclose()

    @asynccontextmanager
    async def lifespan(self):
        await self.start()
        try:
            yield
        finally:
            await self.close()

    async def async_login(self, email: str, password: str) -> Any:
        return await self.async_request("POST", "/auth/login", json={"email": email, "senha": password})

    def login(self, email: str, password: str) -> Any:
        return self.request("POST", "/auth/login", json={"email": email, "senha": password})


client = XanoClient()
