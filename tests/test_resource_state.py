from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.xano_client import XanoError
from app.services.vehicle_status import vehicle_status_class
from app.state.auth_state import AuthState
from app.state.form_state import _build_vehicle_payload
from app.state.resource_state import ResourceState, _normalize_record, _pagination_total_pages
from app.state.form_state import FormState


class ResourceStateTests(unittest.TestCase):
    def test_normalizes_part_catalog_fields(self) -> None:
        part = _normalize_record(
            {
                "PCNome": "Pastilha de freio",
                "PCvalor": 299.9,
                "qtd_disp": 8,
                "area_secao": "Freios",
            },
            "/pecas",
        )

        self.assertEqual(part["_part_name"], "Pastilha de freio")
        self.assertEqual(part["_part_price"], "R$ 299,90")
        self.assertEqual(part["_part_area"], "Freios")
        self.assertEqual(part["_part_quantity"], "8")
        self.assertEqual(part["_part_stock_class"], "stock-available")
        self.assertEqual(part["_part_image_url"], "")

    def test_classifies_empty_and_low_part_stock(self) -> None:
        self.assertEqual(
            _normalize_record({"qtd_disp": 0}, "/pecas")["_part_stock_class"],
            "stock-out",
        )
        self.assertEqual(
            _normalize_record({"qtd_disp": 5}, "/pecas")["_part_stock_class"],
            "stock-low",
        )

    def test_rejects_invalid_part_quantity(self) -> None:
        with self.assertRaisesRegex(XanoError, "quantidade de peças inválida"):
            _normalize_record({"qtd_disp": -1}, "/pecas")

    def test_normalizes_vehicle_fields_from_xano_record(self) -> None:
        vehicle = _normalize_record(
            {
                "Marca": "BYD",
                "Modelo": "Song Pro",
                "Ano": 2024,
                "Quilometragem": 25000,
                "Preco": 189990.5,
                "Combustivel": "Flex",
                "Imagem_url": "https://example.test/song-pro.jpg",
                "status_descricao": "Disponível",
            },
            "/veiculos",
        )

        self.assertEqual(vehicle["_vehicle_name"], "BYD Song Pro")
        self.assertEqual(vehicle["_vehicle_year"], "2024")
        self.assertEqual(vehicle["_vehicle_mileage"], "25.000")
        self.assertEqual(vehicle["_vehicle_fuel"], "Flex")
        self.assertEqual(vehicle["_vehicle_price"], "R$ 189.990,50")
        self.assertEqual(vehicle["_image_url"], "https://example.test/song-pro.jpg")
        self.assertEqual(vehicle["_vehicle_status"], "Disponível")
        self.assertEqual(vehicle["_vehicle_status_class"], "status-available")

    def test_missing_optional_vehicle_fields_are_not_fabricated(self) -> None:
        vehicle = _normalize_record(
            {"Modelo": "Modelo cadastrado", "Ano": 2025, "Preco": 0},
            "/veiculos",
        )

        self.assertEqual(vehicle["_vehicle_name"], "Modelo cadastrado")
        self.assertEqual(vehicle["_vehicle_mileage"], "Não informado")
        self.assertEqual(vehicle["_vehicle_fuel"], "Não informado")
        self.assertEqual(vehicle["_image_url"], "")
        self.assertEqual(vehicle["_vehicle_price"], "R$ 0,00")
        self.assertEqual(vehicle["_vehicle_status_class"], "status-neutral")

    def test_accepts_requested_lowercase_vehicle_payload(self) -> None:
        vehicle = _normalize_record(
            {
                "imagem_url": "https://example.test/car.png",
                "modelo": "Sedan",
                "ano": 2023,
                "quilometragem": 1234,
                "valor": 25000,
                "combustivel": "Flex",
            },
            "/veiculos",
        )

        self.assertEqual(vehicle["_vehicle_name"], "Sedan")
        self.assertEqual(vehicle["_vehicle_year"], "2023")
        self.assertEqual(vehicle["_vehicle_mileage"], "1.234")
        self.assertEqual(vehicle["_vehicle_fuel"], "Flex")
        self.assertEqual(vehicle["_vehicle_price"], "R$ 25.000,00")
        self.assertEqual(vehicle["_image_url"], "https://example.test/car.png")

    def test_vehicle_status_badges_use_database_status_colors(self) -> None:
        self.assertEqual(vehicle_status_class("Disponível"), "status-available")
        self.assertEqual(vehicle_status_class("Disponivel"), "status-available")
        self.assertEqual(vehicle_status_class("Reservado"), "status-reserved")
        self.assertEqual(vehicle_status_class("Vendido"), "status-sold")
        self.assertEqual(vehicle_status_class("Outro"), "status-neutral")

    def test_builds_vehicle_payload_with_selected_xano_status_and_image_url(self) -> None:
        payload = _build_vehicle_payload(
            {
                "Marca": " G3M ",
                "Modelo": "Sedan",
                "Cor": "Azul",
                "Ano": "2025",
                "Quilometragem": "12500",
                "Preço": "123456.78",
                "Status (ID)": "3",
                "URL da imagem": "https://images.example.test/sedan.png",
            },
            [{"id": 1, "Descricao": "Disponível"}, {"id": 3, "Descricao": "Vendido"}],
        )

        self.assertEqual(
            payload,
            {
                "Marca": "G3M",
                "Modelo": "Sedan",
                "Cor": "Azul",
                "Ano": 2025,
                "Quilometragem": 12500.0,
                "Preco": 123456.78,
                "status_id": 3,
                "Imagem_url": "https://images.example.test/sedan.png",
            },
        )

    def test_rejects_unknown_vehicle_status_and_invalid_image_url(self) -> None:
        values = {
            "Marca": "G3M",
            "Modelo": "Sedan",
            "Cor": "Azul",
            "Ano": "2025",
            "Preço": "25000",
            "Status (ID)": "9",
        }
        statuses = [{"id": 1, "Descricao": "Disponível"}]
        with self.assertRaisesRegex(XanoError, "status de veículo válido"):
            _build_vehicle_payload(values, statuses)

        values["Status (ID)"] = "1"
        values["URL da imagem"] = "file:///car.png"
        with self.assertRaisesRegex(XanoError, "HTTP ou HTTPS"):
            _build_vehicle_payload(values, statuses)


class ResourceStatePaginationTests(unittest.IsolatedAsyncioTestCase):
    async def test_load_fetches_every_vehicle_page(self) -> None:
        async def get_state(_state_type):
            return SimpleNamespace(token="test-token")

        state = SimpleNamespace(
            endpoint="",
            title="",
            loading=False,
            error="",
            records=[],
            get_state=get_state,
        )
        first_page = {
            "items": [{"id": 1, "Modelo": "Primeiro"}],
            "pagination": {"total_pages": 2},
        }
        second_page = {
            "items": [{"id": 2, "Modelo": "Segundo"}],
            "pagination": {"total_pages": 2},
        }

        with patch(
            "app.state.resource_state.client.request",
            side_effect=[first_page, second_page],
        ) as request:
            await ResourceState.load.fn(state, "/veiculos", "Veículos")

        self.assertEqual([row["id"] for row in state.records], [1, 2])
        self.assertEqual(request.call_count, 2)
        self.assertEqual(request.call_args_list[0].kwargs["params"], {"page": 1, "per_page": 100})
        self.assertEqual(request.call_args_list[1].kwargs["params"], {"page": 2, "per_page": 100})
        self.assertIs(request.call_args_list[0].kwargs["token"], "test-token")
        self.assertFalse(state.loading)
        self.assertEqual(state.error, "")

    def test_accepts_integer_equivalent_pagination_values(self) -> None:
        self.assertEqual(_pagination_total_pages({"total_pages": 2}, "Peças"), 2)
        self.assertEqual(_pagination_total_pages({"total_pages": 2.0}, "Peças"), 2)
        self.assertEqual(_pagination_total_pages({"total_pages": "2"}, "Peças"), 2)

    def test_rejects_non_integral_pagination_values(self) -> None:
        for value in (True, 1.5, "2.0", "", None, 0):
            with self.subTest(value=value):
                with self.assertRaisesRegex(XanoError, "paginação inválida"):
                    _pagination_total_pages({"total_pages": value}, "Peças")


class VehicleFormStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_loads_real_statuses_and_defaults_to_available(self) -> None:
        async def get_state(_state_type):
            return SimpleNamespace(token="test-token")

        state = SimpleNamespace(
            values={},
            vehicle_statuses=[],
            loading_statuses=False,
            status_error="",
            get_state=get_state,
        )
        statuses = [
            {"id": 4, "Descricao": "Vendido"},
            {"id": 2, "Descricao": "Disponível"},
            {"id": 3, "Descricao": "Reservado"},
        ]

        with patch(
            "app.state.form_state.client.request", return_value=statuses
        ) as request:
            await FormState.load_vehicle_statuses.fn(state)

        self.assertEqual(state.values["Status (ID)"], "2")
        self.assertEqual(
            state.vehicle_statuses,
            [
                {"id": "4", "Descricao": "Vendido"},
                {"id": "2", "Descricao": "Disponível"},
                {"id": "3", "Descricao": "Reservado"},
            ],
        )
        self.assertEqual(request.call_args.args[:2], ("GET", "/status-veiculos"))
        self.assertFalse(state.loading_statuses)
        self.assertEqual(state.status_error, "")

    async def test_saves_vehicle_status_and_image_url_to_xano(self) -> None:
        async def get_state(_state_type):
            return SimpleNamespace(token="test-token")

        state = SimpleNamespace(
            values={
                "Marca": "G3M",
                "Modelo": "Sedan",
                "Cor": "Azul",
                "Ano": "2025",
                "Preço": "45000.99",
                "Status (ID)": "2",
                "URL da imagem": "https://images.example.test/sedan.png",
            },
            vehicle_statuses=[
                {"id": "1", "Descricao": "Disponível"},
                {"id": "2", "Descricao": "Reservado"},
            ],
            saving=False,
            error="",
            success="",
            get_state=get_state,
        )

        with patch("app.state.form_state.client.request", return_value={"id": 15}) as request:
            await FormState.save.fn(state, "veiculos")

        self.assertEqual(request.call_args.args[:2], ("POST", "/veiculos"))
        self.assertEqual(request.call_args.kwargs["json"]["status_id"], 2)
        self.assertEqual(
            request.call_args.kwargs["json"]["Imagem_url"],
            "https://images.example.test/sedan.png",
        )
        self.assertEqual(state.values, {})
        self.assertEqual(state.vehicle_statuses[1]["Descricao"], "Reservado")
        self.assertFalse(state.saving)
        self.assertTrue(state.success)


if __name__ == "__main__":
    unittest.main()
