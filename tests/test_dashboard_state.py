import unittest

from app.services.xano_client import XanoError
from app.state.dashboard_state import (
    _build_params,
    _count,
    _currency,
    _extract_kpis,
    _percentage,
    _report_rows,
)


class DashboardStateTests(unittest.TestCase):
    def test_formats_currency_in_brazilian_locale(self) -> None:
        self.assertEqual(_currency("1234.5", "valor"), "R$ 1.234,50")

    def test_formats_percentage_in_brazilian_locale(self) -> None:
        self.assertEqual(_percentage("12.5", "cancelamentos"), "12,50%")

    def test_formats_integer_counts_and_rejects_fractional_counts(self) -> None:
        self.assertEqual(_count("3.0", "vendas"), "3")
        with self.assertRaises(XanoError):
            _count("3.5", "vendas")

    def test_formats_report_rows_without_exposing_foreign_keys(self) -> None:
        rows = _report_rows(
            [
                {
                    "data": "2026-10-01",
                    "quantidade": 3,
                    "valor_liquido": 1200.5,
                    "vendedor_id": 9,
                }
            ],
            "vendas por período",
        )

        self.assertEqual(
            rows,
            ["Data: 2026-10-01 · Quantidade: 3 · Valor liquido: R$ 1.200,50"],
        )

    def test_rejects_non_list_report_data(self) -> None:
        with self.assertRaises(XanoError):
            _report_rows({"unexpected": True}, "vendas por período")

    def test_extracts_kpis_from_documented_and_current_xano_shapes(self) -> None:
        flat = {"vendas_pagas": 2}
        nested = {"kpis": flat}

        self.assertEqual(_extract_kpis(flat), flat)
        self.assertEqual(_extract_kpis(nested), flat)

    def test_builds_manager_filters_and_does_not_send_vendor_filters_for_seller(self) -> None:
        manager_params = _build_params(
            "2026-10-01",
            "2026-10-31",
            is_manager=True,
            status_id="2",
            vendedor_id="8",
            forma_pagamento_id="3",
            tipo_item="veiculo",
            status_veiculo_id="1",
        )
        seller_params = _build_params(
            "2026-10-01",
            "2026-10-31",
            is_manager=False,
            vendedor_id="8",
        )

        self.assertEqual(
            manager_params,
            {
                "data_inicio": "2026-10-01",
                "data_fim": "2026-10-31",
                "status_id": 2,
                "vendedor_id": 8,
                "forma_pagamento_id": 3,
                "status_veiculo_id": 1,
                "tipo_item": "veiculo",
            },
        )
        self.assertEqual(seller_params, {"data_inicio": "2026-10-01", "data_fim": "2026-10-31"})

    def test_rejects_invalid_dashboard_filter_values(self) -> None:
        with self.assertRaises(XanoError):
            _build_params("2026-10-01", "2026-10-31", is_manager=True, status_id="0")
        with self.assertRaises(XanoError):
            _build_params("2026-10-01", "2026-10-31", is_manager=True, tipo_item="other")


if __name__ == "__main__":
    unittest.main()
