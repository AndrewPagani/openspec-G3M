import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.xano_client import XanoError
from app.state.vendas_state import VendasState


def state_fixture():
    async def get_state(_state_type):
        return SimpleNamespace(token="fixture-token", is_manager=True, read_generation=0, records=[], complete=False)

    state = SimpleNamespace(
        get_state=get_state, read_generation=0, references_generation=0, processando=False, creation_uncertain=False,
        venda_id="", erro="", mensagem="", cliente_id="12", itens_json="[]",
        payment_url="", payment_flow="", payment_status="", total_confirmado="",
        payment_due_date="", parcelas=[], selected_items=[
            {"tipo": "veiculo", "id": "7", "qtd": "1", "nome": "Veículo de teste", "preco": "100"},
            {"tipo": "peca", "id": "7", "qtd": "2", "nome": "Peça de teste", "preco": "20"},
        ],
    )
    state._sale_payload = lambda: VendasState._sale_payload(state)
    state._set_payment = lambda response: VendasState._set_payment(state, response)
    state._extract_installments = VendasState._extract_installments

    async def generate():
        await VendasState.generate_payment_link.fn(state)

    async def methods():
        state.methods_loaded = True

    state.generate_payment_link = generate
    state.load_payment_methods = methods
    return state


class SalesPayloadTests(unittest.TestCase):
    def test_mixed_sale_keeps_vehicle_and_part_with_same_id(self):
        state = state_fixture()
        self.assertEqual(state._sale_payload(), {
            "cliente_id": 12, "itens": [{"qtd": 1, "veiculo_id": 7}, {"qtd": 2, "peca_id": 7}],
        })
        VendasState.remove_item.fn(state, "peca", "7")
        self.assertEqual([row["tipo"] for row in state.selected_items], ["veiculo"])

    def test_invalid_json_quantities_and_identifiers_are_rejected(self):
        for item in (
            {"peca_id": 2, "qtd": 1.5}, {"peca_id": 2, "qtd": True},
            {"peca_id": 2.5, "qtd": 1}, {"peca_id": 2, "qtd": "NaN"},
            {"veiculo_id": 2, "qtd": 2}, {"veiculo_id": 2, "peca_id": 3, "qtd": 1},
        ):
            with self.subTest(item=item):
                state = state_fixture()
                state.selected_items = []
                state.itens_json = json.dumps([item])
                with self.assertRaises(XanoError):
                    state._sale_payload()

    def test_payment_urls_require_https_and_exact_asaas_host(self):
        for url in (
            "javascript:alert(1)", "http://www.asaas.com/i/test",
            "https://asaas.com.evil.test/i/test", "https://asaas.com@evil.test/i/test",
            "https://user:pass@asaas.com/i/test",
        ):
            with self.subTest(url=url), self.assertRaises(XanoError):
                state_fixture()._set_payment({"invoice_url": url})


class SalesPaymentFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_retry_link_does_not_repeat_sale_or_reserve(self):
        state = state_fixture()
        with patch("app.state.vendas_state.client.async_request", side_effect=[
            {"id": 42, "Valor_final": 140}, XanoError("ASAAS temporariamente indisponível"),
            {"invoice_url": "https://sandbox.asaas.com/i/fixture", "status": "PENDING"},
        ]) as request:
            await VendasState.create_sale.fn(state)
            self.assertEqual(state.venda_id, "42")
            self.assertIn("preservada", state.erro)
            await VendasState.create_sale.fn(state)
            self.assertEqual(request.call_count, 2)
            await state.generate_payment_link()
        self.assertEqual([call.args[1] for call in request.call_args_list], [
            "/vendas", "/vendas/42/link-pagamento", "/vendas/42/link-pagamento",
        ])
        self.assertEqual(state.payment_url, "https://sandbox.asaas.com/i/fixture")
        self.assertEqual(state.erro, "")

    async def test_ambiguous_creation_does_not_allow_blind_second_post(self):
        for failure in (XanoError("Não foi possível conectar ao Xano"), {}, {"id": -3}):
            with self.subTest(failure=failure):
                state = state_fixture()
                with patch("app.state.vendas_state.client.async_request", side_effect=[failure]) as request:
                    await VendasState.create_sale.fn(state)
                    self.assertTrue(state.creation_uncertain)
                    await VendasState.create_sale.fn(state)
                self.assertEqual(request.call_count, 1)

    async def test_reopen_reads_saved_link_without_creating_charge(self):
        state = state_fixture()
        state.router = SimpleNamespace(page=SimpleNamespace(params={"id": "42"}))
        with patch("app.state.vendas_state.client.async_request", return_value={
            "payment_flow": "ASAAS", "total_venda": 140, "parcelas": [],
            "asaas_cobranca": {"invoice_url": "https://www.asaas.com/i/fixture", "status": "RECEIVED"},
        }) as request:
            await VendasState.load_sale.fn.read_body(state)
        self.assertEqual(request.call_args.args[:2], ("GET", "/vendas/42/pagamento"))
        self.assertEqual(request.call_count, 1)
        self.assertEqual(state.payment_status, "RECEIVED")
        self.assertEqual(state.payment_url, "https://www.asaas.com/i/fixture")
        with patch("app.state.vendas_state.client.async_request") as request:
            await VendasState.receive_installment.fn(state, "1")
        request.assert_not_called()

    async def test_failed_other_sale_clears_previous_link(self):
        state = state_fixture()
        state.payment_url = "https://www.asaas.com/i/previous"
        state.router = SimpleNamespace(page=SimpleNamespace(params={"id": "99"}))
        with patch("app.state.vendas_state.client.async_request", side_effect=XanoError("Venda não encontrada")):
            await VendasState.load_sale.fn.read_body(state)
        self.assertEqual(state.payment_url, "")
        self.assertEqual(state.parcelas, [])

    async def test_invalid_sale_route_clears_previous_payment(self):
        state = state_fixture()
        state.payment_url = "https://www.asaas.com/i/previous"
        state.router = SimpleNamespace(page=SimpleNamespace(params={"id": "invalid"}))
        with patch("app.state.vendas_state.client.async_request") as request:
            await VendasState.load_sale.fn.read_body(state)
        request.assert_not_called()
        self.assertEqual(state.payment_url, "")
        self.assertEqual(state.venda_id, "")

    async def test_legacy_history_keeps_received_installment(self):
        state = state_fixture()
        state.router = SimpleNamespace(page=SimpleNamespace(params={"id": "42"}))
        with patch("app.state.vendas_state.catalogs.get", return_value=[{"id": 1, "Metodo": "Pix"}]), patch("app.state.vendas_state.client.async_request", return_value={
            "total_venda": 140,
            "asaas_cobranca": None,
            "parcelas": [{"id": 2, "numero_parcela": 1, "total_parcelas": 1,
                "valor": 140, "status": "RECEBIDA", "vencimento": "2026-11-14",
                "recebido_em": "2026-11-14T14:00:00Z", "recebido_por": 1, "forma_recebida": "Pix"}],
        }):
            await VendasState.load_sale.fn.read_body(state)
        self.assertEqual(state.payment_flow, "LEGADO")
        self.assertEqual(state.parcelas[0]["valor"], "140,00")
        self.assertFalse(state.methods_loading)
        self.assertEqual(state.methods_error, "")
        self.assertEqual(state.payment_methods, [{"id": "1", "name": "Pix"}])

    async def test_sale_without_charge_can_be_reopened(self):
        state = state_fixture()
        state.payment_due_date = "01/01/2020"
        state.router = SimpleNamespace(page=SimpleNamespace(params={"id": "42"}))
        with patch("app.state.vendas_state.client.async_request", return_value={
            "total_venda": 140, "payment_flow": "ASAAS", "asaas_cobranca": None,
        }):
            await VendasState.load_sale.fn.read_body(state)
        self.assertEqual(state.detail_error, "")
        self.assertEqual(state.payment_url, "")
        self.assertEqual(state.payment_due_date, "")
        self.assertEqual(state.total_confirmado, "R$ 140,00")

    def test_legacy_timestamps_accept_xano_epoch_milliseconds(self):
        rows = VendasState._extract_installments({"parcelas": [{
            "id": 2, "numero_parcela": 1, "total_parcelas": 1, "valor": 140,
            "status": "RECEBIDA", "vencimento": 1794657600000,
            "recebido_em": 1794657600000, "recebido_por": 1, "forma_recebida": "Pix",
        }]})
        self.assertEqual(len(rows), 1)
