from __future__ import annotations

from typing import Any

import reflex as rx

from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState
from app.state.read_lifecycle import read_event


def _value(record: dict[str, Any], *keys: str, default: str = "Não informado") -> str:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _normalize_detail(response: object) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise XanoError("A API retornou detalhes de veículo em formato inválido.")
    base = response.get("veiculo") if isinstance(response.get("veiculo"), dict) else response
    details = response.get("detalhes")
    if not isinstance(details, dict):
        details = response.get("veiculo_detalhe")
    if not isinstance(details, dict):
        details = {}

    merged = {**base, **details}
    normalized = {
        "id": str(merged.get("id") or ""),
        "marca": _value(merged, "Marca", "marca", default=""),
        "modelo": _value(merged, "Modelo", "modelo", default=""),
        "placa": _value(merged, "Placa", "placa"),
        "chassi": _value(merged, "Chassi", "chassi"),
        "uf_registro": _value(merged, "uf_registro", "UF_registro"),
        "cidade_registro": _value(merged, "cidade_registro"),
        "ano_fabricacao": _value(merged, "ano_fabricacao", "Ano"),
        "motorizacao": _value(merged, "motorizacao"),
        "combustivel": _value(merged, "combustivel", "Combustivel"),
        "cambio": _value(merged, "cambio"),
        "quilometragem": _value(merged, "quilometragem", "Quilometragem"),
        "numero_portas": _value(merged, "numero_portas"),
        "numero_lugares": _value(merged, "numero_lugares"),
        "opcionais": [
            str(item).strip()
            for item in (merged.get("opcionais") or merged.get("Opcionais") or [])
            if str(item).strip()
        ],
        "imagem_url": _value(merged, "imagem_url", default=""),
        "status": _value(merged, "status_descricao", "Status", "status"),
    }
    return normalized


class VehicleDetailState(rx.State):
    vehicle: dict[str, Any] = {}
    opcionais: list[str] = []
    read_id: str = ""
    read_generation: int = 0
    loading: bool = False
    error: str = ""

    @read_event(outputs=('vehicle', 'opcionais', 'loading', 'error', 'read_id'), clear=('vehicle', 'opcionais', 'error'))
    async def load(self) -> None:
        vehicle_id = str(self.router.page.params.get("id", "")).strip()
        self.read_id = vehicle_id
        if not vehicle_id.isdigit() or int(vehicle_id) < 1:
            self.loading = False
            self.vehicle = {}
            self.error = "Identificador de veículo inválido."
            return
        self.loading, self.error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            response = await client.async_request(
                "GET",
                f"/veiculos/{vehicle_id}",
                token=auth_state.token,
            )
            self.vehicle = _normalize_detail(response)
            self.opcionais = self.vehicle["opcionais"]
        except XanoError as exc:
            self.vehicle, self.opcionais, self.error = {}, [], str(exc)
        finally:
            self.loading = False
