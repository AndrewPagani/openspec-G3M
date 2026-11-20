"""Collect and write an authenticated dashboard report."""

from __future__ import annotations

import asyncio
import io
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime, timezone
from math import isfinite
from typing import Any
from zoneinfo import ZoneInfo

from xlsxwriter import Workbook

from app.services.sales_query import sales_query_params
from app.services.xano_client import XanoError, client

MAX_ROWS = 20_000
MAX_BYTES = 1_000_000
TIMEOUT_SECONDS = 90
PAGE_SIZE = 100
MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
LOCAL_ZONE = ZoneInfo("America/Sao_Paulo")
SALES_FILTERS = (
    "data_inicio",
    "data_fim",
    "status_id",
    "vendedor_id",
    "forma_pagamento_id",
)

# Each sheet selects individual scalar fields. Dot paths never serialize objects.
COLUMNS = {
    "Vendas": (
        ("ID", "id", "text"),
        ("Data da venda (UTC)", "data_venda", "utc"),
        ("Cliente", "cliente.CNome", "text"),
        ("Vendedor", "vendedor.UNome", "text"),
        ("Forma de pagamento", "forma_pagamento.Metodo", "text"),
        ("Status", "status.Descricao_venda", "text"),
        ("Valor bruto", "Valor_bruto", "money"),
        ("Desconto", "Desconto", "money"),
        ("Valor final", "Valor_final", "money"),
    ),
    "Clientes": (
        ("ID", "id", "text"),
        ("Nome", "CNome", "text"),
        ("CPF", "CPF", "text"),
        ("Telefone", "Telefone", "text"),
        ("E-mail", "Email", "text"),
        ("Cadastro", "created_at", "datetime"),
    ),
    "Veículos": (
        ("ID", "id", "text"),
        ("Marca", "Marca", "text"),
        ("Modelo", "Modelo", "text"),
        ("Ano", "Ano", "int"),
        ("Placa", "Placa", "text"),
        ("Quilometragem", "Quilometragem", "number"),
        ("Preço", "Preco", "money"),
        ("Status", "status_descricao", "text"),
    ),
    "Peças": (
        ("ID", "id", "text"),
        ("Nome", "PCNome", "text"),
        ("Área", "area_secao", "text"),
        ("Preço", "PCvalor", "money"),
        ("Saldo", "qtd_disp", "int"),
    ),
    "Usuários": (
        ("ID", "id", "text"),
        ("Nome", "UNome", "text"),
        ("E-mail", "Email", "text"),
        ("Perfil", "cargo", "text"),
        ("ID do perfil", "perfil_id", "text"),
        ("Cadastro", "created_at", "datetime"),
    ),
}

ROUTES = {
    "Vendas": "/vendas",
    "Clientes": "/clientes",
    "Veículos": "/veiculos",
    "Peças": "/pecas",
    "Usuários": "/usuarios",
}


class ReportError(Exception):
    """A safe message for the dashboard, without upstream payloads."""


class ReportCancelled(Exception):
    """The session owning this export changed."""


def _bounded_size(count: int, area: str) -> None:
    if count > MAX_ROWS:
        raise ReportError(
            f"{area} excede o limite de {MAX_ROWS:,} linhas.".replace(",", ".")
        )


def _records(value: Any) -> list[dict]:
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("Invalid record list")
    return value


def _integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError("Expected integer")
    return int(value)


async def _collection(
    area: str,
    token: str,
    filters: dict[str, str],
    progress: Callable[[str], Awaitable[None]],
) -> list[dict]:
    route = ROUTES[area]
    if area == "Usuários":
        rows = _records(await client.async_request("GET", route, token=token))
        _bounded_size(len(rows), area)
    else:
        rows = []
        expected = None
        page = 1
        while True:
            if expected is not None:
                await progress(f"Consultando {area} · página {page} de {expected[2]}…")
            query = {"page": str(page), "per_page": str(PAGE_SIZE)}
            if area == "Vendas":
                query = sales_query_params(page=page, per_page=PAGE_SIZE, **filters)
            response = await client.async_request(
                "GET", route, token=token, params=query
            )
            if not isinstance(response, dict) or not isinstance(
                response.get("pagination"), dict
            ):
                raise TypeError("Missing pagination")
            pagination = response["pagination"]
            total = _integer(pagination["total"])
            per_page = _integer(pagination["per_page"])
            pages = _integer(pagination["total_pages"])
            _bounded_size(total, area)
            if (
                _integer(pagination["page"]) != page
                or total < 0
                or not 1 <= per_page <= PAGE_SIZE
                or (
                    pages != (total + per_page - 1) // per_page
                    and (total, pages) != (0, 1)
                )
            ):
                raise ValueError("Invalid pagination")
            current = (total, per_page, pages)
            if expected is not None and expected != current:
                raise ValueError("Pagination changed")
            expected = current
            batch = _records(response.get("items"))
            if len(batch) != min(per_page, total - len(rows)):
                raise ValueError("Incomplete page")
            rows.extend(batch)
            if page >= pages:
                break
            page += 1

    ids = set()
    for row in rows:
        value = row.get("id")
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, str))
            or not str(value).strip()
        ):
            raise ValueError("Missing record ID")
        identifier = str(value)
        if identifier in ids:
            raise ValueError("Duplicate record ID")
        ids.add(identifier)
    return rows


async def collect_report(
    token: str,
    params: dict[str, str | int],
    include_users: bool,
    progress: Callable[[str], Awaitable[None]],
) -> tuple[dict, dict[str, list[dict]]]:
    area = "Dashboard"
    try:
        await progress(f"Consultando {area}…")
        dashboard = await client.async_request(
            "GET", "/gerenciamento/indicadores", token=token, params=params
        )
        if not isinstance(dashboard, dict):
            raise TypeError("Invalid dashboard")
        if isinstance(dashboard.get("data"), dict):
            dashboard = {**dashboard["data"], **dashboard}
        filters = {key: str(params[key]) for key in SALES_FILTERS if key in params}
        collections = {}
        for area in ROUTES:
            if area == "Usuários" and not include_users:
                continue
            await progress(f"Consultando {area}…")
            collections[area] = await _collection(area, token, filters, progress)
        return dashboard, collections
    except (KeyError, TypeError, ValueError, XanoError) as exc:
        raise ReportError(
            f"Não foi possível consultar {area}. Tente exportar novamente."
        ) from exc


def _field(row: dict, path: str) -> Any:
    value = row
    for key in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _timestamp(value: Any, zone: ZoneInfo | timezone) -> date | datetime:
    if isinstance(value, (int, float)) or str(value).lstrip("-").isdigit():
        epoch = float(value)
        parsed = datetime.fromtimestamp(
            epoch / 1000 if abs(epoch) >= 10_000_000_000 else epoch, tz=UTC
        )
    elif len(str(value)) == 10:
        return date.fromisoformat(str(value))
    else:
        parsed = datetime.fromisoformat(str(value))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(zone).replace(tzinfo=None)


def _cell_value(value: Any, kind: str, label: str) -> Any:
    if value is None or value == "":
        return None
    if kind == "text":
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError("Expected scalar text")
        if len(str(value)) > 32_767:
            raise ValueError("Text exceeds Excel cell capacity")
        return str(value)
    if kind in ("date", "month"):
        return date.fromisoformat(str(value))
    if kind in ("datetime", "utc"):
        return _timestamp(value, UTC if kind == "utc" else LOCAL_ZONE)
    # Use the same numeric parser and integer validation as the Dashboard.
    from app.state.dashboard_state import _count, _decimal

    number = _decimal(value, label)
    if not number.is_finite():
        raise ValueError("Expected finite number")
    if kind == "int":
        return int(_count(value, label))
    result = float(number / 100 if kind == "percent" else number)
    if not isfinite(result):
        raise ValueError("Expected finite Excel number")
    return result


COUNT = ("Quantidade", "quantidade", "int")
SALE_COUNT = ("Vendas", "total_vendas", "int")
AMOUNT = ("Valor total", "valor_total", "money")
SHARE = ("Participação", "percentual", "percent")
SERIES = (
    (
        "Vendas por status",
        ("vendas_por_status_pagamento", "vendas_por_status"),
        (("Status", "descricao", "text"), SALE_COUNT, AMOUNT),
        False,
    ),
    (
        "Vendas por forma de pagamento",
        ("vendas_por_forma_pagamento", "vendas_por_metodo_pagamento", "pagamentos"),
        (("Forma de pagamento", "metodo", "text"), SALE_COUNT, AMOUNT),
        False,
    ),
    (
        "Mix de itens",
        ("mix_itens", "vendas_por_tipo_item"),
        (("Tipo", "tipo", "text"), COUNT),
        False,
    ),
    (
        "Veículos vendidos por marca",
        ("veiculos_vendidos_por_marca",),
        (("Marca", "marca", "text"), COUNT, AMOUNT, SHARE),
        False,
    ),
    (
        "Peças vendidas por categoria",
        ("pecas_vendidas_por_categoria",),
        (("Categoria", "categoria", "text"), COUNT, AMOUNT, SHARE),
        False,
    ),
    (
        "Peças vendidas por fabricante",
        ("pecas_vendidas_por_fabricante",),
        (("Fabricante", "fabricante", "text"), COUNT, AMOUNT, SHARE),
        False,
    ),
    (
        "Vendas por vendedor",
        ("vendas_por_vendedor",),
        (("Vendedor", "nome", "text"), SALE_COUNT, AMOUNT),
        True,
    ),
    (
        "Veículos por status",
        ("veiculos_por_status", "estoque_veiculos_por_status"),
        (("Status", "descricao", "text"), COUNT),
        True,
    ),
    (
        "Peças com saldo baixo",
        ("pecas_baixo_estoque",),
        (
            ("Peça", "nome", "text"),
            COUNT,
            ("Preço unitário", "valor_unitario", "money"),
        ),
        True,
    ),
)
KPI_COLUMNS = (
    ("Vendas no período", "total_vendas_periodo", "int"),
    ("Valor bruto vendido", "valor_bruto_vendido", "money"),
    ("Valor líquido recebido no período", "valor_liquido_recebido_periodo", "money"),
    ("Vendas pagas", "vendas_pagas", "int"),
    ("Ticket médio das vendas pagas", "ticket_medio_vendas_pagas", "money"),
    ("Vendas concluídas", "vendas_concluidas", "int"),
    ("Descontos", "descontos", "money"),
    ("Vendas canceladas", "vendas_canceladas", "int"),
    ("Percentual de cancelamentos", "percentual_vendas_canceladas", "percent"),
)
STOCK_KPIS = (
    ("Veículos no status selecionado", "veiculos_disponiveis", "int"),
    ("Valor dos veículos no status selecionado", "valor_veiculos_disponiveis", "money"),
    ("Unidades de peças disponíveis", "pecas_qtd_disponivel", "int"),
    ("Valor do estoque de peças", "valor_estoque_pecas", "money"),
    ("Peças com saldo baixo (até 5)", "pecas_sem_estoque", "int"),
)
ANALYSES = (
    (
        "Conversão de estoque",
        "conversao_estoque",
        (
            ("Propostas", "propostas_total", "int"),
            ("Convertidas", "propostas_convertidas", "int"),
            ("Taxa de conversão", "taxa_conversao", "percent"),
        ),
    ),
    (
        "Giro de estoque",
        "giro_estoque",
        (
            ("Entradas", "entradas_quantidade", "int"),
            ("Saídas", "saidas_quantidade", "int"),
            ("Estoque médio", "estoque_medio", "number"),
            ("Giro", "giro", "number"),
        ),
    ),
)


def _dashboard(
    sheet, data, collections, params, group, manager, profile, filter_labels, formats
):
    from app.state.dashboard_state import (
        _decimal,
        _extract_kpis,
        _extract_series,
        _trend_chart_rows,
    )

    kpis = _extract_kpis(data)
    required = {key for _, key, _ in KPI_COLUMNS} - {
        "ticket_medio_vendas_pagas",
        "vendas_concluidas",
        "descontos",
    }
    if manager:
        required.update(("veiculos_disponiveis", "pecas_qtd_disponivel"))
    if any(kpis.get(key) is None for key in required):
        raise ValueError("Missing required dashboard metrics")
    total = _cell_value(kpis["total_vendas_periodo"], "int", "vendas no período")
    if total != len(collections["Vendas"]):
        raise ReportError(
            "A quantidade de Vendas divergiu do Dashboard. Tente exportar novamente."
        )

    sheet.write_row(0, 0, ["Relatório do Dashboard", "Valor"], formats["header"])
    metadata = (
        (
            "Gerado em (São Paulo)",
            datetime.now(LOCAL_ZONE).replace(tzinfo=None),
            "datetime",
        ),
        ("Perfil", profile, "text"),
        ("Data inicial (UTC)", params["data_inicio"], "date"),
        ("Data final (UTC)", params["data_fim"], "date"),
        (
            "Agrupamento",
            {"dia": "Dia", "semana": "Semana", "mes": "Mês", "ano": "Ano"}[group],
            "text",
        ),
        ("Status da venda", filter_labels.get("status_id", "Todos"), "text"),
        ("Vendedor", filter_labels.get("vendedor_id", "Todos autorizados"), "text"),
        (
            "Forma de pagamento",
            filter_labels.get("forma_pagamento_id", "Todas"),
            "text",
        ),
        (
            "Tipo de item (séries de itens)",
            {"veiculo": "Veículo", "peca": "Peça"}.get(
                params.get("tipo_item"), "Todos"
            ),
            "text",
        ),
        (
            "Status do veículo (estoque)",
            filter_labels.get("status_veiculo_id", "Disponível por padrão"),
            "text",
        ),
        (
            "Recorte de Vendas",
            "Datas, status, vendedor e forma de pagamento do Dashboard",
            "text",
        ),
        (
            "Recorte dos cadastros",
            "Todos os registros autorizados, independentemente do período",
            "text",
        ),
        ("Total por aba", "Registros", "text"),
        *((area, len(rows), "int") for area, rows in collections.items()),
    )
    for row, (label, value, kind) in enumerate(metadata, start=1):
        sheet.write_string(row, 0, label)
        typed = value if kind == "datetime" else _cell_value(value, kind, label)
        sheet.write(row, 1, typed, formats.get(kind))

    row = len(metadata) + 2
    sheet.write_row(row, 0, ["Indicadores", "Valor"], formats["header"])
    metrics = [(name, kpis.get(key), kind) for name, key, kind in KPI_COLUMNS]
    metrics.append(
        (
            "Ticket médio",
            _decimal(kpis["valor_bruto_vendido"], "valor bruto") / total
            if total
            else 0,
            "money",
        )
    )
    if manager:
        metrics.extend(
            (name, _extract_series(data, key) if key not in kpis else kpis[key], kind)
            for name, key, kind in STOCK_KPIS
        )
    for name, value, kind in metrics:
        if value is not None:
            row += 1
            sheet.write_string(row, 0, name)
            sheet.write(row, 1, _cell_value(value, kind, name), formats.get(kind))

    timeline = _extract_series(data, "vendas_timeline")
    if timeline is None:
        timeline = _extract_series(data, "vendas_por_periodo")
    if isinstance(timeline, list):
        _bounded_size(len(timeline), "Série de vendas")
    by_period = _trend_chart_rows(timeline, group)
    period_kind = "text"
    if group in ("dia", "mes"):
        period_kind = "month" if group == "mes" else "date"
        if group == "mes":
            by_period = [
                {**item, "periodo": item["periodo"] + "-01"} for item in by_period
            ]
    elif group == "ano":
        period_kind = "int"
    row += 2
    sheet.write_string(row, 0, "Vendas por período")
    row = _write_table(
        sheet,
        row + 1,
        (("Período", "periodo", period_kind), SALE_COUNT, AMOUNT),
        by_period,
        formats,
    )

    for name, keys, columns, manager_only in SERIES:
        if manager_only and not manager:
            continue
        raw = _extract_series(data, *keys)
        if isinstance(raw, dict):
            raw = next(
                (
                    raw[key]
                    for key in ("items", "data", "results", "rows", *keys)
                    if key in raw
                ),
                raw,
            )
        rows = [] if raw is None else _records(raw)
        _bounded_size(len(rows), name)
        sheet.write_string(row, 0, name)
        row = _write_table(sheet, row + 1, columns, rows, formats)

    for name, key, columns in ANALYSES:
        raw = _extract_series(data, key)
        sheet.write_string(row, 0, name)
        if raw is None or (isinstance(raw, dict) and raw.get("disponivel") is False):
            sheet.write_string(row + 1, 0, "Não disponível")
            row += 3
        else:
            rows = [raw] if isinstance(raw, dict) else _records(raw)
            _bounded_size(len(rows), name)
            row = _write_table(sheet, row + 1, columns, rows, formats)


def _write_table(sheet, start, columns, rows, formats):
    sheet.write_row(start, 0, [name for name, _, _ in columns], formats["header"])
    for index, row in enumerate(rows, start=start + 1):
        for column, (name, path, kind) in enumerate(columns):
            value = _cell_value(_field(row, path), kind, name)
            sheet.write(index, column, value, formats.get(kind))
    if not rows:
        sheet.write_string(start + 1, 0, "Nenhum registro")
    return start + max(len(rows), 1) + 3


async def build_report(*args) -> bytes:
    """Keep workbook serialization outside the event loop."""
    return await asyncio.to_thread(_workbook, *args)


def _workbook(
    dashboard: dict,
    collections: dict[str, list[dict]],
    params: dict[str, str | int],
    group: str,
    manager: bool,
    profile: str,
    filter_labels: dict[str, str],
) -> bytes:
    output = io.BytesIO()
    area = "Dashboard"
    try:
        with Workbook(
            output,
            {
                "in_memory": True,
                "strings_to_formulas": False,
                "strings_to_urls": False,
                "strings_to_numbers": False,
            },
        ) as book:
            formats = {
                "header": book.add_format(
                    {"bold": True, "font_color": "white", "bg_color": "#24455D"}
                ),
                "money": book.add_format({"num_format": '"R$" #,##0.00'}),
                "percent": book.add_format({"num_format": "0.00%"}),
                "date": book.add_format({"num_format": "dd/mm/yyyy"}),
                "month": book.add_format({"num_format": "mm/yyyy"}),
                "datetime": book.add_format({"num_format": "dd/mm/yyyy hh:mm:ss"}),
                "number": book.add_format({"num_format": "0.00"}),
            }
            formats["utc"] = formats["datetime"]
            sheet = book.add_worksheet(area)
            sheet.set_column(0, 0, 43)
            sheet.set_column(1, 1, 36)
            sheet.set_column(2, 4, 19)
            sheet.freeze_panes(1, 0)
            _dashboard(
                sheet,
                dashboard,
                collections,
                params,
                group,
                manager,
                profile,
                filter_labels,
                formats,
            )
            for area, rows in collections.items():
                sheet = book.add_worksheet(area)
                columns = COLUMNS[area]
                for index, (name, _, kind) in enumerate(columns):
                    width = max(
                        len(name) + 3, 25 if kind in ("text", "datetime", "utc") else 15
                    )
                    sheet.set_column(index, index, width)
                sheet.freeze_panes(1, 0)
                _write_table(sheet, 0, columns, rows, formats)
                sheet.autofilter(0, 0, len(rows), len(columns) - 1)
    except (KeyError, TypeError, ValueError, OverflowError, OSError, XanoError) as exc:
        raise ReportError(
            f"Não foi possível montar a aba {area}. Tente exportar novamente."
        ) from exc
    if output.tell() > MAX_BYTES:
        raise ReportError(
            "O arquivo excede 1 MB. Reduza o período ou os filtros de vendas e tente novamente."
        )
    return output.getvalue()
