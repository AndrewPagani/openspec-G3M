from __future__ import annotations

import csv
import io
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
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


def _currency(value: Any, label: str) -> str:
    amount = _decimal(value, label)
    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


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
                elif any(
                    term in normalized_key
                    for term in ("valor", "bruto", "liquido", "total", "ticket", "desconto")
                ):
                    item = _currency(item, title)
            columns.append(f"{title}: {item}")
        rows.append(" · ".join(columns) or "Registro disponível")
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
    return [grouped[key] for key in sorted(grouped)]


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


def _chart_rows(value: Any, label: str, *, name_key: str, value_key: str) -> list[dict[str, Any]]:
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
            name = row.get("Metodo") or row.get("forma_pagamento") or row.get("nome")
        if name is None and name_key == "descricao":
            name = row.get("Descricao") or row.get("status") or row.get("nome")
        if name is None:
            raise XanoError(f"A API não informou a categoria de {label}.")
        amount_value = row.get(value_key)
        if amount_value is None:
            amount_value = row.get("quantidade", row.get("total", 0))
        amount = _decimal(amount_value, label)
        rows.append({"nome": str(name), "quantidade": float(amount)})
    rows.sort(key=lambda row: row["quantidade"], reverse=True)
    if len(rows) > 8:
        rows = rows[:7] + [
            {"nome": "Outros", "quantidade": sum(row["quantidade"] for row in rows[7:])}
        ]
    return rows


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
        if raw_value.strip():
            try:
                value = int(raw_value)
            except ValueError as exc:
                raise XanoError(f"O filtro {key} deve ser um número inteiro positivo.") from exc
            if value < 1:
                raise XanoError(f"O filtro {key} deve ser um número inteiro positivo.")
            params[key] = value

    if tipo_item:
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
    descontos: str = "—"
    valor_bruto: str = "—"
    vendas_canceladas: str = "—"
    percentual_canceladas: str = "—"
    veiculos_disponiveis: str = "—"
    valor_veiculos: str = "—"
    pecas_disponiveis: str = "—"
    valor_estoque_pecas: str = "—"
    pecas_sem_estoque: str = "—"
    vendas_por_periodo: list[str] = []
    chart_vendas_por_periodo: list[dict] = []
    chart_formas_pagamento: list[dict] = []
    chart_mix_itens: list[dict] = []
    chart_veiculos_por_status: list[dict] = []
    pagamentos_com_movimento: bool = False
    mix_com_movimento: bool = False
    estoque_com_movimento: bool = False
    timeline_rows: list[dict] = []
    vendas_por_status: list[str] = []
    vendas_por_pagamento: list[str] = []
    vendas_por_vendedor: list[str] = []
    mix_itens: list[str] = []
    veiculos_por_status: list[str] = []
    filtro_status_id: str = ""
    filtro_vendedor_id: str = ""
    filtro_forma_pagamento_id: str = ""
    filtro_tipo_item: str = ""
    filtro_status_veiculo_id: str = ""
    periodo_ativo: str = "dia"

    def set_data_inicio(self, value: str) -> None:
        self.data_inicio = value

    def set_data_fim(self, value: str) -> None:
        self.data_fim = value

    def set_filtro_status_id(self, value: str) -> None:
        self.filtro_status_id = value

    def set_filtro_vendedor_id(self, value: str) -> None:
        self.filtro_vendedor_id = value

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
            self.chart_vendas_por_periodo = _trend_chart_rows(
                self.timeline_rows, self.periodo_ativo
            )
            return
        await self.load()

    def _clear_metrics(self) -> None:
        self.valor_liquido = "—"
        self.total_vendas = "—"
        self.vendas_pagas = "—"
        self.ticket_medio = "—"
        self.descontos = "—"
        self.valor_bruto = "—"
        self.vendas_canceladas = "—"
        self.percentual_canceladas = "—"
        self.veiculos_disponiveis = "—"
        self.valor_veiculos = "—"
        self.pecas_disponiveis = "—"
        self.valor_estoque_pecas = "—"
        self.pecas_sem_estoque = "—"
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
        self.vendas_por_periodo = []
        self.vendas_por_status = []
        self.vendas_por_pagamento = []
        self.vendas_por_vendedor = []
        self.mix_itens = []
        self.veiculos_por_status = []

    async def load(self) -> None:
        self.loading, self.error = True, ""
        self._clear_metrics()
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
                "valor_liquido_recebido_periodo",
                "vendas_pagas",
                "ticket_medio_vendas_pagas",
                "descontos",
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

            self.valor_liquido = _currency(kpis["valor_liquido_recebido_periodo"], "valor líquido")
            total_vendas = kpis.get("total_vendas_periodo")
            self.total_vendas = (
                _count(total_vendas, "vendas no período") if total_vendas is not None else "—"
            )
            self.vendas_pagas = _count(kpis["vendas_pagas"], "vendas pagas")
            self.ticket_medio = _currency(kpis["ticket_medio_vendas_pagas"], "ticket médio")
            self.descontos = _currency(kpis["descontos"], "descontos")
            self.valor_bruto = _currency(kpis["valor_bruto_vendido"], "valor bruto vendido")
            self.vendas_canceladas = _count(kpis["vendas_canceladas"], "vendas canceladas")
            self.percentual_canceladas = _percentage(
                kpis["percentual_vendas_canceladas"], "percentual de vendas canceladas"
            )
            if auth_state.is_manager:
                self.veiculos_disponiveis = _count(kpis["veiculos_disponiveis"], "veículos disponíveis")
                self.pecas_disponiveis = _count(kpis["pecas_qtd_disponivel"], "peças disponíveis")
                self.valor_veiculos = (
                    _currency(result["valor_veiculos_disponiveis"], "valor de veículos")
                    if "valor_veiculos_disponiveis" in result
                    else "—"
                )
                self.valor_estoque_pecas = (
                    _currency(result["valor_estoque_pecas"], "valor do estoque de peças")
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
            self.timeline_rows = timeline_rows if isinstance(timeline_rows, list) else []
            self.vendas_por_periodo = _report_rows(timeline_rows, "vendas por período")
            self.chart_vendas_por_periodo = _trend_chart_rows(
                timeline_rows, self.periodo_ativo
            )
            self.vendas_por_status = _report_rows(
                _extract_series(result, "vendas_por_status_pagamento", "vendas_por_status"),
                "vendas por status",
            )
            self.vendas_por_pagamento = _report_rows(
                _extract_series(
                    result,
                    "vendas_por_forma_pagamento",
                    "vendas_por_metodo_pagamento",
                    "pagamentos",
                ),
                "vendas por forma de pagamento",
            )
            self.chart_formas_pagamento = _chart_rows(
                _extract_series(
                    result,
                    "vendas_por_forma_pagamento",
                    "vendas_por_metodo_pagamento",
                    "pagamentos",
                ),
                "vendas por forma de pagamento",
                name_key="metodo",
                value_key="total_vendas",
            )
            self.pagamentos_com_movimento = _has_chart_values(self.chart_formas_pagamento)
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
                self.vendas_por_vendedor = _report_rows(
                    _extract_series(result, "vendas_por_vendedor"), "vendas por vendedor"
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
                ("Descontos", self.descontos),
                ("Vendas canceladas", self.vendas_canceladas),
                ("Percentual de cancelamentos", self.percentual_canceladas),
            )
        )
        return rx.download(
            data="\ufeff" + output.getvalue(),
            filename="dashboard-vendas.csv",
            mime_type="text/csv;charset=utf-8",
        )
