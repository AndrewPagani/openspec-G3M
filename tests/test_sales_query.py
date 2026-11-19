import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx

from app.services.sales_query import sales_query_params
from app.state.vendas_state import VendasState


class SalesQueryTests(unittest.IsolatedAsyncioTestCase):
    def test_unfiltered_query_omits_optional_json_objects(self) -> None:
        outgoing = httpx.Request(
            "GET", "https://example.test/vendas", params=sales_query_params(),
        )
        self.assertEqual(dict(outgoing.url.params), {
            "page": "1", "per_page": "100", "busca": "",
        })

    def test_whitespace_only_filters_are_absent(self) -> None:
        outgoing = httpx.Request(
            "GET", "https://example.test/vendas",
            params=sales_query_params(
                page=2, cliente_id="  ", vendedor_id="\t", status_id="",
                forma_pagamento_id=" ", data_inicio=" ", data_fim=" ",
            ),
        )
        self.assertEqual(dict(outgoing.url.params), {
            "page": "2", "per_page": "100", "busca": "",
        })

    async def test_sales_filters_reach_the_get_query(self) -> None:
        async def get_state(_state_type):
            return SimpleNamespace(token="test-token")

        state = SimpleNamespace(
            get_state=get_state,
            busca="  Ana  ",
            filtro_forma_pagamento="3",
            filtro_data_inicio="2026-11-01",
            filtro_data_fim="2026-11-13",
            _rows=lambda result, message: result["items"],
        )
        with patch(
            "app.state.vendas_state.client.async_request",
            return_value={"items": []},
        ) as request:
            await VendasState.load_sales.fn.read_body(state)

        args, kwargs = request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "/vendas")
        self.assertNotIn("json", kwargs)
        outgoing = httpx.Request(*args, params=kwargs["params"])
        self.assertEqual(dict(outgoing.url.params), {
            "page": "1", "per_page": "100", "busca": "Ana",
            "forma_pagamento_id": "3",
            "data_inicio": "2026-11-01", "data_fim": "2026-11-13",
        })
        self.assertEqual(state.list_error, "")
        self.assertFalse(state.list_loading)
