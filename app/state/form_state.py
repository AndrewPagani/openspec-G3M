from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse

import reflex as rx

from app.services.xano_client import XanoError, client
from app.services.vehicle_status import vehicle_status_class
from app.state.auth_state import AuthState


def _validate_image_url(value: str) -> str:
    parsed_url = urlparse(value)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise XanoError("O campo URL da imagem precisa ser um endereço HTTP ou HTTPS válido.")
    return value


def _build_vehicle_payload(
    values: dict[str, str], statuses: list[dict[str, Any]]
) -> dict[str, str | int | float]:
    payload: dict[str, str | int | float] = {}
    fields = {
        "Marca": ("Marca", "text", True),
        "Modelo": ("Modelo", "text", True),
        "Cor": ("Cor", "text", True),
        "Ano": ("Ano", "int", True),
        "Placa": ("Placa", "text", False),
        "Chassi": ("Chassi", "text", False),
        "Quilometragem": ("Quilometragem", "decimal", False),
        "Preço": ("Preco", "decimal", True),
        "Status (ID)": ("status_id", "int", True),
        "URL da imagem": ("imagem_url", "url", False),
    }
    valid_status_ids = {
        str(status.get("id"))
        for status in statuses
        if status.get("id") is not None
    }

    for label, (field, kind, required) in fields.items():
        raw_value = values.get(label, "").strip()
        if not raw_value:
            if required:
                raise XanoError(f"O campo {label} é obrigatório.")
            continue
        try:
            if kind == "int":
                parsed_value = int(raw_value)
                if label == "Status (ID)" and str(parsed_value) not in valid_status_ids:
                    raise XanoError("Selecione um status de veículo válido.")
                if label == "Ano" and not 1900 <= parsed_value <= 2100:
                    raise XanoError("O campo Ano precisa estar entre 1900 e 2100.")
                payload[field] = parsed_value
            elif kind == "decimal":
                amount = Decimal(raw_value.replace(",", "."))
                if not amount.is_finite() or amount < 0:
                    raise XanoError(
                        f"O campo {label} precisa ser um valor finito e não negativo."
                    )
                payload[field] = float(amount)
            elif kind == "url":
                payload[field] = _validate_image_url(raw_value)
            else:
                payload[field] = raw_value
        except XanoError:
            raise
        except (ValueError, InvalidOperation) as exc:
            raise XanoError(f"Valor inválido no campo {label}.") from exc
    return payload


def _build_part_payload(values: dict[str, str]) -> dict[str, str | int | float]:
    name = values.get("Nome", "").strip()
    if not name:
        raise XanoError("O campo Nome é obrigatório.")

    raw_price = values.get("Preço", "").strip()
    if not raw_price:
        raise XanoError("O campo Preço é obrigatório.")

    try:
        price = Decimal(raw_price.replace(",", "."))
        if not price.is_finite() or price < 0:
            raise XanoError("O campo Preço precisa ser um valor finito e não negativo.")
    except XanoError:
        raise
    except (ValueError, InvalidOperation) as exc:
        raise XanoError("Valor inválido no campo Preço.") from exc

    payload: dict[str, str | int | float] = {
        "PCNome": name,
        "PCvalor": float(price),
    }
    for label, field in (("Quantidade", "qtd_disp"), ("Área (ID)", "area_id")):
        raw_value = values.get(label, "").strip()
        if not raw_value:
            continue
        try:
            parsed_value = int(raw_value)
        except ValueError as exc:
            raise XanoError(f"Valor inválido no campo {label}.") from exc
        if parsed_value < 0:
            raise XanoError(f"O campo {label} não pode ser negativo.")
        payload[field] = parsed_value
    return payload


def _build_vehicle_details_payload(values: dict[str, str]) -> dict[str, object]:
    text_fields = {
        "UF de registro": "uf_registro",
        "Cidade de registro": "cidade_registro",
        "Motorização / cilindrada": "motorizacao",
    }
    payload: dict[str, object] = {}
    for label, field in text_fields.items():
        value = values.get(label, "").strip()
        if value:
            payload[field] = value

    choices = {
        "UF de registro": {
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO",
        },
        "Combustível": {"Flex", "Gasolina", "Diesel", "Elétrico", "Híbrido"},
        "Câmbio / transmissão": {"Automático", "Manual", "CVT", "Automatizado"},
    }
    for label, field in (
        ("UF de registro", "uf_registro"),
        ("Combustível", "combustivel"),
        ("Câmbio / transmissão", "cambio"),
    ):
        value = values.get(label, "").strip()
        if value:
            if value not in choices[label]:
                raise XanoError(f"Selecione uma opção válida para {label}.")
            payload[field] = value

    raw_year = values.get("Ano", "").strip()
    if raw_year:
        try:
            year = int(raw_year)
        except ValueError as exc:
            raise XanoError("Valor inválido no campo Ano.") from exc
        if not 1900 <= year <= 2100:
            raise XanoError("O campo Ano precisa estar entre 1900 e 2100.")
        payload["ano_fabricacao"] = year

    integer_fields = {
        "Número de portas": ("numero_portas", 1, 20),
        "Número de lugares": ("numero_lugares", 1, 100),
    }
    for label, (field, minimum, maximum) in integer_fields.items():
        raw_value = values.get(label, "").strip()
        if not raw_value:
            continue
        try:
            value = int(raw_value)
        except ValueError as exc:
            raise XanoError(f"Valor inválido no campo {label}.") from exc
        if not minimum <= value <= maximum:
            raise XanoError(f"O campo {label} precisa estar entre {minimum} e {maximum}.")
        payload[field] = value

    raw_mileage = values.get("Quilometragem", "").strip()
    if raw_mileage:
        try:
            mileage = Decimal(raw_mileage.replace(",", "."))
        except InvalidOperation as exc:
            raise XanoError("Valor inválido no campo Quilometragem atual.") from exc
        if not mileage.is_finite() or mileage < 0:
            raise XanoError("A Quilometragem atual precisa ser não negativa.")
        payload["quilometragem"] = float(mileage)

    raw_options = values.get("Opcionais e equipamentos", "").strip()
    if raw_options:
        payload["opcionais"] = [
            item.strip() for item in raw_options.split(",") if item.strip()
        ]

    return payload


class FormState(rx.State):
    values: dict[str, str] = {}
    vehicle_statuses: list[dict] = []
    part_areas: list[dict] = []
    saving: bool = False
    loading_statuses: bool = False
    loading_part_areas: bool = False
    error: str = ""
    success: str = ""
    status_error: str = ""
    part_area_error: str = ""
    uf_options: list[str] = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    ]
    fuel_options: list[str] = ["Flex", "Gasolina", "Diesel", "Elétrico", "Híbrido"]
    transmission_options: list[str] = ["Automático", "Manual", "CVT", "Automatizado"]
    door_options: list[str] = ["2", "3", "4", "5"]
    seat_options: list[str] = ["2", "3", "4", "5", "6", "7", "8", "9"]

    @rx.var
    def image_preview_url(self) -> str:
        return self.values.get("URL da imagem", "")

    @rx.var
    def selected_status_label(self) -> str:
        selected_id = self.values.get("Status (ID)", "")
        for status in self.vehicle_statuses:
            if str(status.get("id", "")) == selected_id:
                return str(status.get("Descricao", ""))
        return ""

    @rx.var
    def selected_status_class(self) -> str:
        return vehicle_status_class(self.selected_status_label)

    def set_field(self, name: str, value: str) -> None:
        self.values[name] = value
        self.error = ""
        self.success = ""

    async def load_vehicle_statuses(self) -> None:
        self.loading_statuses, self.status_error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            result = client.request(
                "GET",
                "/status-veiculos",
                token=auth_state.token,
            )
            if not isinstance(result, list) or any(
                not isinstance(status, dict)
                or status.get("id") is None
                or not isinstance(status.get("Descricao"), str)
                for status in result
            ):
                raise XanoError("A API retornou uma lista de status de veículo inválida.")
            self.vehicle_statuses = [
                {"id": str(status["id"]), "Descricao": status["Descricao"]}
                for status in result
            ]
            if not self.values.get("Status (ID)"):
                available = next(
                    (
                        status["id"]
                        for status in self.vehicle_statuses
                        if status["Descricao"].strip().casefold()
                        in {"disponível", "disponivel"}
                    ),
                    "",
                )
                if available:
                    self.values["Status (ID)"] = available
        except XanoError as exc:
            self.vehicle_statuses, self.status_error = [], str(exc)
        finally:
            self.loading_statuses = False

    async def load_part_areas(self) -> None:
        self.loading_part_areas, self.part_area_error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            result = client.request("GET", "/veiculo-areas", token=auth_state.token)
            if not isinstance(result, list) or any(
                not isinstance(area, dict)
                or area.get("id") is None
                or not isinstance(area.get("Secao"), str)
                for area in result
            ):
                raise XanoError("A API retornou uma lista de áreas de peças inválida.")
            self.part_areas = [
                {"id": str(area["id"]), "Secao": area["Secao"].strip()}
                for area in result
                if area["Secao"].strip()
            ]
        except XanoError as exc:
            self.part_areas, self.part_area_error = [], str(exc)
        finally:
            self.loading_part_areas = False

    async def save(self, endpoint: str) -> None:
        self.saving, self.error, self.success = True, "", ""
        try:
            schemas = {
                "clientes": {
                    "Nome": ("CNome", "text", True),
                    "CPF": ("CPF", "text", True),
                    "Telefone": ("Telefone", "text", True),
                    "E-mail": ("Email", "text", True),
                },
                "veiculos": {
                    "Marca": ("Marca", "text", True),
                    "Modelo": ("Modelo", "text", True),
                    "Cor": ("Cor", "text", True),
                    "Ano": ("Ano", "int", True),
                    "Placa": ("Placa", "text", False),
                    "Chassi": ("Chassi", "text", False),
                    "Quilometragem": ("Quilometragem", "decimal", False),
                    "Preço": ("Preco", "decimal", True),
                    "Status (ID)": ("status_id", "int", True),
                    "URL da imagem": ("imagem_url", "url", False),
                },
                "pecas": {
                    "Nome": ("PCNome", "text", True),
                    "Preço": ("PCvalor", "decimal", True),
                    "Quantidade": ("qtd_disp", "int", True),
                    "Área (ID)": ("area_id", "int", False),
                },
            }
            schema = schemas.get(endpoint.strip("/"))
            if schema is None:
                raise XanoError(
                    "Este formulário não corresponde a um endpoint de cadastro disponível."
                )

            if endpoint.strip("/") == "veiculos":
                payload = _build_vehicle_payload(self.values, self.vehicle_statuses)
                details_payload = _build_vehicle_details_payload(self.values)
            elif endpoint.strip("/") == "pecas":
                payload = _build_part_payload(self.values)
                details_payload = {}
            else:
                payload: dict[str, str | int | float] = {}
                details_payload = {}
                for label, (field, kind, required) in schema.items():
                    raw_value = self.values.get(label, "").strip()
                    if not raw_value:
                        if required:
                            raise XanoError(f"O campo {label} é obrigatório.")
                        continue
                    try:
                        if kind == "int":
                            payload[field] = int(raw_value)
                        elif kind == "decimal":
                            amount = Decimal(raw_value.replace(",", "."))
                            if not amount.is_finite() or amount < 0:
                                raise XanoError(
                                    f"O campo {label} precisa ser um valor finito e não negativo."
                                )
                            payload[field] = float(amount)
                        elif kind == "url":
                            payload[field] = _validate_image_url(raw_value)
                        else:
                            payload[field] = raw_value
                    except XanoError:
                        raise
                    except (ValueError, InvalidOperation) as exc:
                        raise XanoError(f"Valor inválido no campo {label}.") from exc

            auth_state = await self.get_state(AuthState)
            response = client.request(
                "POST",
                f"/{endpoint.strip('/')}",
                token=auth_state.token,
                json=payload,
            )
            if endpoint.strip("/") == "veiculos" and details_payload:
                vehicle_id = response.get("id") if isinstance(response, dict) else None
                if vehicle_id is None:
                    raise XanoError(
                        "O veículo foi salvo, mas a API não retornou o ID para salvar os detalhes."
                    )
                client.request(
                    "POST",
                    f"/veiculos/{vehicle_id}/detalhes",
                    token=auth_state.token,
                    json=details_payload,
                )
            self.success = "Registro salvo no Xano com sucesso."
            self.values = {}
        except XanoError as exc:
            self.error = str(exc)
        finally:
            self.saving = False
