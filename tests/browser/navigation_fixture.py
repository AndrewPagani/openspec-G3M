"""Standalone local Reflex backend. All Xano HTTP is replaced; unknown calls fail.

Run from repository root, then start the generated .web Vite frontend on :3000.
This server is exclusively for tests, never for normal app use.
"""

import asyncio
import sys
import time
from copy import deepcopy
from datetime import datetime
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
            return {"items": [], "pagination": {"page": page, "per_page": 100, "total": 0, "total_pages": 0}}
        if fixture_mode in {"excel", "excel-error"} and int((params or {}).get("per_page", 0)) == 100:
            if fixture_mode == "excel-error" and path == "/clientes" and page == 2:
                raise XanoError("Falha controlada de exportação")
            return excel_catalog(path, page)
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
        return {"items": rows, "pagination": {"page": page, "per_page": count, "total": count * pages, "total_pages": pages}}
    if path == "/vendas":
        if fixture_mode == "sales-error":
            raise XanoError("Vendas indisponíveis na fixture")
        search = (params or {}).get("busca", "")
        if fixture_mode in {"excel", "excel-error"} and (params or {}).get("data_inicio"):
            return paged(excel_sales(token, params), page)
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
            "pagination": {"page": page, "per_page": 1, "total": 2, "total_pages": 2},
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
        if token != "fixture-admin":
            raise XanoError("Acesso de teste restrito a administradores")
        return [{"id": 5, "UNome": "Gestora", "Email": "admin@example.test", "cargo": "Administrador",
                 "perfil_id": 1, "created_at": "2026-11-01T12:00:00Z", "Senha": "PROIBIDO-EXPORTAR"}]
    if path == "/gerenciamento/indicadores":
        sales = excel_sales(token, params) if fixture_mode in {"excel", "excel-error"} else None
        total = len(sales) if sales is not None else 2
        indicators = {
            "kpis": {
                "total_vendas_periodo": total,
                "valor_liquido_recebido_periodo": 150,
                "vendas_pagas": 1,
                "valor_bruto_vendido": 150 * total,
                "vendas_canceladas": 1 if sales else 0,
                "percentual_vendas_canceladas": 100 / total if sales else 0,
                "veiculos_disponiveis": 1,
                "pecas_qtd_disponivel": 8,
            },
        }
        if sales is not None:
            indicators["vendas_timeline"] = [
                {"periodo": row["data_venda"], "total_vendas": 1, "valor_total": 150}
                for row in sales
            ]
            indicators["vendas_por_status_pagamento"] = [
                {"status_id": 1, "descricao": "Pendente", "total_vendas": total, "valor_total": 150 * total}
            ]
            indicators["vendas_por_forma_pagamento"] = [
                {"forma_id": 1, "metodo": "Pix", "total_vendas": total, "valor_total": 150 * total}
            ]
            indicators["mix_itens"] = [{"tipo": "peca", "quantidade": total}]
            indicators["veiculos_vendidos_por_marca"] = [
                {"marca": "Marca", "quantidade": 1, "valor_total": 150, "percentual": 100}
            ]
            indicators["pecas_vendidas_por_categoria"] = [
                {"categoria": "Motor", "quantidade": 1, "valor_total": 150, "percentual": 100}
            ]
            indicators["conversao_estoque"] = {"disponivel": False}
            if token != "fixture-seller":
                indicators["vendas_por_vendedor"] = [
                    {"vendedor_id": 17, "nome": "Vendedor 17", "total_vendas": total, "valor_total": 150 * total}
                ]
                indicators["veiculos_por_status"] = [{"status_id": 2, "descricao": "Reservado", "quantidade": 1}]
                indicators["pecas_baixo_estoque"] = [{"id": 1, "nome": "Peça sem saldo", "quantidade": 0, "valor_unitario": 0}]
        return indicators
    raise XanoError("Endpoint não previsto na fixture: " + method + " " + path)


def paged(rows, page):
    return {
        "items": rows[(page - 1) * 100:page * 100],
        "pagination": {"page": page, "per_page": 100, "total": len(rows), "total_pages": (len(rows) + 99) // 100},
    }


def excel_sales(token, params):
    cases = [
        ("2026-11-01T00:00:00Z", 17),
        ("2026-11-01T23:59:59Z", 17),
        ("2026-11-01T23:59:59.001Z", 17),
        ("2026-11-02T00:00:00Z", 18),
        ("2026-10-31T23:59:59Z", 17),
        *([("2026-11-01T18:00:00Z", 17)] * 102),
    ]
    start = params["data_inicio"] + "T00:00:00+00:00"
    end = params["data_fim"] + "T23:59:59+00:00"
    return [
        {
            "id": index, "data_venda": moment, "cliente": {"CNome": f"Cliente {index}"},
            "vendedor": {"UNome": f"Vendedor {seller}"},
            "Valor_final": 150, "asaas_cobranca": {"invoice_url": "https://example.test/PROIBIDO-EXPORTAR"},
        }
        for index, (moment, seller) in enumerate(cases, start=1)
        if datetime.fromisoformat(start) <= datetime.fromisoformat(moment) <= datetime.fromisoformat(end)
        and (token != "fixture-seller" or seller == 17)
    ]


def excel_catalog(path, page):
    if path == "/clientes":
        rows = [
            {"id": index, "CNome": f"=Cliente {index}", "CPF": "00000000001",
             "Telefone": "+550000001", "created_at": "2026-10-15T12:00:00Z"}
            for index in range(1, 1002)
        ]
    elif path == "/veiculos":
        rows = [{"id": 1, "Marca": "Marca", "status_descricao": "Reservado", "Preco": 10000}]
    else:
        rows = [{"id": 1, "PCNome": "Peça sem saldo", "qtd_disp": 0}]
    return paged(rows, page)


async def async_request(method, path, **kwargs):
    captured_mode, captured_delay = mode, delay
    call = {
        "method": method,
        "path": path,
        "params": kwargs.get("params"),
        "at": time.monotonic(),
    }
    calls.append(call)
    if captured_mode == "excel-timeout" and path == "/vendas" and (kwargs.get("params") or {}).get("data_inicio"):
        raise TimeoutError
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
