import unittest

from app.services.xano_client import XanoError
from app.state.dashboard_state import (
    _build_params,
    _count,
    _currency,
    _average_currency,
    _extract_kpis,
    _extract_series,
    _percentage,
    _rounded_number,
    _report_rows,
    _analysis_rows,
    _chart_rows,
    _filter_options,
    _vehicle_status_chart_rows,
    _sales_status_rows,
    _trend_chart_rows,
    _has_chart_values,
    _payment_chart_rows,
    _low_stock_labels,
    _normalize_low_stock_rows,
    _salesperson_rows,
)
from app.state.auth_state import _role_is_manager


class DashboardStateTests(unittest.TestCase):
    def test_manager_role_matches_xano_roles(self) -> None:
        self.assertTrue(_role_is_manager("Gerente"))
        self.assertFalse(_role_is_manager("Vendedor"))
        self.assertFalse(_role_is_manager("Cliente"))
        self.assertFalse(_role_is_manager("Gerente Comercial"))
        self.assertFalse(_role_is_manager("Administrador"))

    def test_formats_currency_in_brazilian_locale(self) -> None:
        self.assertEqual(_currency("1234.5", "valor"), "R$ 1.234,50")

    def test_rounds_chart_values_to_two_decimal_places(self) -> None:
        self.assertEqual(_rounded_number("3123723.305", "valor"), 3123723.31)

    def test_builds_brand_chart_rows(self) -> None:
        brands = [{"marca": f"Marca {index}", "quantidade": index} for index in range(1, 10)]
        self.assertEqual(
            _chart_rows(
                brands,
                "veículos vendidos por marca",
                name_key="marca",
                value_key="quantidade",
                max_categories=None,
            ),
            [{"nome": f"Marca {index}", "quantidade": float(index)} for index in range(9, 0, -1)],
        )

    def test_calculates_average_sales_in_frontend(self) -> None:
        self.assertEqual(
            _average_currency("1000", "4", "vendas no período"),
            "R$ 250,00",
        )
        self.assertEqual(
            _average_currency("1000", "0", "vendas no período"),
            "R$ 0,00",
        )

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

    def test_formats_status_quantity_as_count_not_currency(self) -> None:
        rows = _report_rows(
            [
                {
                    "descricao": "Concluída",
                    "total_vendas": 99,
                    "valor_total": 3123723.30,
                }
            ],
            "vendas por status",
        )
        self.assertEqual(
            rows,
            ["Descricao: Concluída · Total vendas: 99 · Valor total: R$ 3.123.723,30"],
        )

    def test_rejects_non_list_report_data(self) -> None:
        with self.assertRaises(XanoError):
            _report_rows({"unexpected": True}, "vendas por período")

    def test_normalizes_new_xano_analysis_objects(self) -> None:
        self.assertEqual(
            _analysis_rows(
                {"disponivel": True, "propostas_total": 10, "taxa_conversao": 20},
                "conversão",
            ),
            ["Disponivel: True · Propostas total: 10 · Taxa conversao: 20,00%"],
        )
        self.assertEqual(
            _analysis_rows({"disponivel": False, "giro": 0}, "giro"),
            ["Não disponível no contrato atual do Xano."],
        )

    def test_normalizes_low_stock_parts_for_display(self) -> None:
        rows = _normalize_low_stock_rows(
            [
                {"id": 1, "PCNome": "Filtro", "qtd_disp": 0, "PCvalor": 35},
                {"id": 2, "nome": "Pastilha", "quantidade": 3, "valor_unitario": 120},
            ]
        )
        self.assertEqual(rows[0]["nome"], "Filtro")
        self.assertEqual(rows[1]["quantidade"], 3)
        self.assertEqual(
            _low_stock_labels(rows),
            ["Filtro — Sem estoque", "Pastilha — Quantidade: 3"],
        )

    def test_normalizes_salespeople_with_sale_counts(self) -> None:
        self.assertEqual(
            _salesperson_rows(
                [
                    {"nome": "Ana", "total_vendas": 3},
                    {"UNome": "Bruno", "quantidade": 1},
                ]
            ),
            [
                {"nome": "Ana", "quantidade": 3},
                {"nome": "Bruno", "quantidade": 1},
            ],
        )

    def test_builds_filter_options_from_xano_ids_and_labels(self) -> None:
        self.assertEqual(
            _filter_options(
                [
                    {"status_id": 2, "descricao": "Concluída", "total_vendas": 3},
                    {"status_id": 4, "descricao": "Cancelada", "total_vendas": 0},
                ],
                "status da venda",
                id_keys=("status_id", "id"),
                name_keys=("descricao", "Descricao_venda", "status"),
            ),
            [
                {"id": "2", "nome": "Concluída"},
                {"id": "4", "nome": "Cancelada"},
            ],
        )

    def test_rejects_filter_options_without_real_xano_identifiers(self) -> None:
        with self.assertRaisesRegex(XanoError, "identificador ou nome"):
            _filter_options(
                [{"descricao": "Concluída"}],
                "status da venda",
                id_keys=("status_id", "id"),
                name_keys=("descricao",),
            )

    def test_status_breakdown_uses_only_values_returned_by_xano(self) -> None:
        self.assertEqual(
            _sales_status_rows(
                [
                    {"status_id": 1, "descricao": "Pendente", "total_vendas": 2},
                    {
                        "status_id": 2,
                        "descricao": "Concluída",
                        "total_vendas": 1,
                        "valor_total": 1500,
                    },
                ]
            ),
            [
                {"nome": "Pendente", "quantidade": "2", "valor_total": ""},
                {
                    "nome": "Concluída",
                    "quantidade": "1",
                    "valor_total": "R$ 1.500,00",
                },
            ],
        )

    def test_builds_category_chart_rows(self) -> None:
        categories = [
            {"categoria": "Motor", "quantidade": 12, "valor_total": 3200.5},
            {"categoria": "Freios", "quantidade": 7, "valor_total": 900},
        ]
        self.assertEqual(
            _chart_rows(
                categories,
                "peças vendidas por categoria",
                name_key="categoria",
                value_key="quantidade",
                secondary_value_key="valor_total",
                max_categories=None,
            ),
            [
                {"nome": "Motor", "quantidade": 12.0, "valor_total": 3200.5},
                {"nome": "Freios", "quantidade": 7.0, "valor_total": 900.0},
            ],
        )

    def test_groups_daily_sales_into_weekly_monthly_and_yearly_series(self) -> None:
        daily = [
            {"periodo": "2026-01-01", "total_vendas": 1, "valor_total": 100},
            {"periodo": "2026-01-02", "total_vendas": 2, "valor_total": 250},
            {"periodo": "2026-02-01", "total_vendas": 1, "valor_total": 75},
        ]

        weekly = _trend_chart_rows(daily, "semana")
        monthly = _trend_chart_rows(daily, "mes")
        yearly = _trend_chart_rows(daily, "ano")

        self.assertEqual(len(weekly), 2)
        self.assertEqual(weekly[0]["valor_total"], 350)
        self.assertEqual(monthly, [
            {"periodo": "2026-01", "total_vendas": 3, "valor_total": 350},
            {"periodo": "2026-02", "total_vendas": 1, "valor_total": 75},
        ])
        self.assertEqual(yearly, [
            {"periodo": "2026", "total_vendas": 4, "valor_total": 425},
        ])

    def test_groups_raw_sale_timeline_rows_from_venda(self) -> None:
        timeline = [
            {"periodo": "2026-10-01T10:00:00Z", "total_vendas": 1, "valor_total": 100},
            {"periodo": "2026-10-01T15:00:00Z", "total_vendas": 1, "valor_total": 50},
        ]

        self.assertEqual(
            _trend_chart_rows(timeline, "dia"),
            [{"periodo": "2026-10-01", "total_vendas": 2, "valor_total": 150.0}],
        )

    def test_period_grouping_is_local_after_timeline_is_loaded(self) -> None:
        timeline = [
            {"data_venda": "2026-10-05T10:00:00Z", "Valor_final": 100},
            {"data_venda": "2026-10-06T10:00:00Z", "Valor_final": 200},
            {"data_venda": "2026-11-01T10:00:00Z", "Valor_final": 300},
        ]
        self.assertEqual(
            _trend_chart_rows(timeline, "mes"),
            [
                {"periodo": "2026-10", "total_vendas": 2, "valor_total": 300.0},
                {"periodo": "2026-11", "total_vendas": 1, "valor_total": 300.0},
            ],
        )
        self.assertEqual(
            _trend_chart_rows(timeline, "ano"),
            [{"periodo": "2026", "total_vendas": 3, "valor_total": 600.0}],
        )

    def test_accepts_data_venda_from_xano_timeline(self) -> None:
        timeline = [
            {
                "data_venda": "2026-10-02T12:30:00Z",
                "total_vendas": 1,
                "valor_total": 800,
            }
        ]

        self.assertEqual(
            _trend_chart_rows(timeline, "dia"),
            [{"periodo": "2026-10-02", "total_vendas": 1, "valor_total": 800.0}],
        )

    def test_accepts_raw_venda_fields_from_xano_timeline(self) -> None:
        self.assertEqual(
            _trend_chart_rows(
                [{"data_venda": "2026-10-03T12:30:00Z", "Valor_final": 950}],
                "dia",
            ),
            [{"periodo": "2026-10-03", "total_vendas": 1, "valor_total": 950.0}],
        )

    def test_accepts_nested_and_enveloped_timeline_response(self) -> None:
        self.assertEqual(
            _trend_chart_rows(
                {
                    "items": [
                        {
                            "venda": {
                                "data_venda": "2026-10-04T12:30:00Z",
                                "Valor_final": 1200,
                            }
                        }
                    ]
                },
                "dia",
            ),
            [{"periodo": "2026-10-04", "total_vendas": 1, "valor_total": 1200.0}],
        )

    def test_accepts_numeric_xano_timestamp_in_periodo(self) -> None:
        self.assertEqual(
            _trend_chart_rows(
                [{"periodo": 1791028800000, "total_vendas": 1, "valor_total": 300}],
                "dia",
            ),
            [{"periodo": "2026-10-03", "total_vendas": 1, "valor_total": 300.0}],
        )

    def test_builds_payment_chart_rows_from_xano_shape(self) -> None:
        self.assertEqual(
            _chart_rows(
                [
                    {"metodo": "PIX", "total_vendas": 4},
                    {"metodo": "Boleto", "total_vendas": 0},
                ],
                "pagamentos",
                name_key="metodo",
                value_key="total_vendas",
            ),
            [
                {"nome": "PIX", "quantidade": 4.0},
                {"nome": "Boleto", "quantidade": 0.0},
            ],
        )

    def test_preserves_zero_categories_returned_by_xano(self) -> None:
        self.assertEqual(
            _chart_rows(
                [
                    {"metodo": "PIX", "total_vendas": 0},
                    {"metodo": "Boleto", "total_vendas": 2},
                ],
                "pagamentos",
                name_key="metodo",
                value_key="total_vendas",
            ),
            [
                {"nome": "Boleto", "quantidade": 2.0},
                {"nome": "PIX", "quantidade": 0.0},
            ],
        )

    def test_colors_vehicle_status_chart_rows_by_status(self) -> None:
        self.assertEqual(
            _vehicle_status_chart_rows(
                [
                    {"descricao": "Disponível", "quantidade": 3},
                    {"descricao": "Reservado", "quantidade": 2},
                    {"descricao": "Vendido", "quantidade": 1},
                    {"descricao": "Em preparação", "quantidade": 0},
                ]
            ),
            [
                {"nome": "Disponível", "quantidade": 3.0, "cor": "#10b981"},
                {"nome": "Reservado", "quantidade": 2.0, "cor": "#f59e0b"},
                {"nome": "Vendido", "quantidade": 1.0, "cor": "#f43f5e"},
                {"nome": "Em preparação", "quantidade": 0.0, "cor": "#64748b"},
            ],
        )

    def test_detects_when_chart_rows_have_no_movement(self) -> None:
        self.assertFalse(_has_chart_values([{"nome": "PIX", "quantidade": 0.0}]))
        self.assertTrue(_has_chart_values([{"nome": "PIX", "quantidade": 1.0}]))

    def test_payment_chart_uses_only_positive_api_values(self) -> None:
        self.assertEqual(
            _payment_chart_rows(
                [
                    {"metodo": "PIX", "total_vendas": 3},
                    {"metodo": "Boleto", "total_vendas": 0},
                ]
            ),
            [{"nome": "PIX", "quantidade": 3.0}],
        )

    def test_accepts_enveloped_payment_rows_and_xano_field_variants(self) -> None:
        self.assertEqual(
            _chart_rows(
                {"data": [{"Metodo": "PIX", "quantidade": 3}]},
                "pagamentos",
                name_key="metodo",
                value_key="total_vendas",
            ),
            [{"nome": "PIX", "quantidade": 3.0}],
        )

    def test_accepts_payment_object_and_count_field_variants(self) -> None:
        self.assertEqual(
            _chart_rows(
                [{"forma_pagamento": {"Metodo": "PIX"}, "count": 4}],
                "pagamentos",
                name_key="metodo",
                value_key="total_vendas",
            ),
            [{"nome": "PIX", "quantidade": 4.0}],
        )

    def test_preserves_nested_indicator_payload_when_kpis_are_at_root(self) -> None:
        payload = {
            "kpis": {"vendas_pagas": 1},
            "data": {"vendas_por_forma_pagamento": [{"metodo": "PIX"}]},
        }
        self.assertEqual(
            payload["data"]["vendas_por_forma_pagamento"][0]["metodo"],
            "PIX",
        )

    def test_rejects_invalid_trend_periods_from_xano(self) -> None:
        with self.assertRaisesRegex(XanoError, "data inválida"):
            _trend_chart_rows(
                [{"periodo": "invalid", "total_vendas": 1, "valor_total": 1}],
                "dia",
            )

    def test_extracts_kpis_from_documented_and_current_xano_shapes(self) -> None:
        flat = {"vendas_pagas": 2}
        nested = {"kpis": flat}

        self.assertEqual(_extract_kpis(flat), flat)
        self.assertEqual(_extract_kpis(nested), flat)

    def test_extracts_analysis_series_from_nested_xano_payload(self) -> None:
        payload = {
            "data": {
                "vendas_por_forma_pagamento": [
                    {"metodo": "PIX", "total_vendas": 2}
                ]
            }
        }
        self.assertEqual(
            _extract_series(payload, "vendas_por_forma_pagamento"),
            payload["data"]["vendas_por_forma_pagamento"],
        )

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

    def test_omits_empty_dashboard_query_filters(self) -> None:
        self.assertEqual(
            _build_params("", "", is_manager=True),
            {},
        )
        self.assertEqual(
            _build_params(
                "",
                "",
                is_manager=True,
                status_id="todos",
                vendedor_id="todos",
                forma_pagamento_id="todos",
                tipo_item="todos",
                status_veiculo_id="todos",
            ),
            {},
        )


if __name__ == "__main__":
    unittest.main()
