import reflex as rx

from app.components.app_shell import shell
from app.components.states import empty_state, feedback
from app.state.auth_state import AuthState
from app.state.dashboard_state import DashboardState


def _metric(title: str, value: rx.Var) -> rx.Component:
    return rx.card(
        rx.text(title, class_name="muted"),
        rx.heading(value, size="6"),
        width="100%",
    )


def _report(title: str, rows: rx.Var) -> rx.Component:
    return rx.card(
        rx.heading(title, size="4"),
        rx.cond(
            rows.length() > 0,
            rx.vstack(
                rx.foreach(rows, lambda row: rx.text(row, class_name="report-row")),
                align="start",
                width="100%",
            ),
            empty_state("Sem dados para o período selecionado."),
        ),
        width="100%",
    )


def gerenciamento() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Data inicial", class_name="muted"),
                    rx.input(
                        type="date",
                        value=DashboardState.data_inicio,
                        on_change=DashboardState.set_data_inicio,
                    ),
                    align="start",
                ),
                rx.vstack(
                    rx.text("Data final", class_name="muted"),
                    rx.input(
                        type="date",
                        value=DashboardState.data_fim,
                        on_change=DashboardState.set_data_fim,
                    ),
                    align="start",
                ),
                rx.button(
                    "Atualizar indicadores",
                    on_click=DashboardState.load,
                    disabled=DashboardState.loading,
                ),
                align="end",
                class_name="toolbar",
                width="100%",
            ),
            rx.cond(
                AuthState.is_manager,
                rx.card(
                    rx.vstack(
                        rx.heading("Filtros", size="4"),
                        rx.grid(
                            rx.input(
                                type="number",
                                min="1",
                                placeholder="ID do status da venda",
                                aria_label="ID do status da venda",
                                value=DashboardState.filtro_status_id,
                                on_change=DashboardState.set_filtro_status_id,
                            ),
                            rx.input(
                                type="number",
                                min="1",
                                placeholder="ID do vendedor",
                                aria_label="ID do vendedor",
                                value=DashboardState.filtro_vendedor_id,
                                on_change=DashboardState.set_filtro_vendedor_id,
                            ),
                            rx.input(
                                type="number",
                                min="1",
                                placeholder="ID da forma de pagamento",
                                aria_label="ID da forma de pagamento",
                                value=DashboardState.filtro_forma_pagamento_id,
                                on_change=DashboardState.set_filtro_forma_pagamento_id,
                            ),
                            rx.select.root(
                                rx.select.trigger(placeholder="Tipo de item"),
                                rx.select.content(
                                    rx.select.item("Veículo", value="veiculo"),
                                    rx.select.item("Peça", value="peca"),
                                ),
                                value=DashboardState.filtro_tipo_item,
                                on_change=DashboardState.set_filtro_tipo_item,
                                width="100%",
                            ),
                            rx.input(
                                type="number",
                                min="1",
                                placeholder="ID do status do veículo",
                                aria_label="ID do status do veículo",
                                value=DashboardState.filtro_status_veiculo_id,
                                on_change=DashboardState.set_filtro_status_veiculo_id,
                            ),
                            columns="repeat(auto-fit, minmax(190px, 1fr))",
                            spacing="3",
                            width="100%",
                        ),
                        rx.text(
                            "Os filtros por ID são opcionais. O vendedor não pode "
                            "definir outro vendedor nem ampliar o escopo autorizado.",
                            class_name="muted",
                        ),
                        align="start",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.fragment(),
            ),
            feedback(DashboardState.error, DashboardState.loading),
            rx.vstack(
                rx.heading("Visão geral", size="5"),
                rx.grid(
                    _metric("Vendas no período", DashboardState.total_vendas),
                    _metric("Valor líquido recebido", DashboardState.valor_liquido),
                    _metric("Vendas pagas", DashboardState.vendas_pagas),
                    _metric("Ticket médio", DashboardState.ticket_medio),
                    _metric("Descontos concedidos", DashboardState.descontos),
                    _metric("Valor bruto vendido", DashboardState.valor_bruto),
                    _metric("Vendas canceladas", DashboardState.vendas_canceladas),
                    _metric("Cancelamentos", DashboardState.percentual_canceladas),
                    columns="repeat(auto-fit, minmax(190px, 1fr))",
                    spacing="4",
                    width="100%",
                ),
                align="start",
                width="100%",
            ),
            rx.cond(
                AuthState.is_manager,
                rx.vstack(
                    rx.vstack(
                        rx.heading("Vendas", size="5"),
                        rx.grid(
                            _report("Vendas por período", DashboardState.vendas_por_periodo),
                            _report("Vendas por status", DashboardState.vendas_por_status),
                            _report("Formas de pagamento", DashboardState.vendas_por_pagamento),
                            _report("Vendas por vendedor", DashboardState.vendas_por_vendedor),
                            _report("Mix de itens", DashboardState.mix_itens),
                            columns="repeat(auto-fit, minmax(300px, 1fr))",
                            spacing="4",
                            width="100%",
                        ),
                        align="start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.heading("Veículos", size="5"),
                        rx.grid(
                            _metric("Veículos disponíveis", DashboardState.veiculos_disponiveis),
                            _metric("Valor dos veículos disponíveis", DashboardState.valor_veiculos),
                            _report("Estoque por status", DashboardState.veiculos_por_status),
                            columns="repeat(auto-fit, minmax(240px, 1fr))",
                            spacing="4",
                            width="100%",
                        ),
                        align="start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.heading("Peças", size="5"),
                        rx.grid(
                            _metric("Peças disponíveis", DashboardState.pecas_disponiveis),
                            _metric("Valor do estoque", DashboardState.valor_estoque_pecas),
                            _metric("Peças sem estoque", DashboardState.pecas_sem_estoque),
                            columns="repeat(auto-fit, minmax(240px, 1fr))",
                            spacing="4",
                            width="100%",
                        ),
                        align="start",
                        width="100%",
                    ),
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.heading("Suas vendas", size="5"),
                    rx.grid(
                        _report("Suas vendas por período", DashboardState.vendas_por_periodo),
                        _report("Suas vendas por status", DashboardState.vendas_por_status),
                        _report("Suas formas de pagamento", DashboardState.vendas_por_pagamento),
                        _report("Mix dos seus itens vendidos", DashboardState.mix_itens),
                        columns="repeat(auto-fit, minmax(300px, 1fr))",
                        spacing="4",
                        width="100%",
                    ),
                    align="start",
                    width="100%",
                ),
            ),
            on_mount=DashboardState.load,
            class_name="page-stack",
            width="100%",
        ),
        "Dashboard",
        allowed=AuthState.authenticated,
    )
