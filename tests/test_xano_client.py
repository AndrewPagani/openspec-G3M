import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.services.xano_client import XanoClient, XanoError


class XanoClientTests(unittest.TestCase):
    def setUp(self) -> None:
        with patch.dict(os.environ, {"XANO_BASE_URL": "https://example.xano.io"}):
            self.client = XanoClient()

    def test_routes_use_their_configured_api_group(self) -> None:
        self.assertEqual(
            self.client._url("/auth/login"),
            "https://example.xano.io/api:autenticacao/auth/login",
        )
        self.assertEqual(
            self.client._url("/clientes"),
            "https://example.xano.io/api:cadastros/clientes",
        )
        self.assertEqual(
            self.client._url("/vendas/12/parcelas/7/receber"),
            "https://example.xano.io/api:Q9GErvvS/vendas/12/parcelas/7/receber",
        )
        self.assertEqual(
            self.client._url("/gerenciamento/indicadores"),
            "https://example.xano.io/api:gerenciamento/indicadores",
        )

    @patch("app.services.xano_client.httpx.request")
    def test_authenticated_request_sends_bearer_token(self, request) -> None:
        request.return_value = httpx.Response(200, json={"ok": True})

        result = self.client.request("GET", "/clientes", token="test-token")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            request.call_args.kwargs["headers"]["Authorization"],
            "Bearer test-token",
        )

    @patch("app.services.xano_client.httpx.request")
    def test_login_unauthorized_reports_invalid_credentials(self, request) -> None:
        request.return_value = httpx.Response(401, json={"message": "unauthorized"})

        with self.assertRaisesRegex(XanoError, "E-mail ou senha inválidos"):
            self.client.login("user@example.com", "wrong-password")

    @patch("app.services.xano_client.httpx.request")
    def test_authenticated_unauthorized_request_reports_expired_session(self, request) -> None:
        request.return_value = httpx.Response(401, json={"message": "unauthorized"})

        with self.assertRaisesRegex(XanoError, "Sua sessão expirou"):
            self.client.request("GET", "/clientes", token="test-token")

    def test_rejects_webhook_route_from_application_client(self) -> None:
        with self.assertRaises(XanoError):
            self.client._url("/webhooks/asaas/pagamentos")

    def test_rejects_legacy_external_payment_routes(self) -> None:
        for route in (
            "/vendas/12/pagamento/atualizar",
            "/vendas/12/pagamento/notificar",
        ):
            with self.subTest(route=route), self.assertRaises(XanoError):
                self.client._url(route)

    def test_routes_hosted_payment_link_to_sales_group(self) -> None:
        self.assertEqual(
            self.client._url("/vendas/12/link-pagamento"),
            "https://example.xano.io/api:Q9GErvvS/vendas/12/link-pagamento",
        )


class AsyncXanoClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        with patch.dict(os.environ, {"XANO_BASE_URL": "https://example.xano.io"}):
            self.client = XanoClient()

    @patch("app.services.xano_client.httpx.AsyncClient")
    async def test_async_request_uses_authorization_and_query_params(self, async_client) -> None:
        response = httpx.Response(200, json={"kpis": {}})
        session = MagicMock()
        session.request = AsyncMock(return_value=response)
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=session)
        context.__aexit__ = AsyncMock(return_value=False)
        async_client.return_value = session
        session.aclose = AsyncMock()
        await self.client.start()

        result = await self.client.async_request(
            "GET",
            "/gerenciamento/indicadores",
            token="test-token",
            params={"data_inicio": "2026-10-01"},
        )

        self.assertEqual(result, {"kpis": {}})
        args, kwargs = session.request.await_args
        self.assertEqual(args[:2], ("GET", "https://example.xano.io/api:gerenciamento/indicadores"))
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-token")
        self.assertEqual(kwargs["params"], {"data_inicio": "2026-10-01"})

    @patch("app.services.xano_client.httpx.AsyncClient")
    async def test_async_unauthorized_request_reports_expired_session(self, async_client) -> None:
        session = MagicMock()
        session.request = AsyncMock(
            return_value=httpx.Response(401, json={"message": "unauthorized"})
        )
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=session)
        context.__aexit__ = AsyncMock(return_value=False)
        async_client.return_value = session
        session.aclose = AsyncMock()
        await self.client.start()

        with self.assertRaisesRegex(XanoError, "Sua sessão expirou"):
            await self.client.async_request("GET", "/clientes", token="test-token")


if __name__ == "__main__":
    unittest.main()
