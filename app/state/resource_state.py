from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import reflex as rx

from app.services.xano_client import XanoError, client
from app.services.vehicle_status import vehicle_status_class
from app.state.auth_state import AuthState


def _first_value(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _format_vehicle_price(value: str) -> str:
    if not value:
        return "Valor não informado"
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return value
    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def _format_vehicle_mileage(value: str) -> str:
    if not value:
        return "Não informado"
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return value
    formatted = f"{amount:,.0f}".replace(",", ".")
    return formatted


def _format_part_quantity(value: str) -> str:
    if not value:
        return "0"
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return value
    return f"{amount:,.0f}".replace(",", ".")


def _parse_part_quantity(value: str) -> int:
    if not value:
        return 0
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation as exc:
        raise XanoError("A API retornou uma quantidade de peças inválida.") from exc
    if not amount.is_finite() or amount < 0 or amount != amount.to_integral_value():
        raise XanoError("A API retornou uma quantidade de peças inválida.")
    return int(amount)


def _normalize_record(record: dict[str, Any], endpoint: str) -> dict[str, Any]:
    normalized = dict(record)
    if endpoint == "/clientes":
        name = _first_value(record, "CNome", "Nome", "nome", "name")
        cpf = _first_value(record, "CPF", "cpf")
        normalized["_display_label"] = f"{name} - {cpf}" if cpf else name
    elif endpoint == "/veiculos":
        make = _first_value(record, "Marca", "marca")
        model = _first_value(record, "Modelo", "modelo")
        image_url = _first_value(
            record,
            "imagem_url",
            "image_url",
            "Imagem",
            "imagem",
            "image",
        )
        price = _first_value(record, "Preco", "preco", "valor", "price")
        normalized["_vehicle_name"] = " ".join(part for part in (make, model) if part)
        year = _first_value(record, "Ano", "ano", "year")
        normalized["_vehicle_year"] = year
        normalized["_vehicle_year_display"] = f"Ano: {year or 'Não informado'}"
        normalized["_vehicle_price"] = _format_vehicle_price(price)
        normalized["_vehicle_price_display"] = f"Valor: {normalized['_vehicle_price']}"
        normalized["_image_url"] = image_url
        mileage = _first_value(record, "Quilometragem", "quilometragem", "mileage")
        fuel = _first_value(
            record,
            "Combustivel",
            "Combustível",
            "combustivel",
            "combustível",
            "fuel",
        )
        normalized["_vehicle_mileage"] = _format_vehicle_mileage(mileage)
        normalized["_vehicle_fuel"] = fuel or "Não informado"
        status = _first_value(
            record, "status_descricao", "Status", "status"
        )
        normalized["_vehicle_status"] = status
        normalized["_vehicle_status_class"] = vehicle_status_class(status)
    elif endpoint == "/pecas":
        name = _first_value(record, "PCNome", "nome", "Nome", "name")
        price = _first_value(record, "PCvalor", "preco", "Preco", "valor", "price")
        quantity = _first_value(
            record,
            "qtd_disp",
            "quantidade_disponivel",
            "quantidade",
            "estoque",
        )
        area = _first_value(
            record,
            "area_secao",
            "area_nome",
            "Secao",
            "area",
        )
        image_url = _first_value(
            record,
            "imagem_url",
            "image_url",
            "Imagem",
            "imagem",
            "image",
        )
        quantity_display = _format_part_quantity(quantity)
        quantity_number = _parse_part_quantity(quantity)
        normalized["_part_name"] = name or "Peça sem nome"
        normalized["_part_price"] = _format_vehicle_price(price)
        normalized["_part_area"] = area or "Área não informada"
        normalized["_part_quantity"] = quantity_display
        normalized["_part_quantity_number"] = quantity_number
        normalized["_part_image_url"] = image_url
        normalized["_part_stock_class"] = (
            "stock-out"
            if quantity_number == 0
            else "stock-low"
            if quantity_number <= 5
            else "stock-available"
        )
    return normalized


def _records_from_response(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, list):
        records = result
    elif isinstance(result, dict):
        records = result.get("items", result.get("data", []))
    else:
        raise XanoError("A API retornou uma resposta inválida para a listagem.")
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise XanoError("A API retornou registros em formato inválido para a listagem.")
    return records


def _pagination_total_pages(pagination: Any, title: str) -> int:
    if not isinstance(pagination, dict):
        raise XanoError(
            f"A API retornou paginação inválida para a listagem de {title.lower()}."
        )

    raw_total_pages = pagination.get("total_pages", 1)
    if isinstance(raw_total_pages, bool):
        invalid = True
    elif isinstance(raw_total_pages, int):
        total_pages = raw_total_pages
        invalid = False
    elif isinstance(raw_total_pages, float):
        total_pages = int(raw_total_pages)
        invalid = not raw_total_pages.is_integer()
    elif isinstance(raw_total_pages, str):
        normalized = raw_total_pages.strip()
        try:
            total_pages = int(normalized)
            invalid = not normalized or str(total_pages) != normalized
        except ValueError:
            total_pages = 0
            invalid = True
    else:
        total_pages = 0
        invalid = True

    if invalid or total_pages < 1:
        raise XanoError(
            f"A API retornou paginação inválida para a listagem de {title.lower()}."
        )
    return total_pages


class ResourceState(rx.State):
    """Shared list state used by the operational screens."""

    records: list[dict] = []
    query: str = ""
    loading: bool = False
    error: str = ""
    endpoint: str = ""
    title: str = ""

    async def load(self, endpoint: str, title: str) -> None:
        self.endpoint, self.title = endpoint, title
        self.loading, self.error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            if endpoint in ("/veiculos", "/pecas"):
                result = client.request(
                    "GET",
                    endpoint,
                    token=auth_state.token,
                    params={"page": 1, "per_page": 100},
                )
                records = _records_from_response(result)
                pagination = result.get("pagination", {}) if isinstance(result, dict) else {}
                total_pages = _pagination_total_pages(pagination, title)
                for page in range(2, total_pages + 1):
                    page_result = client.request(
                        "GET",
                        endpoint,
                        token=auth_state.token,
                        params={"page": page, "per_page": 100},
                    )
                    records.extend(_records_from_response(page_result))
            else:
                result = client.request("GET", endpoint, token=auth_state.token)
                records = _records_from_response(result)
            self.records = [_normalize_record(row, endpoint) for row in records]
        except XanoError as exc:
            self.records, self.error = [], str(exc)
        finally:
            self.loading = False

    def set_query(self, value: str) -> None:
        self.query = value

    @rx.var
    def filtered_records(self) -> list[dict]:
        if not self.query:
            return self.records
        needle = self.query.lower()
        return [
            row for row in self.records
            if needle in " ".join(str(v) for v in row.values()).lower()
        ]
