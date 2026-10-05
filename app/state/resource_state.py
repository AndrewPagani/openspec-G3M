from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import reflex as rx

from app.services.xano_client import XanoError, client
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
            "Imagem_url",
            "imagem_url",
            "image_url",
            "Imagem",
            "imagem",
            "image",
        )
        price = _first_value(record, "Preco", "preco", "price")
        normalized["_vehicle_name"] = " ".join(part for part in (make, model) if part)
        year = _first_value(record, "Ano", "ano", "year")
        normalized["_vehicle_year"] = year
        normalized["_vehicle_year_display"] = f"Ano: {year or 'Não informado'}"
        normalized["_vehicle_price"] = _format_vehicle_price(price)
        normalized["_vehicle_price_display"] = f"Valor: {normalized['_vehicle_price']}"
        normalized["_image_url"] = image_url
    return normalized


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
            result = client.request("GET", endpoint, token=auth_state.token)
            if isinstance(result, list):
                records = result
            elif isinstance(result, dict):
                records = result.get("items", result.get("data", []))
            else:
                raise XanoError("A API retornou uma resposta inválida para a listagem.")
            if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
                raise XanoError("A API retornou registros em formato inválido para a listagem.")
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
