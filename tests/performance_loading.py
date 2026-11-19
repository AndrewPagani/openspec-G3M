"""Reproducible synthetic before/after load + loop responsiveness benchmark.

Historical code is read from git, never checked out over the working tree.
There are no external calls. Run from the repo root with its Python environment.
"""

import argparse
import ast
import asyncio
import json
import subprocess
import sys
import time
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from types import SimpleNamespace
from unittest.mock import patch

from app.services.xano_client import client
from app.state.resource_state import ClientsState


async def measure(body, *, blocking):
    state = SimpleNamespace(records=[{"id": "previous"}], get_state=None)

    async def auth(_):
        return SimpleNamespace(token="fixture")

    state.get_state = auth
    requests, yields, ticks = [], [], []

    def response(method, path, **kwargs):
        page = int(kwargs["params"]["page"])
        requests.append({"path": path, "page": page})
        if path == "/vendas":
            return {"items": [], "pagination": {"total_pages": 1}}
        return {
            "items": [
                {"id": i, "CNome": f"Cliente {i}", "created_at": "2026-11-01T12:00:00Z"}
                for i in range((page - 1) * 100 + 1, page * 100 + 1)
            ],
            "pagination": {"total_pages": 10},
        }

    def sync_request(*args, **kwargs):
        time.sleep(0.04)
        return response(*args, **kwargs)

    async def async_request(*args, **kwargs):
        await asyncio.sleep(0.04)
        return response(*args, **kwargs)

    async def heartbeat():
        while True:
            ticks.append(time.perf_counter())
            await asyncio.sleep(0.002)

    ticker = asyncio.create_task(heartbeat())
    await asyncio.sleep(0)
    start = time.perf_counter()
    with (
        patch.object(client, "request", side_effect=sync_request),
        patch.object(client, "async_request", side_effect=async_request),
    ):
        if blocking:
            await body(state, "/clientes", "Clientes")
            yields.append(
                (time.perf_counter() - start, len(state.records), state.loading)
            )
        else:
            async for _ in body(state, "/clientes", "Clientes"):
                yields.append(
                    (time.perf_counter() - start, len(state.records), state.loading)
                )
            yields.append(
                (time.perf_counter() - start, len(state.records), state.loading)
            )
    elapsed = time.perf_counter() - start
    await asyncio.sleep(0.006)
    ticker.cancel()
    await asyncio.gather(ticker, return_exceptions=True)
    return {
        "fixture_only": True,
        "rows": len(state.records),
        "requests": len(requests),
        "first_feedback_ms": round(yields[0][0] * 1000, 1),
        "first_data_ms": round(next(t for t, n, _ in yields if n and n != 1) * 1000, 1),
        "complete_ms": round(elapsed * 1000, 1),
        "updates": len(yields),
        "max_heartbeat_gap_ms": round(
            max(b - a for a, b in pairwise(ticks)) * 1000, 1
        ),
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline-ref", default="970758fbd1ecf109000b6f8ec8dbe2c9dec9f07a"
    )
    args = parser.parse_args()
    raw = await asyncio.to_thread(subprocess.check_output, ["git", "show", args.baseline_ref + ":app/state/resource_state.py"])
    source = raw.decode("utf-8")
    tree = ast.parse(source)
    functions = [node for node in tree.body if not isinstance(node, ast.ClassDef)]
    old_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "ResourceState"
    )
    load = deepcopy(
        next(
            node
            for node in old_class.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "load"
        )
    )
    load.decorator_list = []
    load.name = "historical_load"
    functions.append(load)
    namespace = {"__name__": "historical_load_benchmark"}
    exec(  # noqa: S102 -- local historical reader, with all HTTP replaced below
        compile(
            ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])),
            "<historical resource reader>",
            "exec",
        ),
        namespace,
    )
    report = {
        "baseline_ref": args.baseline_ref,
        "baseline": await measure(namespace["historical_load"], blocking=True),
        "final": await measure(ClientsState.load.fn.read_body, blocking=False),
    }
    out = Path(".impeccable/review/navigation")
    out.mkdir(parents=True, exist_ok=True)
    (out / "loop-benchmark.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report))


if __name__ == "__main__":
    asyncio.run(main())
