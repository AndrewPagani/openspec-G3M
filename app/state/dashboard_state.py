from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import reflex as rx

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
    params: dict[str, str | int] = {"data_inicio": data_inicio, "data_fim": data_fim}
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
            result = client.request(
                "GET",
                "/gerenciamento/indicadores",
                token=auth_state.token,
                params=params,
            )
            if not isinstance(result, dict):
                raise XanoError("A API de indicadores retornou uma resposta inválida.")
            if "kpis" not in result and isinstance(result.get("data"), dict):
                result = result["data"]

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
            self.vendas_por_periodo = _report_rows(result.get("vendas_por_periodo"), "vendas por período")
            self.vendas_por_status = _report_rows(
                result.get("vendas_por_status_pagamento"), "vendas por status"
            )
            self.vendas_por_pagamento = _report_rows(
                result.get("vendas_por_forma_pagamento"), "vendas por forma de pagamento"
            )
            self.mix_itens = _report_rows(result.get("mix_itens"), "mix de itens")
            if auth_state.is_manager:
                self.vendas_por_vendedor = _report_rows(
                    result.get("vendas_por_vendedor"), "vendas por vendedor"
                )
                self.veiculos_por_status = _report_rows(
                    result.get("veiculos_por_status"), "veículos por status"
                )
        except (XanoError, ValueError) as exc:
            self._clear_metrics()
            self.error = str(exc)
        finally:
            self.loading = False
