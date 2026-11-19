"""Bounded, credential-scoped reference cache. Never stores operational records."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from copy import deepcopy
from hashlib import sha256
from time import monotonic

from app.services.xano_client import XanoError, client

CATALOGS = frozenset({"/formas-pagamento", "/status-veiculos", "/veiculo-areas"})


class CatalogCache:
    def __init__(self, clock=monotonic):
        self.clock = clock
        self.entries = OrderedDict()
        self.pending = {}
        self.latest = {}
        self.tasks = set()
        self.epoch = 0

    def invalidate(self):
        # In-flight requests may finish for their consumers, but cannot refill cache.
        self.epoch += 1
        self.entries.clear()
        self.pending.clear()
        self.latest.clear()

    async def close(self):
        tasks = tuple(self.tasks)
        self.invalidate()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def get(self, path: str, token: str, *, force: bool = False):
        if path not in CATALOGS:
            raise ValueError("Only reference catalogs may be cached")
        credential = sha256(token.removeprefix("Bearer ").strip().encode()).hexdigest()
        key = (client._url(path), credential)
        now = self.clock()
        for old in list(self.entries):
            if self.entries[old][0] <= now:
                del self.entries[old]
        if not force and key in self.entries:
            return deepcopy(self.entries[key][1])
        if force:
            self.entries.pop(key, None)
        flight_key = (self.epoch, key, force)
        task = self.pending.get(flight_key)
        if task is None:
            epoch = self.epoch
            revision = object()
            self.latest[key] = revision

            async def fetch():
                response = await client.async_request("GET", path, token=token)
                rows = response if isinstance(response, list) else None
                if path == "/formas-pagamento" and isinstance(response, dict):
                    pagination = response.get("pagination", {})
                    if not isinstance(pagination, dict) or pagination.get(
                        "total_pages", 1
                    ) not in (0, "0", 1, "1"):
                        raise XanoError("A API retornou um catálogo incompleto.")
                    rows = response.get("items", response.get("data"))
                name = {
                    "/formas-pagamento": "Metodo",
                    "/status-veiculos": "Descricao",
                    "/veiculo-areas": "Secao",
                }[path]
                if not isinstance(rows, list) or any(
                    not isinstance(row, dict)
                    or (
                        row.get("id", row.get("Id"))
                        if path == "/formas-pagamento"
                        else row.get("id")
                    )
                    is None
                    or not str(
                        row.get(
                            name,
                            row.get("metodo", "")
                            if path == "/formas-pagamento"
                            else "",
                        )
                    ).strip()
                    for row in rows
                ):
                    raise XanoError("A API retornou um catálogo em formato inválido.")
                if epoch == self.epoch and self.latest.get(key) is revision:
                    self.entries[key] = (self.clock() + 300, deepcopy(response))
                    while len(self.entries) > 128:
                        self.entries.popitem(last=False)
                return response

            task = asyncio.create_task(fetch())
            self.tasks.add(task)
            self.pending[flight_key] = task

            def finished(done):
                self.tasks.discard(done)
                if self.latest.get(key) is revision:
                    self.latest.pop(key, None)
                if self.pending.get(flight_key) is done:
                    self.pending.pop(flight_key, None)
                if not done.cancelled():
                    done.exception()  # Retrieve errors even when every consumer left.

            task.add_done_callback(finished)
        return deepcopy(await asyncio.shield(task))


catalogs = CatalogCache()
