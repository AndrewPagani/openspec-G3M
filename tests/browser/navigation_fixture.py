"""Standalone local Reflex backend. All Xano HTTP is replaced; unknown calls fail.

Run from repository root, then start the generated .web Vite frontend on :3000.
This server is exclusively for tests, never for normal app use.
"""

import asyncio
import sys
import time
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import uvicorn
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.app import app
from app.services.catalogs import catalogs
from app.services.xano_client import XanoError, client

mode = "normal"
delay = 0.35
calls = []
names = {}


def response(method, path, *, token="", params=None, json=None, fixture_mode="normal"):
    page = int((params or {}).get("page", 1))
    account = "Conta B " if token == "fixture-account-b" else ""
    if path == "/auth/login":
        return {
            "authToken": "fixture-account-b",
            "user": {"id": 18, "UNome": "Conta B", "perfil": {"Cargo": "Gerente"}},
        }
    if path == "/status-veiculos":
        return [
            {"id": 1, "Descricao": "Disponível"},
            {"id": 2, "Descricao": "Reservado"},
        ]
    if path == "/veiculo-areas":
        return [{"id": 1, "Secao": "Motor"}]
    if path == "/formas-pagamento":
        return [{"id": 1, "Metodo": "Pix"}]
    if path in {"/clientes", "/veiculos", "/pecas"}:
        if fixture_mode == "page-error" and page == 2:
            raise XanoError("Falha controlada na segunda página. Atualize a lista.")
        if fixture_mode == "timeout":
            raise XanoError(
                "Não foi possível conectar ao Xano. Verifique a URL e a rede."
            )
        if fixture_mode == "empty":
            return {"items": [], "pagination": {"total_pages": 0}}
        count, pages = (100, 10) if fixture_mode == "large" else (1, 2)
        rows = []
        for index in range((page - 1) * count + 1, page * count + 1):
            if path == "/clientes":
                row = {
                    "id": index,
                    "CNome": account + names.get(index, f"Cliente visual {index}"),
                    "CPF": "00000000000",
                    "Email": f"visual{index}@example.test",
                    "Telefone": "11900000001",
                    "created_at": "2026-11-01T12:00:00Z",
                }
            elif path == "/veiculos":
                row = {
                    "id": index,
                    "Marca": "Veículo visual",
                    "Modelo": str(index),
                    "Ano": 2025,
                    "Preco": 40000,
                    "status_id": 1,
                }
            else:
                row = {
                    "id": index,
                    "PCNome": f"Peça visual {index}",
                    "PCvalor": 150,
                    "qtd_disp": 8,
                    "area_id": 1,
                }
            rows.append(row)
        return {"items": rows, "pagination": {"total_pages": pages}}
    if path == "/vendas":
        if fixture_mode == "sales-error":
            raise XanoError("Vendas indisponíveis na fixture")
        search = (params or {}).get("busca", "")
        return {
            "items": [
                {
                    "id": page,
                    "cliente_id": 1,
                    "cliente": {"CNome": f"{search or account}Cliente visual 1"},
                    "vendedor": {"UNome": "Vendedor visual"},
                    "Valor_final": 150,
                    "data_venda": "2026-11-01T12:00:00Z",
                    "status": {"Descricao_venda": "Pendente"},
                }
            ],
            "pagination": {"total_pages": 2},
        }
    if path.startswith("/clientes/"):
        identity = int(path.rsplit("/", 1)[1])
        if method == "DELETE":
            return {"deleted": True}
        if method == "PATCH":
            names[identity] = json["CNome"]
        if fixture_mode == "stale-error" and identity == 1:
            raise XanoError("Erro antigo do detalhe 1")
        return {
            "id": identity,
            "CNome": account + names.get(identity, f"Detalhe visual {identity}"),
            "CPF": "00000000000",
            "Email": "visual@example.test",
            "Telefone": "11900000001",
            "created_at": "2026-11-01T12:00:00Z",
        }
    if path.startswith("/veiculos/"):
        return {
            "id": int(path.rsplit("/", 1)[1]),
            "Marca": "Detalhe veículo",
            "Modelo": path.rsplit("/", 1)[1],
        }
    if path.startswith("/vendas/") and path.endswith("/pagamento"):
        return {
            "payment_flow": "ASAAS",
            "total_venda": 150,
            "invoice_url": f"https://sandbox.asaas.com/i/fixture-{path.split('/')[2]}",
            "status": "PENDING",
        }
    if path == "/usuarios":
        return {"items": []}
    if path == "/gerenciamento/indicadores":
        return {
            "kpis": {
                "total_vendas_periodo": 1,
                "valor_liquido_recebido_periodo": 150,
                "vendas_pagas": 1,
                "valor_bruto_vendido": 150,
                "vendas_canceladas": 0,
                "percentual_vendas_canceladas": 0,
                "veiculos_disponiveis": 1,
                "pecas_qtd_disponivel": 8,
            }
        }
    raise XanoError("Endpoint não previsto na fixture: " + method + " " + path)


async def async_request(method, path, **kwargs):
    captured_mode, captured_delay = mode, delay
    call = {
        "method": method,
        "path": path,
        "params": kwargs.get("params"),
        "at": time.monotonic(),
    }
    calls.append(call)
    extra = (
        1.3
        if (
            (captured_mode == "slow-sales" and path == "/vendas")
            or (captured_mode == "slow-methods" and path == "/formas-pagamento")
            or (captured_mode in {"race", "stale-error"} and path.endswith("/1"))
            or (
                captured_mode == "race"
                and (kwargs.get("params") or {}).get("busca") == "old"
            )
            or (
                captured_mode == "write-during-read"
                and (kwargs.get("params") or {}).get("page") == 2
            )
        )
        else 0
    )
    # Snapshot a GET at dispatch, so a late response can contain pre-write values.
    result, error = None, None
    try:
        result = deepcopy(response(method, path, fixture_mode=captured_mode, **kwargs))
    except XanoError as exc:
        error = exc
    try:
        await asyncio.sleep(captured_delay + extra)
    except asyncio.CancelledError:
        call["cancelled"] = True
        raise
    call["finished"] = time.monotonic()
    if error:
        raise error
    return result


def forbidden_sync(*args, **kwargs):
    raise AssertionError("Blocking UI HTTP is forbidden in the fixture")


client.request = forbidden_sync
client.async_request = async_request
application = app()


async def control(request):
    global mode, delay
    if request.method == "POST":
        body = await request.json()
        mode, delay = body.get("mode", "normal"), float(body.get("delay", 0.35))
        if body.get("reset"):
            calls.clear()
            names.clear()
            catalogs.invalidate()
    return JSONResponse({"mode": mode, "calls": calls})


app._api.routes.append(Route("/fixture-control", control, methods=["GET", "POST"]))
if __name__ == "__main__":
    uvicorn.run(application, host="127.0.0.1", port=8001, log_level="warning")
