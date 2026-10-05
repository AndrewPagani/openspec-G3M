import unittest

from app.services.xano_client import XanoError
from app.state.vendas_state import (
    VendasState,
    _format_local_datetime,
    _parse_installment_count,
)


class VendasStateTests(unittest.TestCase):
    def test_installment_count_accepts_values_from_one_through_twenty_four(self) -> None:
        self.assertEqual(_parse_installment_count("1"), 1)
        self.assertEqual(_parse_installment_count("24"), 24)

    def test_installment_count_rejects_non_integer_and_out_of_range_values(self) -> None:
        for value in ("0", "25", "1.5", "invalid"):
            with self.subTest(value=value), self.assertRaises(XanoError):
                _parse_installment_count(value)

    def test_extracts_manual_installment_fields(self) -> None:
        installments = VendasState._extract_installments(
            {
                "parcelas": [
                    {
                        "id": 5,
                        "numero_parcela": 1,
                        "total_parcelas": 2,
                        "valor": 10.5,
                        "vencimento": "2026-10-05",
                        "status": "PENDENTE",
                        "forma_recebida": None,
                        "recebido_em": None,
                        "recebido_por": None,
                    }
                ]
            }
        )
        self.assertEqual(
            installments,
            [
                {
                    "id": "5",
                    "numero_parcela": "1",
                    "total_parcelas": "2",
                    "valor": "10,50",
                    "vencimento": "05/10/2026",
                    "status": "PENDENTE",
                    "forma_recebida": "",
                    "recebido_em": "",
                    "recebido_por": "",
                }
            ],
        )

    def test_rejects_malformed_installment_response(self) -> None:
        with self.assertRaises(XanoError):
            VendasState._extract_installments({"parcelas": [{"id": 1}, "invalid"]})

    def test_formats_due_date_in_sao_paulo_timezone(self) -> None:
        self.assertEqual(
            _format_local_datetime("2026-10-05T12:00:00Z"),
            "05/10/2026",
        )
        self.assertEqual(
            _format_local_datetime("2026-10-05T12:00:00Z", include_time=True),
            "05/10/2026 09:00",
        )


if __name__ == "__main__":
    unittest.main()
