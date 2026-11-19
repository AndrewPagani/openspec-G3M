"""Detached read snapshots; network never holds a Reflex session lock.

Only explicitly declared output fields are committed. Every commit checks the
route generation, credentials, query inputs and worker generation again.
"""

from __future__ import annotations

import asyncio
import inspect
from copy import deepcopy
from functools import wraps
from types import MethodType, SimpleNamespace

import reflex as rx

from app.services.xano_client import client
from app.state.auth_state import AuthState

_active_reads: dict[str, set[asyncio.Task]] = {}


def cancel_reads(session: str):
    for task in tuple(_active_reads.get(session, ())):
        if task is not asyncio.current_task():
            task.cancel()


class NavigationState(rx.State):
    generation: int = 0

    async def changed(self):
        self.generation += 1
        cancel_reads(self.router.session.client_token)
        from app.state.client_detail_state import ClientDetailState
        from app.state.dashboard_state import DashboardState
        from app.state.form_state import FormState
        from app.state.resource_state import (
            ClientsState,
            PartsState,
            UsersState,
            VehiclesState,
        )
        from app.state.settings_state import SettingsState
        from app.state.vehicle_detail_state import VehicleDetailState
        from app.state.vendas_state import SaleDetailState, VendasState

        auth = await self.get_state(AuthState)
        if not auth.token:
            return
        settings = await self.get_state(SettingsState)
        theme = await settings.load()
        path = self.router.url.path.rstrip("/") or "/"
        events = {
            "/": DashboardState.load,
            "/gerenciamento": DashboardState.load,
            "/clientes": ClientsState.load("/clientes", "Clientes"),
            "/veiculos": VehiclesState.load("/veiculos", "Veículos"),
            "/pecas": PartsState.load("/pecas", "Peças e estoque"),
            "/usuarios": UsersState.load("/usuarios", "Usuários"),
            "/vendas": VendasState.load_sales_page,
            "/vendas/nova": VendasState.load_sale_references,
            "/veiculos/novo": FormState.load_vehicle_statuses,
            "/pecas/novo": FormState.load_part_areas,
        }
        if path in events:
            return [theme, events[path]]
        if path.startswith("/clientes/") and path.rsplit("/", 1)[1] != "novo":
            return [theme, ClientDetailState.load]
        if path.startswith("/veiculos/") and path.rsplit("/", 1)[1] != "novo":
            return [theme, VehicleDetailState.load]
        if path.startswith("/vendas/") and path.rsplit("/", 1)[1] != "nova":
            return [theme, SaleDetailState.load_sale]

        return theme


class ReadSnapshot(SimpleNamespace):
    async def get_state(self, state_class):
        if state_class is AuthState:
            return self._auth
        raise TypeError("Read snapshots only expose captured authentication")

    def __getattr__(self, name):
        descriptor = inspect.getattr_static(self._state_class, name)
        if isinstance(descriptor, staticmethod):
            return descriptor.__func__
        handler = getattr(self._state_class, name)
        fn = getattr(handler, "fn", handler)
        fn = getattr(fn, "read_body", fn)
        return MethodType(fn, self)


def read_event(
    *,
    outputs,
    inputs=(),
    loading="loading",
    clear=(),
    generation_field="read_generation",
    merge=(),
):
    """Turn a read-only handler into a guarded background event."""

    def decorate(body):
        @wraps(body)
        async def worker(self, *args, **kwargs):
            async with self:
                auth = await self.get_state(AuthState)
                if not auth.token:
                    return
                nav = await self.get_state(NavigationState)
                session = self.router.session.client_token
                task = asyncio.current_task()
                _active_reads.setdefault(session, set()).add(task)

                def finished(done):
                    remaining = _active_reads.get(session)
                    if remaining is not None:
                        remaining.discard(done)
                        if not remaining:
                            _active_reads.pop(session, None)

                task.add_done_callback(finished)
                generation = getattr(self, generation_field) + 1
                setattr(self, generation_field, generation)
                identity = (
                    nav.generation,
                    auth.token,
                    auth.account_id,
                    client.base_url,
                    tuple(client.api_groups.items()),
                    self.router.url.path,
                    tuple(deepcopy(getattr(self, name)) for name in inputs),
                )
                for name in clear:
                    value = getattr(self, name)
                    empty = ([] if isinstance(value, list) else {} if isinstance(value, dict)
                             else False if isinstance(value, bool) else 0 if isinstance(value, int) else "")
                    setattr(self, name, empty)
                setattr(self, loading, True)
                snapshot = ReadSnapshot(
                    **{
                        name: deepcopy(getattr(self, name))
                        for name in self.__class__.base_vars
                        if not name.startswith("router")
                    }
                )
                snapshot.router = deepcopy(self.router)
                snapshot._state_class = self.__class__
                snapshot._auth = SimpleNamespace(
                    token=auth.token,
                    account_id=auth.account_id,
                    is_manager=auth.is_manager,
                )

            async def publish():
                async with self:
                    auth = await self.get_state(AuthState)
                    nav = await self.get_state(NavigationState)
                    current = (
                        nav.generation,
                        auth.token,
                        auth.account_id,
                        client.base_url,
                        tuple(client.api_groups.items()),
                        self.router.url.path,
                        tuple(deepcopy(getattr(self, name)) for name in inputs),
                    )
                    if (
                        getattr(self, generation_field) != generation
                        or identity != current
                    ):
                        return False
                    for name in outputs:
                        value = deepcopy(getattr(snapshot, name))
                        if name in merge:
                            value = {**value, **dict(getattr(self, name))}
                        setattr(self, name, value)
                    return True

            result = body(snapshot, *args, **kwargs)
            if inspect.isasyncgen(result):
                async for _ in result:
                    if not await publish():
                        await result.aclose()
                        return
            else:
                await result
            await publish()

        worker.read_body = body
        return rx.event(background=True)(worker)

    return decorate
