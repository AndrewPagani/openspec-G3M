import unittest

from scripts.generate_xano_seed import fixed_records, generate_clients, generate_transactions


class XanoSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixed = fixed_records()
        self.clients = generate_clients()
        self.sales, self.items, self.installments = generate_transactions(
            self.clients, self.fixed, 1
        )

    def test_generates_requested_counts_and_references(self) -> None:
        self.assertEqual(len(self.clients), 100)
        self.assertEqual(len(self.sales), 100)
        self.assertEqual(len(self.installments), 100)
        client_ids = {row["id"] for row in self.clients}
        vehicle_ids = {row["id"] for row in self.fixed["veiculo"]}
        part_ids = {row["id"] for row in self.fixed["peca"]}
        self.assertTrue(all(row["cliente_id"] in client_ids for row in self.sales))
        self.assertTrue(all(
            row["veiculo_id"] in vehicle_ids or row["peca_id"] in part_ids
            for row in self.items
        ))

    def test_generates_35_vehicle_sales_and_65_part_sales(self) -> None:
        vehicle_sale_ids = {row["venda_id"] for row in self.items if row["veiculo_id"]}
        self.assertEqual(len(vehicle_sale_ids), 35)
        self.assertEqual(len(self.sales) - len(vehicle_sale_ids), 65)

    def test_sale_totals_and_received_installments_are_consistent(self) -> None:
        totals = {}
        for row in self.items:
            totals[row["venda_id"]] = totals.get(row["venda_id"], 0) + row["qtd"] * row["preco_unit"]
        self.assertEqual(
            {row["id"]: round(row["Valor_final"], 2) for row in self.sales},
            {sale_id: round(total, 2) for sale_id, total in totals.items()},
        )
        self.assertTrue(all(row["status"] == "RECEBIDA" for row in self.installments))
        self.assertEqual(
            {row["venda_id"]: row["valor"] for row in self.installments},
            {row["id"]: row["Valor_final"] for row in self.sales},
        )
