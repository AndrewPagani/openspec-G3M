import io
import unittest
from unittest.mock import AsyncMock, patch
from zipfile import ZipFile

from app.services.excel_report import ReportError, build_report, collect_report
from app.services.xano_client import XanoError

FILTERS = {
    "data_inicio": "2026-11-01",
    "data_fim": "2026-11-03",
    "status_id": 1,
    "vendedor_id": 2,
    "forma_pagamento_id": 3,
    "tipo_item": "peca",
    "status_veiculo_id": 4,
}
KPI_ZERO = {
    "total_vendas_periodo": 0,
    "valor_bruto_vendido": 0,
    "valor_liquido_recebido_periodo": 0,
    "vendas_pagas": 0,
    "vendas_canceladas": 0,
    "percentual_vendas_canceladas": 0,
}


def page(number=1, pages=0, items=None):
    return {
        "items": items if items is not None else [],
        "pagination": {
            "page": number,
            "per_page": 1,
            "total": pages,
            "total_pages": pages,
        },
    }


class ExcelReportTests(unittest.IsolatedAsyncioTestCase):
    async def test_filters_and_valid_empty_collections(self):
        async def request(_method, route, *, token, params):
            self.assertEqual(token, "session")
            if route == "/gerenciamento/indicadores":
                self.assertEqual(params, FILTERS)
                return {"kpis": KPI_ZERO}
            if route == "/vendas":
                self.assertEqual(
                    params,
                    {
                        "data_inicio": "2026-11-01",
                        "data_fim": "2026-11-03",
                        "status_id": "1",
                        "vendedor_id": "2",
                        "forma_pagamento_id": "3",
                        "page": "1",
                        "per_page": "100",
                        "busca": "",
                    },
                )
            else:
                self.assertEqual(params, {"page": "1", "per_page": "100"})
            return page()

        with patch(
            "app.services.excel_report.client.async_request", side_effect=request
        ) as client:
            dashboard, collections = await collect_report(
                "session", FILTERS, False, AsyncMock()
            )
        self.assertEqual(client.await_count, 5)
        self.assertEqual(list(collections), ["Vendas", "Clientes", "Veículos", "Peças"])
        binary = await build_report(
            dashboard, collections, FILTERS, "mes", False, "Vendedor", {}
        )
        with ZipFile(io.BytesIO(binary)) as book:
            shared_strings = book.read("xl/sharedStrings.xml").decode()
            self.assertIn("Nenhum registro", shared_strings)
            self.assertIn("CPF", shared_strings)
            self.assertNotIn("Usuários", book.read("xl/workbook.xml").decode())

    async def test_historical_export_keeps_sales_without_linked_customer(self):
        params = {"data_inicio": "2000-11-01", "data_fim": "2026-11-20"}
        sales = [
            {
                "id": sale_id,
                "data_venda": "2026-11-01T12:00:00Z",
                "cliente": {"id": None, "CNome": ""}
                if sale_id > 98
                else {"id": 1, "CNome": "Cliente de teste"},
                "Valor_final": 150,
            }
            for sale_id in range(1, 102)
        ]
        kpis = {**KPI_ZERO, "total_vendas_periodo": 101}

        async def request(_method, route, *, token, params):
            if route == "/gerenciamento/indicadores":
                return {"kpis": kpis}
            if route != "/vendas":
                return page()
            self.assertEqual(params["data_inicio"], "2000-11-01")
            self.assertEqual(params["busca"], "")
            number = int(params["page"])
            return {
                "items": sales[(number - 1) * 100 : number * 100],
                "pagination": {
                    "page": number,
                    "per_page": 100,
                    "total": 101,
                    "total_pages": 2,
                },
            }

        with patch(
            "app.services.excel_report.client.async_request", side_effect=request
        ):
            dashboard, collections = await collect_report(
                "session", params, False, AsyncMock()
            )
        self.assertEqual(len(collections["Vendas"]), 101)
        self.assertEqual(
            sum(not row["cliente"]["CNome"] for row in collections["Vendas"]), 3
        )

        binary = await build_report(
            dashboard, collections, params, "dia", False, "Vendedor", {}
        )
        with ZipFile(io.BytesIO(binary)) as book:
            sales_sheet = book.read("xl/worksheets/sheet2.xml")
            self.assertIn(b'<row r="102"', sales_sheet)
            self.assertNotIn(b'r="C102"', sales_sheet)

    async def test_subsequent_page_failure_does_not_return_partial_report(self):
        for invalid in (
            page(2, 2, [{"id": 4}]),  # duplicate record
            page(2, 2, []),  # incomplete page
            page(2, 3, [{"id": 5}]),  # total changed during collection
            XanoError("dados privados simulados"),  # API read failed
        ):
            with (
                self.subTest(invalid=invalid),
                patch(
                    "app.services.excel_report.client.async_request",
                    side_effect=[{"kpis": KPI_ZERO}, page(1, 2, [{"id": 4}]), invalid],
                ),
                self.assertRaisesRegex(
                    ReportError, "^Não foi possível consultar Vendas"
                ),
            ):
                await collect_report("session", FILTERS, False, AsyncMock())

    async def test_mismatch_blocks_workbook(self):
        with self.assertRaisesRegex(ReportError, "divergiu do Dashboard"):
            await build_report(
                {"kpis": KPI_ZERO},
                {"Vendas": [{"id": 1}]},
                FILTERS,
                "dia",
                False,
                "Vendedor",
                {},
            )
