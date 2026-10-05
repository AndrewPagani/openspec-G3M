from __future__ import annotations

from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import reflex as rx

from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState


def _validate_image_url(value: str) -> str:
    parsed_url = urlparse(value)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise XanoError("O campo URL da imagem precisa ser um endereço HTTP ou HTTPS válido.")
    return value


class FormState(rx.State):
    values: dict[str, str] = {}
    saving: bool = False
    error: str = ""
    success: str = ""

    def set_field(self, name: str, value: str) -> None:
        self.values[name] = value

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
