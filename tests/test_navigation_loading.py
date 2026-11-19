"""Controlled I/O: lifecycle, isolation, cache and progressive loading contracts."""

import asyncio
import unittest
from types import SimpleNamespace
from typing import ClassVar
from unittest.mock import AsyncMock, patch

import httpx

from app.services.catalogs import CatalogCache, catalogs
from app.services.xano_client import XanoClient, XanoError, client
from app.state.auth_state import AuthState, clear_operational_state
from app.state.read_lifecycle import NavigationState
from app.state.resource_state import ClientsState, PartsState, UsersState, VehiclesState
from app.state.vendas_state import SaleDetailState, VendasState


class TransportLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_pool_reuses_connection_owner_headers_and_close(self):
        api = XanoClient()
        calls = []

        async def respond(request):
            calls.append(request)
            return httpx.Response(200, json={"ok": True})

        session = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        with patch(
            "app.services.xano_client.httpx.AsyncClient", return_value=session
        ) as factory:
            async with api.lifespan():
                await api.start()
                await asyncio.gather(
                    api.async_request(
                        "GET", "/clientes", token="Bearer a", params={"page": 1}
                    ),
                    api.async_request(
                        "GET", "/vendas", token="b", params={"page": "1", "busca": ""}
                    ),
                )
                self.assertFalse(session.is_closed)
            await api.close()
        self.assertTrue(session.is_closed)
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(
            [r.headers["authorization"] for r in calls], ["Bearer a", "Bearer b"]
        )
        self.assertIn("page=1", str(calls[0].url))
        self.assertNotIn("authorization", session.headers)

    async def test_read_limit_cancellation_failure_and_write_not_retried(self):
        api = XanoClient()
        active = maximum = writes = 0
        gate = asyncio.Event()

        async def respond(request):
            nonlocal active, maximum, writes
            if request.method == "POST":
                writes += 1
                raise httpx.ReadTimeout("uncertain")
            active += 1
            maximum = max(maximum, active)
            try:
                await gate.wait()
                return httpx.Response(200, json=[])
            finally:
                active -= 1

        api._session = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        api._reads = asyncio.Semaphore(3)
        tasks = [
            asyncio.create_task(api.async_request("GET", "/clientes")) for _ in range(6)
        ]
        await asyncio.sleep(0.01)
        self.assertEqual(maximum, 3)
        tasks[0].cancel()
        await asyncio.sleep(0.01)
        gate.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        with self.assertRaises(XanoError):
            await api.async_request("POST", "/vendas", json={"cliente_id": 1})
        self.assertEqual(writes, 1)
        self.assertEqual(api._reads._value, 3)
        await api.close()


class CatalogTests(unittest.IsolatedAsyncioTestCase):
    async def test_forced_refresh_wins_over_older_pending_response(self):
        cache = CatalogCache()
        gate = asyncio.Event()
        count = 0

        async def respond(*args, **kwargs):
            nonlocal count
            count += 1
            if count == 1:
                await gate.wait()
                return [{"id": 1, "Metodo": "Antigo"}]
            return {"items": [{"Id": 1, "metodo": "Atual"}]}

        with patch.object(client, "async_request", AsyncMock(side_effect=respond)):
            old = asyncio.create_task(cache.get("/formas-pagamento", "a"))
            await asyncio.sleep(.01)
            fresh = await cache.get("/formas-pagamento", "a", force=True)
            gate.set()
            await old
            self.assertEqual(await cache.get("/formas-pagamento", "a"), fresh)

    async def test_shutdown_cancels_invalidated_producers(self):
        cache = CatalogCache()

        async def respond(*args, **kwargs):
            await asyncio.Event().wait()

        with patch.object(client, "async_request", AsyncMock(side_effect=respond)):
            consumer = asyncio.create_task(cache.get("/veiculo-areas", "a"))
            await asyncio.sleep(.01)
            cache.invalidate()
            await cache.close()
            await asyncio.gather(consumer, return_exceptions=True)
        self.assertEqual(len(cache.tasks), 0)

    async def test_ttl_non_sliding_copies_credentials_environment_and_force(self):
        now = [0]
        cache = CatalogCache(lambda: now[0])
        with patch.object(
            client,
            "async_request",
            AsyncMock(return_value=[{"id": 1, "Metodo": "Pix"}]),
        ) as request:
            first = await cache.get("/formas-pagamento", "a")
            first[0]["Metodo"] = "changed"
            now[0] = 299
            self.assertEqual(
                (await cache.get("/formas-pagamento", "a"))[0]["Metodo"], "Pix"
            )
            self.assertEqual(request.await_count, 1)
            now[0] = 300
            await cache.get("/formas-pagamento", "a")
            await cache.get("/formas-pagamento", "b")
            with patch.object(client, "base_url", "https://other.example"):
                await cache.get("/formas-pagamento", "a")
            await cache.get("/formas-pagamento", "a", force=True)
            self.assertEqual(request.await_count, 5)
        with self.assertRaises(ValueError):
            await cache.get("/veiculos", "a")

    async def test_shared_flight_consumer_cancel_and_invalidation(self):
        cache = CatalogCache()
        gate = asyncio.Event()

        async def response(*args, **kwargs):
            await gate.wait()
            return [{"id": 1, "Secao": "Motor"}]

        with patch.object(
            client, "async_request", AsyncMock(side_effect=response)
        ) as request:
            first = asyncio.create_task(cache.get("/veiculo-areas", "a"))
            second = asyncio.create_task(cache.get("/veiculo-areas", "a"))
            await asyncio.sleep(0.01)
            first.cancel()
            await asyncio.gather(first, return_exceptions=True)
            cache.invalidate()
            gate.set()
            self.assertEqual((await second)[0]["Secao"], "Motor")
            self.assertEqual(request.await_count, 1)
            self.assertEqual(len(cache.entries), 0)
            await cache.get("/veiculo-areas", "a")
            self.assertEqual(request.await_count, 2)

    async def test_cap_and_failed_or_invalid_response_not_cached(self):
        cache = CatalogCache()
        with patch.object(
            client,
            "async_request",
            AsyncMock(return_value=[{"id": 1, "Descricao": "Disponível"}]),
        ):
            for index in range(130):
                await cache.get("/status-veiculos", str(index))
        self.assertEqual(len(cache.entries), 128)
        for response in (XanoError("offline"), {"items": "invalid"}, [{"id": 1}]):
            with (
                patch.object(
                    client,
                    "async_request",
                    AsyncMock(
                        side_effect=response
                        if isinstance(response, Exception)
                        else None,
                        return_value=response,
                    ),
                ),
                self.assertRaises(XanoError),
            ):
                await cache.get("/formas-pagamento", "invalid")
        self.assertEqual(len(cache.entries), 128)


class ReadLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        catalogs.invalidate()

    async def test_namespace_ownership_and_sale_draft_isolation(self):
        states = [
            cls(_reflex_internal_init=True)
            for cls in (ClientsState, VehiclesState, PartsState, UsersState)
        ]
        states[0].records = [{"id": 9}]
        states[0].query, states[0].error = "Ana", "client error"
        for state in states[1:]:
            self.assertEqual(state.records, [])
            self.assertEqual(state.query, "")
            self.assertEqual(state.error, "")
        sale = VendasState(_reflex_internal_init=True)
        detail = SaleDetailState(_reflex_internal_init=True)
        sale.venda_id = "42"
        detail.venda_id = "77"
        self.assertEqual(sale.venda_id, "42")

    async def test_editing_sales_filters_releases_old_loading_without_a_post(self):
        state = VendasState(_reflex_internal_init=True)
        state.list_loading = True
        state.vendas = [{"id": "old"}]
        VendasState.set_busca.fn(state, "new")
        self.assertFalse(state.list_loading)
        self.assertTrue(state.list_needs_refresh)
        self.assertEqual(state.vendas, [])
        self.assertEqual(state.read_generation, 1)

    async def test_dashboard_query_change_preserves_options_and_clears_old_metrics(self):
        from app.state.dashboard_state import DashboardState
        state = DashboardState(_reflex_internal_init=True)
        state.loading, state.total_vendas = True, "99"
        state.forma_pagamento_opcoes = [{"id": "1", "nome": "Pix"}]
        DashboardState.set_data_inicio.fn(state, "2026-10-01")
        self.assertFalse(state.loading)
        self.assertTrue(state.needs_refresh)
        self.assertEqual(state.total_vendas, "—")
        self.assertEqual(state.forma_pagamento_opcoes, [{"id": "1", "nome": "Pix"}])

    async def test_payment_detail_snapshot_keeps_static_helpers_unbound(self):
        from app.state.read_lifecycle import ReadSnapshot
        state = SaleDetailState(_reflex_internal_init=True)
        snapshot = ReadSnapshot(**{name: getattr(state, name) for name in state.base_vars})
        snapshot._state_class = SaleDetailState
        snapshot._auth = SimpleNamespace(token="fixture")
        snapshot.router = SimpleNamespace(page=SimpleNamespace(params={"id": "77"}))
        with patch.object(client, "async_request", AsyncMock(return_value={
            "payment_flow": "ASAAS", "total_venda": 150,
            "invoice_url": "https://sandbox.asaas.com/i/fixture", "status": "PENDING",
        })):
            await snapshot.load_sale()
        self.assertEqual(snapshot.venda_id, "77")
        self.assertEqual(snapshot.detail_error, "")
        self.assertFalse(snapshot.detail_loading)


    async def test_progressive_clients_before_aux_and_no_partial_sales_total(self):
        state = SimpleNamespace(
            get_state=AsyncMock(return_value=SimpleNamespace(token="a"))
        )
        rows = {"items": [{"id": 1, "CNome": "Ana"}], "pagination": {"total_pages": 2}}
        sales = {
            "items": [{"cliente_id": 1, "status_venda": "Pendente"}],
            "pagination": {"total_pages": 2},
        }
        with patch.object(
            client,
            "async_request",
            AsyncMock(
                side_effect=[
                    rows,
                    {"items": [{"id": 2, "CNome": "Bia"}]},
                    sales,
                    XanoError("offline"),
                ]
            ),
        ):
            stream = ClientsState.load.fn.read_body(state, "/clientes", "Clientes")
            await anext(stream)  # Initial feedback, before I/O.
            self.assertTrue(state.loading)
            self.assertEqual(state.records, [])
            await anext(stream)
            self.assertEqual(len(state.records), 1)
            self.assertFalse(state.complete)
            await anext(stream)
            self.assertEqual(len(state.records), 2)
            self.assertTrue(state.complete)
            self.assertTrue(state.activity_pending)
            self.assertFalse(state.client_sales_available)
            async for _ in stream:
                pass
            self.assertFalse(state.activity_pending)
            self.assertFalse(state.client_sales_available)
            self.assertEqual(state.pending_purchases, 0)
            self.assertIn("vendas", state.client_sales_warning)

    async def test_later_page_failure_preserves_main_data_and_marks_incomplete(self):
        state = SimpleNamespace(
            get_state=AsyncMock(return_value=SimpleNamespace(token="a"))
        )
        with patch.object(
            client,
            "async_request",
            AsyncMock(
                side_effect=[
                    {
                        "items": [{"id": 1, "Modelo": "Primeiro"}],
                        "pagination": {"total_pages": 3},
                    },
                    XanoError("timeout"),
                ]
            ),
        ):
            async for _ in VehiclesState.load.fn.read_body(
                state, "/veiculos", "Veículos"
            ):
                pass
        self.assertEqual(state.records[0]["id"], 1)
        self.assertFalse(state.complete)
        self.assertEqual(state.loaded_pages, 1)
        self.assertEqual(state.error, "timeout")

    async def test_guard_discards_stale_result_error_and_finalizer(self):
        # The browser suite additionally exercises the actual Reflex StateProxy.
        auth = SimpleNamespace(token="a", account_id="17", is_manager=True)
        nav = SimpleNamespace(generation=1)
        lock = asyncio.Lock()

        class Context:
            base_vars: ClassVar[set[str]] = {
                "read_generation",
                "client",
                "loading",
                "error",
            }

            def __init__(self):
                self.read_generation, self.client, self.loading, self.error = (
                    0,
                    {},
                    False,
                    "",
                )
                self.router = SimpleNamespace(
                    url=SimpleNamespace(path="/clientes/1"),
                    page=SimpleNamespace(params={"id": "1"}),
                    session=SimpleNamespace(client_token="fixture"),
                )

            async def __aenter__(self):
                await lock.acquire()
                return self

            async def __aexit__(self, *args):
                lock.release()

            async def get_state(self, cls):
                return auth if cls is AuthState else nav

        from app.state.client_detail_state import ClientDetailState

        for failure in (False, True):
            state = Context()
            gate = asyncio.Event()

            async def response(*args, gate=gate, failure=failure, **kwargs):
                await gate.wait()
                if failure:
                    raise XanoError("old error")
                return {"id": 1, "CNome": "Old"}

            with patch.object(client, "async_request", AsyncMock(side_effect=response)):
                task = asyncio.create_task(ClientDetailState.load.fn(state))
                await asyncio.sleep(0.01)
                async with state:  # A second session event succeeds while I/O waits.
                    state.router.url.path = "/clientes/2"
                    state.read_generation += 1
                    state.client, state.error, state.loading = (
                        {"id": "2"},
                        "new error",
                        True,
                    )
                    nav.generation += 1
                gate.set()
                await task
            self.assertEqual(state.client, {"id": "2"})
            self.assertEqual(state.error, "new error")
            self.assertTrue(state.loading)

    async def test_session_reset_keeps_local_preferences_outside_reset(self):
        reset = []
        nav = SimpleNamespace(generation=4)

        async def get_state(cls):
            if cls is NavigationState:
                return nav
            return SimpleNamespace(reset=lambda: reset.append(cls.__name__))

        await clear_operational_state(
            SimpleNamespace(
                get_state=get_state,
                router=SimpleNamespace(session=SimpleNamespace(client_token="fixture")),
            )
        )
        self.assertEqual(nav.generation, 5)
        self.assertIn("SaleDetailState", reset)
        self.assertIn("VendasState", reset)
        self.assertNotIn("SettingsState", reset)
