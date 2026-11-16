from __future__ import annotations

import csv
import hashlib
import io
from collections.abc import AsyncIterator
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

import reflex as rx

from app.services.vehicle_status import vehicle_status_chart_color
from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState


def _decimal(value: Any, label: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise XanoError(f"A API retornou um valor inválido para {label}.") from exc


def _rounded_number(value: Any, label: str) -> float:
    return float(_decimal(value, label).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _currency(value: Any, label: str) -> str:
    amount = _decimal(value, label)
    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def _average_currency(total: Any, count: Any, label: str) -> str:
    total_amount = _decimal(total, f"total de {label}")
    count_amount = _decimal(count, f"quantidade de {label}")
    if count_amount < 0 or count_amount != count_amount.to_integral_value():
        raise XanoError(f"A API retornou uma quantidade inválida para {label}.")
    if count_amount == 0:
        return _currency(0, label)
    return _currency(total_amount / count_amount, label)


def _percentage(value: Any, label: str) -> str:
    return f"{_decimal(value, label):.2f}%".replace(".", ",")


def _count(value: Any, label: str) -> str:
    amount = _decimal(value, label)
    if amount != amount.to_integral_value():
        raise XanoError(f"A API retornou uma quantidade inválida para {label}.")
    return str(int(amount))


def _report_rows(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise XanoError(f"A API retornou uma lista inválida para {label}.")

    rows: list[str] = []
    for row in value:
        if not isinstance(row, dict):
            rows.append(str(row))
            continue
        columns = []
        for key, item in row.items():
            normalized_key = str(key).lower()
            if normalized_key == "id" or normalized_key.endswith("_id"):
                continue
            title = str(key).replace("_", " ").capitalize()
            if isinstance(item, (int, float, Decimal)):
                if "percentual" in normalized_key or normalized_key.endswith("_percent"):
                    item = _percentage(item, title)
                elif normalized_key in {"total_vendas", "quantidade", "count", "qtd"}:
                    item = _count(item, title)
                elif any(
                    term in normalized_key
                    for term in ("valor", "bruto", "liquido", "total", "ticket", "desconto")
                ):
                    item = _currency(item, title)
            columns.append(f"{title}: {item}")
        rows.append(" · ".join(columns) or "Registro disponível")
    return rows


def _analysis_rows(value: Any, label: str) -> list[str]:
    if isinstance(value, dict) and value.get("disponivel") is False:
        return ["Não disponível no contrato atual do Xano."]
    if isinstance(value, dict):
        columns = []
        for key, item in value.items():
            normalized_key = str(key).lower()
            title = str(key).replace("_", " ").capitalize()
            if isinstance(item, (int, float, Decimal)) and not isinstance(item, bool):
                if "percentual" in normalized_key or normalized_key.startswith("taxa"):
                    item = _percentage(item, title)
                elif "valor" in normalized_key:
                    item = _currency(item, title)
                elif normalized_key in {
                    "propostas_total",
                    "propostas_convertidas",
                    "entradas_quantidade",
                    "saidas_quantidade",
                }:
                    item = _count(item, title)
            columns.append(f"{title}: {item}")
        return [" · ".join(columns) or "Registro disponível"]
    return _report_rows(value, label)


def _salesperson_rows(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        for key in ("items", "data", "results", "rows", "vendas_por_vendedor"):
            nested = value.get(key)
            if isinstance(nested, list):
                value = nested
                break
    if not isinstance(value, list):
        raise XanoError("A API retornou uma lista inválida para vendas por vendedor.")

    rows = []
    for row in value:
        if not isinstance(row, dict):
            raise XanoError("A API retornou um registro inválido para vendas por vendedor.")
        name = row.get("nome") or row.get("UNome") or row.get("name") or row.get("vendedor")
        if name is None:
            raise XanoError("A API não informou o nome de um vendedor.")
        quantity = next(
            (
                row.get(key)
                for key in ("total_vendas", "quantidade", "count", "qtd")
                if row.get(key) is not None
            ),
            0,
        )
        rows.append({"nome": str(name), "quantidade": int(_count(quantity, "vendas por vendedor"))})
    return sorted(rows, key=lambda row: row["quantidade"], reverse=True)


def _filter_options(
    value: Any,
    label: str,
    *,
    id_keys: tuple[str, ...],
    name_keys: tuple[str, ...],
) -> list[dict[str, str]]:
    if value is None:
        return []
    if isinstance(value, dict):
        for key in ("items", "data", "results", "rows"):
            nested = value.get(key)
            if isinstance(nested, list):
                value = nested
                break
    if not isinstance(value, list):
        raise XanoError(f"A API retornou uma lista inválida para opções de {label}.")

    options = []
    for row in value:
        if not isinstance(row, dict):
            raise XanoError(f"A API retornou uma opção inválida para {label}.")
        option_id = next((row.get(key) for key in id_keys if row.get(key) is not None), None)
        name = next((row.get(key) for key in name_keys if row.get(key) is not None), None)
        if option_id is None or name is None or not str(name).strip():
            raise XanoError(f"A API não informou o identificador ou nome de {label}.")
        options.append({"id": str(option_id), "nome": str(name).strip()})
    return options


def _sales_status_rows(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if isinstance(value, dict):
        for key in ("items", "data", "results", "rows", "vendas_por_status_pagamento"):
            nested = value.get(key)
            if isinstance(nested, list):
                value = nested
                break
    if not isinstance(value, list):
        raise XanoError("A API retornou uma lista inválida para vendas por status.")

    rows = []
    for row in value:
        if not isinstance(row, dict):
            raise XanoError("A API retornou um registro inválido para vendas por status.")
        name = row.get("descricao") or row.get("Descricao_venda") or row.get("status")
        if name is None:
            raise XanoError("A API não informou a descrição de um status de venda.")
        count = next(
            (
                row.get(key)
                for key in ("total_vendas", "quantidade", "count", "qtd")
                if row.get(key) is not None
            ),
            0,
        )
        result = {
            "nome": str(name),
            "quantidade": _count(count, "vendas por status"),
            "valor_total": "",
        }
        amount = row.get("valor_total")
        if amount is not None:
            result["valor_total"] = _currency(amount, "valor por status")
        rows.append(result)
    return rows


def _extract_kpis(result: dict[str, Any]) -> dict[str, Any]:
    kpis = result.get("kpis")
    if isinstance(kpis, dict):
        return kpis
    return result


def _extract_series(result: dict[str, Any], *keys: str) -> Any:
    containers: list[Any] = [result]
    for key in ("data", "result", "payload", "response"):
        nested = result.get(key)
        if isinstance(nested, dict):
            containers.append(nested)
            for nested_key in ("data", "result", "payload"):
                deeper = nested.get(nested_key)
                if isinstance(deeper, dict):
                    containers.append(deeper)
    for container in containers:
        for key in keys:
            if key in container:
                return container[key]
    return None


def _trend_chart_rows(value: Any, period: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        for key in ("items", "data", "vendas", "vendas_timeline", "results"):
            nested = value.get(key)
            if isinstance(nested, list):
                value = nested
                break
    if not isinstance(value, list):
        raise XanoError("A API retornou uma lista inválida para vendas por período.")

    grouped: dict[str, dict[str, Any]] = {}
    for row in value:
        if not isinstance(row, dict):
            raise XanoError("A API retornou um registro inválido para vendas por período.")
        raw_period = _timeline_date(row)
        normalized_period = _normalize_timeline_date(raw_period)
        if normalized_period is None:
            keys = ", ".join(str(key) for key in row.keys()) or "nenhuma"
            raise XanoError(
                "A API não informou uma data válida para a série de vendas. "
                f"Campos recebidos: {keys}."
            )
        try:
            current_date = date.fromisoformat(normalized_period[:10])
        except ValueError as exc:
            raise XanoError("A API retornou uma data inválida para vendas por período.") from exc

        if period == "semana":
            year, week, _ = current_date.isocalendar()
            label = f"{year}-S{week:02d}"
        elif period == "mes":
            label = current_date.strftime("%Y-%m")
        elif period == "ano":
            label = str(current_date.year)
        else:
            label = current_date.isoformat()

        bucket = grouped.setdefault(
            label, {"periodo": label, "total_vendas": 0, "valor_total": 0.0}
        )
        quantity = row.get("total_vendas", 1)
        amount = _timeline_value(row)
        bucket["total_vendas"] += int(_count(quantity, "vendas"))
        bucket["valor_total"] += float(_decimal(amount, "valor vendido"))
    return [
        {
            **grouped[key],
            "valor_total": _rounded_number(grouped[key]["valor_total"], "valor vendido"),
        }
        for key in sorted(grouped)
    ]


def _timeline_chart_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **row,
            "periodo_formatado": _format_timeline_period(row["periodo"]),
        }
        for row in rows
    ]


def _format_timeline_period(periodo: Any) -> str:
    value = str(periodo)
    try:
        if len(value) == 7:
            return date.fromisoformat(f"{value}-01").strftime("%d/%m/%Y")
        if len(value) == 4:
            return date.fromisoformat(f"{value}-01-01").strftime("%d/%m/%Y")
        return date.fromisoformat(value[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return value


def _timeline_date(row: dict[str, Any]) -> Any:
    for key in (
        "periodo",
        "data_venda",
        "data",
        "date",
        "created_at",
        "timestamp",
    ):
        value = row.get(key)
        if value is not None and value != "":
            return value
    for key in ("venda", "sale", "item", "record"):
        nested = row.get(key)
        if isinstance(nested, dict):
            found = _timeline_date(nested)
            if found:
                return found
    return None


def _normalize_timeline_date(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(value / 1000 if value > 10_000_000_000 else value, timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, dict):
        for key in ("value", "timestamp", "date", "datetime", "iso"):
            if key in value:
                normalized = _normalize_timeline_date(value[key])
                if normalized:
                    return normalized
    return None


def _timeline_value(row: dict[str, Any]) -> Any:
    for key in ("valor_total", "Valor_final", "valor", "value"):
        if key in row and row[key] is not None:
            return row[key]
    for key in ("venda", "sale", "item", "record"):
        nested = row.get(key)
        if isinstance(nested, dict):
            value = _timeline_value(nested)
            if value != 0:
                return value
    return 0


def _chart_rows(
    value: Any,
    label: str,
    *,
    name_key: str,
    value_key: str,
    secondary_value_key: str | None = None,
    max_categories: int | None = 8,
) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        for key in ("items", "data", "results", "rows"):
            nested = value.get(key)
            if isinstance(nested, list):
                value = nested
                break
    if not isinstance(value, list):
        raise XanoError(f"A API retornou uma lista inválida para {label}.")
    rows = []
    for row in value:
        if not isinstance(row, dict):
            raise XanoError(f"A API retornou um registro inválido para {label}.")
        name = row.get(name_key)
        if name is None and name_key == "metodo":
            name = (
                row.get("Metodo")
                or row.get("forma_pagamento")
                or row.get("forma")
                or row.get("nome")
                or row.get("descricao")
            )
            if isinstance(name, dict):
                name = (
                    name.get("metodo")
                    or name.get("Metodo")
                    or name.get("nome")
                    or name.get("Metodo_nome")
                )
        if name is None and name_key == "descricao":
            name = row.get("Descricao") or row.get("status") or row.get("nome")
        if name is None and name_key == "marca":
            name = row.get("Marca") or row.get("nome") or row.get("marca_nome")
        if name is None:
            raise XanoError(f"A API não informou a categoria de {label}.")
        amount_value = row.get(value_key)
        if amount_value is None:
            amount_value = next(
                (
                    row.get(key)
                    for key in ("quantidade", "total", "count", "qtd", "valor")
                    if row.get(key) is not None
                ),
                0,
            )
        amount = _decimal(amount_value, label)
        chart_row = {"nome": str(name), "quantidade": float(amount)}
        if secondary_value_key is not None:
            secondary_value = row.get(secondary_value_key)
            if secondary_value is None:
                secondary_value = next(
                    (
                        row[key]
                        for key in ("valor", "valor_total")
                        if row.get(key) is not None
                    ),
                    None,
                )
            if secondary_value is not None:
                chart_row["valor_total"] = _rounded_number(secondary_value, label)
        rows.append(chart_row)
    rows.sort(key=lambda row: row["quantidade"], reverse=True)
    if max_categories is not None and len(rows) > max_categories:
        rows = rows[: max_categories - 1] + [
            {
                "nome": "Outros",
                "quantidade": sum(
                    row["quantidade"] for row in rows[max_categories - 1 :]
                ),
                **(
                    {
                        "valor_total": sum(
                            row.get("valor_total", 0)
                            for row in rows[max_categories - 1 :]
                        )
                    }
                    if secondary_value_key is not None
                    else {}
                ),
            }
        ]
    return rows


_CHART_COLORS = (
    "#60a5fa",
    "#2dd4bf",
    "#c4b5fd",
    "#fbbf24",
    "#93c5fd",
    "#67e8f9",
)


def _color_chart_rows(
    rows: list[dict[str, Any]], category_ids: dict[str, str] | None = None
) -> list[dict[str, Any]]:
    return [
        {
            **row,
            "cor": _CHART_COLORS[
                int.from_bytes(
                    hashlib.sha256(
                        str(row.get("id", (category_ids or {}).get(row["nome"], row["nome"]))).encode("utf-8")
                    ).digest()[:4],
                    "big",
                )
                % len(_CHART_COLORS)
            ],
        }
        for row in rows
    ]


def _vehicle_status_chart_rows(value: Any) -> list[dict[str, Any]]:
    rows = _chart_rows(
        value,
        "veículos por status",
        name_key="descricao",
        value_key="quantidade",
    )
    for row in rows:
        row["cor"] = vehicle_status_chart_color(row["nome"])
    return rows


def _has_chart_values(rows: list[dict[str, Any]]) -> bool:
    return any(row.get("quantidade", 0) > 0 for row in rows)


def _payment_chart_rows(value: Any) -> list[dict[str, Any]]:
    rows = _chart_rows(
        value,
        "vendas por forma de pagamento",
        name_key="metodo",
        value_key="total_vendas",
    )
    return [row for row in rows if row["quantidade"] > 0]


def _normalize_low_stock_rows(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        for key in ("items", "data", "results", "rows", "pecas_baixo_estoque"):
            nested = value.get(key)
            if isinstance(nested, list):
                value = nested
                break
    if not isinstance(value, list):
        raise XanoError("A API retornou uma lista inválida para peças com estoque baixo.")

    rows: list[dict[str, Any]] = []
    for row in value:
        if not isinstance(row, dict):
            raise XanoError("A API retornou um registro inválido para peças com estoque baixo.")
        name = row.get("nome") or row.get("PCNome") or row.get("name")
        if name is None:
            raise XanoError("A API não informou o nome de uma peça com estoque baixo.")
        quantity = row.get("quantidade", row.get("qtd_disp", 0))
        rows.append(
            {
                "id": row.get("id"),
                "nome": str(name),
                "quantidade": float(_decimal(quantity or 0, "quantidade de estoque")),
                "valor_unitario": float(_decimal(
                    row.get("valor_unitario", row.get("PCvalor", 0)) or 0,
                    "valor unitário da peça",
                )),
            }
        )
    return rows


def _low_stock_labels(rows: list[dict[str, Any]]) -> list[str]:
    labels = []
    for row in rows:
        quantity = row["quantidade"]
        quantity_label = "Sem estoque" if quantity == 0 else f"Quantidade: {quantity:g}"
        labels.append(f"{row['nome']} — {quantity_label}")
    return labels


def _build_params(
    data_inicio: str,
    data_fim: str,
    *,
    is_manager: bool,
    status_id: str = "",
    vendedor_id: str = "",
    forma_pagamento_id: str = "",
    tipo_item: str = "",
    status_veiculo_id: str = "",
) -> dict[str, str | int]:
    params: dict[str, str | int] = {}
    if data_inicio.strip():
        params["data_inicio"] = data_inicio.strip()
    if data_fim.strip():
        params["data_fim"] = data_fim.strip()
    if not is_manager:
        return params

    for key, raw_value in (
        ("status_id", status_id),
        ("vendedor_id", vendedor_id),
        ("forma_pagamento_id", forma_pagamento_id),
        ("status_veiculo_id", status_veiculo_id),
    ):
        if raw_value.strip() and raw_value.strip().casefold() != "todos":
            try:
                value = int(raw_value)
            except ValueError as exc:
                raise XanoError(f"O filtro {key} deve ser um número inteiro positivo.") from exc
            if value < 1:
                raise XanoError(f"O filtro {key} deve ser um número inteiro positivo.")
            params[key] = value

    if tipo_item and tipo_item.strip().casefold() != "todos":
        if tipo_item not in ("veiculo", "peca"):
            raise XanoError("O tipo de item deve ser Veículo ou Peça.")
        params["tipo_item"] = tipo_item
    return params


class DashboardState(rx.State):
    data_inicio: str = date.today().replace(day=1).isoformat()
    data_fim: str = date.today().isoformat()
    loading: bool = False
    error: str = ""
    valor_liquido: str = "—"
    total_vendas: str = "—"
    vendas_pagas: str = "—"
    ticket_medio: str = "—"
    valor_bruto: str = "—"
    vendas_canceladas: str = "—"
    percentual_canceladas: str = "—"
    veiculos_disponiveis: str = "—"
    valor_veiculos: str = "—"
    pecas_disponiveis: str = "—"
    valor_estoque_pecas: str = "—"
    pecas_sem_estoque: str = "—"
    pecas_baixo_estoque: list[dict] = []
    pecas_baixo_estoque_labels: list[str] = []
    veiculos_vendidos_por_marca: list[str] = []
    chart_veiculos_vendidos_por_marca: list[dict] = []
    chart_pecas_vendidas_por_categoria: list[dict] = []
    pecas_vendidas_por_categoria: list[str] = []
    conversao_estoque: list[str] = []
    giro_estoque: list[str] = []
    vendas_por_periodo: list[str] = []
    chart_vendas_por_periodo: list[dict] = []
    chart_formas_pagamento: list[dict] = []
    chart_mix_itens: list[dict] = []
    chart_veiculos_por_status: list[dict] = []
    pagamentos_com_movimento: bool = False
    mix_com_movimento: bool = False
    estoque_com_movimento: bool = False
    timeline_rows: list[dict] = []
    vendas_por_status: list[dict[str, str]] = []
    vendas_por_pagamento: list[str] = []
    vendas_por_vendedor: list[dict] = []
    status_venda_opcoes: list[dict] = []
    vendedor_opcoes: list[dict] = []
    forma_pagamento_opcoes: list[dict] = []
    status_veiculo_opcoes: list[dict] = []
    filtro_vendedor_nome: str = ""
    mix_itens: list[str] = []
    veiculos_por_status: list[str] = []
    filtro_status_id: str = "todos"
    filtro_vendedor_id: str = "todos"
    filtro_forma_pagamento_id: str = "todos"
    filtro_tipo_item: str = "todos"
    filtro_status_veiculo_id: str = "todos"
    periodo_ativo: str = "dia"

    def set_data_inicio(self, value: str) -> None:
        self.data_inicio = value

    def set_data_fim(self, value: str) -> None:
        self.data_fim = value

    def set_filtro_status_id(self, value: str) -> None:
        self.filtro_status_id = value

    def set_filtro_vendedor_id(self, value: str) -> None:
        self.filtro_vendedor_id = value

    def set_filtro_vendedor_nome(self, value: str) -> None:
        self.filtro_vendedor_nome = value

    @rx.var
    def vendedores_visiveis(self) -> list[str]:
        search = self.filtro_vendedor_nome.strip().casefold()
        return [
            f"{row['nome']} — {row['quantidade']} "
            f"{'venda' if row['quantidade'] == 1 else 'vendas'}"
            for row in self.vendas_por_vendedor
            if not search or search in row["nome"].casefold()
        ]

    def set_filtro_forma_pagamento_id(self, value: str) -> None:
        self.filtro_forma_pagamento_id = value

    def set_filtro_tipo_item(self, value: str) -> None:
        self.filtro_tipo_item = value

    def set_filtro_status_veiculo_id(self, value: str) -> None:
        self.filtro_status_veiculo_id = value

    async def set_periodo(self, value: str) -> None:
        if value not in ("dia", "semana", "mes", "ano"):
            raise XanoError("Selecione um período válido para o gráfico.")
        self.periodo_ativo = value
        if self.timeline_rows:
            self.chart_vendas_por_periodo = _timeline_chart_rows(
                _trend_chart_rows(self.timeline_rows, self.periodo_ativo)
            )
            return
        await self.load()

    def _clear_metrics(self) -> None:
        self.valor_liquido = "—"
        self.total_vendas = "—"
        self.vendas_pagas = "—"
        self.ticket_medio = "—"
        self.valor_bruto = "—"
        self.vendas_canceladas = "—"
        self.percentual_canceladas = "—"
        self.veiculos_disponiveis = "—"
        self.valor_veiculos = "—"
        self.pecas_disponiveis = "—"
        self.valor_estoque_pecas = "—"
        self.pecas_sem_estoque = "—"
        self.pecas_baixo_estoque = []
        self.pecas_baixo_estoque_labels = []
        self.veiculos_vendidos_por_marca = []
        self.chart_veiculos_vendidos_por_marca = []
        self.chart_pecas_vendidas_por_categoria = []
        self.pecas_vendidas_por_categoria = []
        self.conversao_estoque = []
        self.giro_estoque = []
        self.vendas_por_periodo = []
        self.chart_vendas_por_periodo = []
        self.chart_formas_pagamento = []
        self.chart_mix_itens = []
        self.chart_veiculos_por_status = []
        self.pagamentos_com_movimento = False
        self.mix_com_movimento = False
        self.estoque_com_movimento = False
        self.timeline_rows = []
        self.vendas_por_status = []
        self.vendas_por_pagamento = []
        self.vendas_por_vendedor = []
        self.mix_itens = []
        self.veiculos_por_status = []
        self.status_venda_opcoes = []
        self.vendedor_opcoes = []
        self.forma_pagamento_opcoes = []
        self.status_veiculo_opcoes = []
        self.vendas_por_periodo = []
        self.vendas_por_status = []
        self.vendas_por_pagamento = []
        self.vendas_por_vendedor = []
        self.mix_itens = []
        self.veiculos_por_status = []

    async def load(self) -> AsyncIterator[None]:
        self.loading, self.error = True, ""
        self._clear_metrics()
        # Flush the loading state before awaiting I/O, so old results are not
        # presented as a completed refresh and the action is disabled in time.
        yield
        try:
            start = date.fromisoformat(self.data_inicio)
            end = date.fromisoformat(self.data_fim)
            if start > end:
                raise XanoError("A data inicial não pode ser posterior à data final.")

            auth_state = await self.get_state(AuthState)
            if not auth_state.token:
                raise XanoError("Entre com sua conta para consultar os indicadores.")
            params = _build_params(
                self.data_inicio,
                self.data_fim,
                is_manager=auth_state.is_manager,
                status_id=self.filtro_status_id,
                vendedor_id=self.filtro_vendedor_id,
                forma_pagamento_id=self.filtro_forma_pagamento_id,
                tipo_item=self.filtro_tipo_item,
                status_veiculo_id=self.filtro_status_veiculo_id,
            )
            result = await client.async_request(
                "GET",
                "/gerenciamento/indicadores",
                token=auth_state.token,
                params=params,
            )
            if not isinstance(result, dict):
                raise XanoError("A API de indicadores retornou uma resposta inválida.")
            if isinstance(result.get("data"), dict):
                nested_result = result["data"]
                result = {**nested_result, **result}
                if "kpis" not in result and isinstance(nested_result.get("kpis"), dict):
                    result["kpis"] = nested_result["kpis"]

            kpis = _extract_kpis(result)
            required_kpis = [
                "total_vendas_periodo",
                "valor_liquido_recebido_periodo",
                "vendas_pagas",
                "valor_bruto_vendido",
                "vendas_canceladas",
                "percentual_vendas_canceladas",
            ]
            if auth_state.is_manager:
                required_kpis.extend(("veiculos_disponiveis", "pecas_qtd_disponivel"))
            missing = [key for key in required_kpis if key not in kpis]
            if missing:
                raise XanoError(
                    "A resposta da API não contém os indicadores obrigatórios: "
                    + ", ".join(missing)
                    + "."
                )

            self.valor_liquido = _currency(
                kpis["valor_liquido_recebido_periodo"], "valor líquido"
            )
            total_vendas = kpis["total_vendas_periodo"]
            self.total_vendas = _count(total_vendas, "vendas no período")
            self.vendas_pagas = _count(kpis["vendas_pagas"], "vendas pagas")
            self.valor_bruto = _currency(
                kpis["valor_bruto_vendido"], "valor bruto vendido"
            )
            self.ticket_medio = _average_currency(
                kpis["valor_bruto_vendido"],
                total_vendas,
                "vendas no período",
            )
            self.vendas_canceladas = _count(
                kpis["vendas_canceladas"], "vendas canceladas"
            )
            self.percentual_canceladas = _percentage(
                kpis["percentual_vendas_canceladas"], "percentual de vendas canceladas"
            )
            low_stock = _extract_series(result, "pecas_baixo_estoque")
            self.pecas_baixo_estoque = _normalize_low_stock_rows(low_stock)
            self.pecas_baixo_estoque_labels = _low_stock_labels(
                self.pecas_baixo_estoque
            )
            marcas_vendidas = _extract_series(result, "veiculos_vendidos_por_marca")
            self.veiculos_vendidos_por_marca = _analysis_rows(
                marcas_vendidas,
                "veículos vendidos por marca",
            )
            self.chart_veiculos_vendidos_por_marca = [
                {**row, "cor": "#60a5fa"}
                for row in _chart_rows(
                    marcas_vendidas,
                    "veículos vendidos por marca",
                    name_key="marca",
                    value_key="quantidade",
                    max_categories=None,
                )
            ]
            categorias_vendidas = _extract_series(
                result, "pecas_vendidas_por_categoria"
            )
            self.pecas_vendidas_por_categoria = _analysis_rows(
                categorias_vendidas,
                "peças vendidas por categoria",
            )
            self.chart_pecas_vendidas_por_categoria = [
                {
                    **row,
                    "cor": "#60a5fa",
                    "valor_formatado": _currency(row["valor_total"], "valor de peças")
                    if "valor_total" in row
                    else "",
                }
                for row in _chart_rows(
                    categorias_vendidas,
                    "peças vendidas por categoria",
                    name_key="categoria",
                    value_key="quantidade",
                    secondary_value_key="valor_total",
                    max_categories=None,
                )
            ]
            self.conversao_estoque = _analysis_rows(
                _extract_series(result, "conversao_estoque"),
                "conversão de estoque",
            )
            self.giro_estoque = _analysis_rows(
                _extract_series(result, "giro_estoque"),
                "giro de estoque",
            )
            if auth_state.is_manager:
                self.veiculos_disponiveis = _count(
                    kpis["veiculos_disponiveis"], "veículos disponíveis"
                )
                self.pecas_disponiveis = _count(
                    kpis["pecas_qtd_disponivel"], "peças disponíveis"
                )
                self.valor_veiculos = (
                    _currency(result["valor_veiculos_disponiveis"], "valor de veículos")
                    if "valor_veiculos_disponiveis" in result
                    else "—"
                )
                self.valor_estoque_pecas = (
                    _currency(
                        result["valor_estoque_pecas"], "valor do estoque de peças"
                    )
                    if "valor_estoque_pecas" in result
                    else "—"
                )
                self.pecas_sem_estoque = (
                    _count(result["pecas_sem_estoque"], "peças sem estoque")
                    if "pecas_sem_estoque" in result
                    else "—"
                )
            timeline_rows = _extract_series(result, "vendas_timeline")
            if timeline_rows is None:
                timeline_rows = _extract_series(result, "vendas_por_periodo")
            self.timeline_rows = (
                timeline_rows if isinstance(timeline_rows, list) else []
            )
            self.vendas_por_periodo = _report_rows(timeline_rows, "vendas por período")
            self.chart_vendas_por_periodo = _timeline_chart_rows(
                _trend_chart_rows(timeline_rows, self.periodo_ativo)
            )
            status_sales = _extract_series(
                result, "vendas_por_status_pagamento", "vendas_por_status"
            )
            self.status_venda_opcoes = _filter_options(
                status_sales,
                "status da venda",
                id_keys=("status_id", "id"),
                name_keys=("descricao", "Descricao_venda", "status"),
            )
            self.vendas_por_status = _sales_status_rows(status_sales)
            self.vendas_por_pagamento = _report_rows(
                _extract_series(
                    result,
                    "vendas_por_forma_pagamento",
                    "vendas_por_metodo_pagamento",
                    "pagamentos",
                ),
                "vendas por forma de pagamento",
            )
            self.chart_formas_pagamento = _payment_chart_rows(
                _extract_series(
                    result,
                    "vendas_por_forma_pagamento",
                    "vendas_por_metodo_pagamento",
                    "pagamentos",
                )
            )
            payment_rows = _extract_series(
                result,
                "vendas_por_forma_pagamento",
                "vendas_por_metodo_pagamento",
                "pagamentos",
            )
            self.forma_pagamento_opcoes = _filter_options(
                payment_rows,
                "forma de pagamento",
                id_keys=("forma_id", "forma_pagamento_id", "id"),
                name_keys=("metodo", "Metodo", "nome"),
            )
            self.chart_formas_pagamento = _color_chart_rows(
                self.chart_formas_pagamento,
                {option["nome"]: option["id"] for option in self.forma_pagamento_opcoes},
            )
            self.pagamentos_com_movimento = len(self.chart_formas_pagamento) > 0
            mix_rows = _extract_series(result, "mix_itens", "vendas_por_tipo_item")
            self.mix_itens = _report_rows(mix_rows, "mix de itens")
            self.chart_mix_itens = _chart_rows(
                mix_rows,
                "mix de itens",
                name_key="tipo",
                value_key="quantidade",
            )
            self.mix_com_movimento = _has_chart_values(self.chart_mix_itens)
            if auth_state.is_manager:
                self.vendas_por_vendedor = _salesperson_rows(
                    _extract_series(result, "vendas_por_vendedor")
                )
                self.vendedor_opcoes = _filter_options(
                    _extract_series(result, "vendas_por_vendedor"),
                    "vendedor",
                    id_keys=("vendedor_id", "id"),
                    name_keys=("nome", "UNome", "name", "vendedor"),
                )
                self.veiculos_por_status = _report_rows(
                    _extract_series(
                        result, "veiculos_por_status", "estoque_veiculos_por_status"
                    ),
                    "veículos por status",
                )
                self.chart_veiculos_por_status = _vehicle_status_chart_rows(
                    _extract_series(
                        result, "veiculos_por_status", "estoque_veiculos_por_status"
                    )
                )
                self.status_veiculo_opcoes = _filter_options(
                    _extract_series(
                        result, "veiculos_por_status", "estoque_veiculos_por_status"
                    ),
                    "status do veículo",
                    id_keys=("status_id", "id"),
                    name_keys=("descricao", "Descricao", "status", "nome"),
                )
                self.estoque_com_movimento = _has_chart_values(
                    self.chart_veiculos_por_status
                )
        except (XanoError, ValueError) as exc:
            self._clear_metrics()
            self.error = str(exc)
        finally:
            self.loading = False

    def export_csv(self) -> rx.event.EventSpec:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(("Métrica", "Valor"))
        writer.writerows(
            (
                ("Data inicial", self.data_inicio),
                ("Data final", self.data_fim),
                ("Vendas no período", self.total_vendas),
                ("Vendas pagas", self.vendas_pagas),
                ("Valor líquido recebido", self.valor_liquido),
                ("Ticket médio", self.ticket_medio),
                ("Valor bruto vendido", self.valor_bruto),
                ("Vendas canceladas", self.vendas_canceladas),
                ("Percentual de cancelamentos", self.percentual_canceladas),
            )
        )
        return rx.download(
            data="\ufeff" + output.getvalue(),
            filename="dashboard-vendas.csv",
            mime_type="text/csv;charset=utf-8",
        )
