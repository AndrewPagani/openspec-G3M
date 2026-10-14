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
        "URL da imagem": ("Imagem_url", "url", False),
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


class FormState(rx.State):
    values: dict[str, str] = {}
    vehicle_statuses: list[dict] = []
    saving: bool = False
    loading_statuses: bool = False
    error: str = ""
    success: str = ""
    status_error: str = ""

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
                    "URL da imagem": ("Imagem_url", "url", False),
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
            else:
                payload: dict[str, str | int | float] = {}
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
            client.request(
                "POST",
                f"/{endpoint.strip('/')}",
                token=auth_state.token,
                json=payload,
            )
            self.success = "Registro salvo no Xano com sucesso."
            self.values = {}
        except XanoError as exc:
            self.error = str(exc)
        finally:
            self.saving = False
