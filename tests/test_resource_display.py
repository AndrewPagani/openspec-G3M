import unittest

from app.services.xano_client import XanoError
from app.state.form_state import _validate_image_url
from app.state.resource_state import _normalize_record


class ResourceDisplayTests(unittest.TestCase):
    def test_client_label_combines_name_and_cpf(self) -> None:
        record = _normalize_record(
            {"id": 4, "CNome": "Ana Silva", "CPF": "123.456.789-00"},
            "/clientes",
        )

        self.assertEqual(record["_display_label"], "Ana Silva - 123.456.789-00")

    def test_vehicle_display_includes_title_year_price_and_image_url(self) -> None:
        record = _normalize_record(
            {
                "id": 12,
                "Marca": "Marca",
                "Modelo": "Modelo",
                "Ano": 2025,
                "Preco": 85000,
                "Imagem_url": "https://example.test/car.jpg",
            },
            "/veiculos",
        )

        self.assertEqual(record["_vehicle_name"], "Marca Modelo")
        self.assertEqual(record["_vehicle_year"], "2025")
        self.assertEqual(record["_vehicle_price"], "R$ 85.000,00")
        self.assertEqual(record["_image_url"], "https://example.test/car.jpg")

    def test_vehicle_image_url_accepts_http_and_https_only(self) -> None:
        self.assertEqual(
            _validate_image_url("https://example.test/car.png"),
            "https://example.test/car.png",
        )
        with self.assertRaises(XanoError):
            _validate_image_url("javascript:alert(1)")
        with self.assertRaises(XanoError):
            _validate_image_url("not-a-url")


if __name__ == "__main__":
    unittest.main()
