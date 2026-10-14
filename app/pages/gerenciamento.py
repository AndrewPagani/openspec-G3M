import reflex as rx

from app.components.app_shell import shell
from app.components.states import empty_state, feedback
from app.state.auth_state import AuthState
from app.state.dashboard_state import DashboardState


def _metric(title: str, value: rx.Var, detail: str = "") -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(title, class_name="dashboard-metric-label"),
            rx.heading(value, size="6", class_name="dashboard-metric-value"),
            rx.cond(detail != "", rx.text(detail, class_name="muted"), rx.fragment()),
            align="start",
            spacing="2",
            width="100%",
        ),
        class_name="dashboard-card dashboard-kpi",
        width="100%",
    )


def _report(title: str, rows: rx.Var, description: str = "") -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(title, size="4"),
            rx.cond(description != "", rx.text(description, class_name="muted"), rx.fragment()),
            rx.cond(
                rows.length() > 0,
                rx.vstack(
                    rx.foreach(rows, lambda row: rx.text(row, class_name="report-row")),
                    align="start",
                    width="100%",
                ),
                empty_state("Sem dados para o período selecionado."),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _chart_empty(rows: rx.Var, message: str) -> rx.Component:
    return rx.vstack(
        rx.callout(message, icon="info", color_scheme="gray"),
        rx.cond(
            rows.length() > 0,
            rx.vstack(
                rx.text("Valores retornados pela API:", class_name="muted"),
                rx.foreach(
                    rows,
                    lambda row: rx.hstack(
                        rx.text(row["nome"]),
                        rx.text(":"),
                        rx.text(row["quantidade"]),
                        class_name="report-row",
                    ),
                ),
                align="start",
                width="100%",
            ),
            rx.fragment(),
        ),
        align="start",
        width="100%",
    )


def _unsupported_analysis(title: str, reason: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(title, size="4"),
            rx.text(reason, class_name="muted"),
            rx.callout(
                "Este indicador não é fornecido pelo endpoint de indicadores atual.",
                icon="info",
                color_scheme="gray",
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card dashboard-unavailable",
        width="100%",
    )


def _period_button(label: str, value: str) -> rx.Component:
    return rx.button(
        label,
        on_click=DashboardState.set_periodo(value),
        variant=rx.cond(DashboardState.periodo_ativo == value, "solid", "soft"),
    )


def _trend_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Evolução das vendas", size="4"),
                    rx.text(
                        "Valor total registrado por período, conforme retornado pelo Xano.",
                        class_name="muted",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    _period_button("Dia", "dia"),
                    _period_button("Semana", "semana"),
                    _period_button("Mês", "mes"),
                    _period_button("Ano", "ano"),
                    class_name="dashboard-periods",
                ),
                align="center",
                width="100%",
                wrap="wrap",
            ),
            rx.cond(
                DashboardState.chart_vendas_por_periodo.length() > 0,
                rx.recharts.area_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="periodo"),
                    rx.recharts.y_axis(),
                    rx.recharts.tooltip(),
                    rx.recharts.area(
                        data_key="valor_total",
                        name="Valor registrado",
                        stroke="#0f766e",
                        fill="#99f6e4",
                        type="monotone",
                    ),
                    data=DashboardState.chart_vendas_por_periodo,
                    width="100%",
                    height=320,
                ),
                empty_state("Sem vendas para exibir no período selecionado."),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _payment_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Vendas por forma de pagamento", size="4"),
            rx.text(
                "Distribuição por quantidade de vendas; valores financeiros por método não são retornados.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.pagamentos_com_movimento,
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        rx.recharts.cell(fill="#0f766e"),
                        rx.recharts.cell(fill="#2563eb"),
                        rx.recharts.cell(fill="#7c3aed"),
                        rx.recharts.cell(fill="#ea580c"),
                        rx.recharts.cell(fill="#db2777"),
                        data=DashboardState.chart_formas_pagamento,
                        data_key="quantidade",
                        name_key="nome",
                        inner_radius=58,
                        outer_radius=92,
                        padding_angle=2,
                    ),
                    rx.recharts.tooltip(),
                    rx.recharts.legend(),
                    width="100%",
                    height=300,
                ),
                _chart_empty(
                    DashboardState.chart_formas_pagamento,
                    "Não há quantidades de vendas por método para desenhar no período "
                    "selecionado. Verifique as vendas e o intervalo de datas no Xano.",
                ),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _mix_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Mix de itens vendidos", size="4"),
            rx.text(
                "Quantidade de veículos e peças; não representa faturamento por categoria.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.mix_com_movimento,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="nome"),
                    rx.recharts.y_axis(),
                    rx.recharts.tooltip(),
                    rx.recharts.bar(
                        data_key="quantidade",
                        name="Quantidade",
                        fill="#2563eb",
                        radius=[6, 6, 0, 0],
                    ),
                    data=DashboardState.chart_mix_itens,
                    width="100%",
                    height=300,
                ),
                _chart_empty(
                    DashboardState.chart_mix_itens,
                    "Não há quantidade de itens vendidos para desenhar no período "
                    "selecionado. Verifique as vendas e o intervalo de datas no Xano.",
                ),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _vehicle_status_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Estoque de veículos por status", size="4"),
            rx.text("Quantidade atual de veículos agrupada pelo status.", class_name="muted"),
            rx.cond(
                DashboardState.estoque_com_movimento,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="nome"),
                    rx.recharts.y_axis(),
                    rx.recharts.tooltip(),
                    rx.recharts.bar(
                        rx.foreach(
                            DashboardState.chart_veiculos_por_status,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data_key="quantidade",
                        name="Veículos",
                        radius=[6, 6, 0, 0],
                    ),
                    data=DashboardState.chart_veiculos_por_status,
                    width="100%",
                    height=300,
                ),
                _chart_empty(
                    DashboardState.chart_veiculos_por_status,
                    "Não há quantidade de veículos por status para desenhar. Verifique "
                    "o cadastro de veículos no Xano.",
                ),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _filters() -> rx.Component:
    return rx.cond(
        AuthState.is_manager,
        rx.card(
            rx.vstack(
                rx.heading("Filtros de análise", size="4"),
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
                    "Os filtros por ID são opcionais. O escopo das vendas de cada perfil "
                    "continua limitado pelas regras de autorização do Xano. O tipo de item "
                    "afeta o mix; os outros totais permanecem conforme a agregação atual do Xano.",
                    class_name="muted",
                ),
                align="start",
                width="100%",
            ),
            class_name="dashboard-card",
            width="100%",
        ),
        rx.fragment(),
    )


def gerenciamento() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Dashboard de Vendas - Concessionária", size="6"),
                    rx.text(
                        "Acompanhe vendas, recebimentos e estoque com dados do Xano.",
                        class_name="muted",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.button(
                    "Exportar CSV",
                    on_click=DashboardState.export_csv,
                    variant="outline",
                ),
                align="center",
                width="100%",
                wrap="wrap",
            ),
            rx.card(
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
                    rx.spacer(),
                    rx.button(
                        rx.cond(DashboardState.loading, "Carregando…", "Atualizar dados"),
                        on_click=DashboardState.load,
                        disabled=DashboardState.loading,
                    ),
                    align="end",
                    class_name="toolbar",
                    width="100%",
                    wrap="wrap",
                ),
                class_name="dashboard-card",
                width="100%",
            ),
            _filters(),
            feedback(DashboardState.error, DashboardState.loading),
            rx.grid(
                _metric(
                    "Faturamento recebido",
                    DashboardState.valor_liquido,
                    "Baixas registradas no período",
                ),
                _metric(
                    "Vendas pagas",
                    DashboardState.vendas_pagas,
                    "Transações com baixa registrada",
                ),
                _metric(
                    "Ticket médio",
                    DashboardState.ticket_medio,
                    "Média das vendas pagas",
                ),
                _metric(
                    "Cancelamentos",
                    DashboardState.percentual_canceladas,
                    DashboardState.vendas_canceladas + " vendas canceladas",
                ),
                columns=rx.breakpoints(
                    initial="1fr",
                    sm="repeat(2, minmax(0, 1fr))",
                    lg="repeat(4, minmax(0, 1fr))",
                ),
                spacing="4",
                width="100%",
            ),
            _trend_chart(),
            rx.grid(
                _payment_chart(),
                _mix_chart(),
                columns=rx.breakpoints(initial="1fr", lg="repeat(2, minmax(0, 1fr))"),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                AuthState.is_manager,
                rx.vstack(
                    rx.heading("Estoque e análises adicionais", size="5"),
                    rx.grid(
                        _metric(
                            "Veículos disponíveis",
                            DashboardState.veiculos_disponiveis,
                            DashboardState.valor_veiculos + " em valor de estoque",
                        ),
                        _metric(
                            "Peças disponíveis",
                            DashboardState.pecas_disponiveis,
                            DashboardState.valor_estoque_pecas + " em valor de estoque",
                        ),
                        _metric("Peças sem estoque", DashboardState.pecas_sem_estoque),
                        _vehicle_status_chart(),
                        _unsupported_analysis(
                            "Conversão e giro de estoque",
                            "O Xano não retorna quantidade de propostas ou histórico de entradas "
                            "e saídas de estoque para calcular estas taxas.",
                        ),
                        _unsupported_analysis(
                            "Veículos vendidos por marca",
                            "O endpoint atual não relaciona os itens vendidos à marca do veículo "
                            "nem retorna faturamento ou participação por marca.",
                        ),
                        _unsupported_analysis(
                            "Peças por categoria e fabricante",
                            "O schema de peças atual não contém categoria nem marca do fabricante "
                            "ou vínculo com a marca do veículo de destino.",
                        ),
                        _unsupported_analysis(
                            "Canal de venda x forma de pagamento",
                            "O schema de venda não registra canal (balcão, oficina, atacado ou "
                            "e-commerce), então não há base para esse comparativo.",
                        ),
                        columns=rx.breakpoints(
                            initial="1fr", lg="repeat(2, minmax(0, 1fr))"
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    align="start",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.grid(
                _report("Vendas por status", DashboardState.vendas_por_status),
                _report("Vendas por vendedor", DashboardState.vendas_por_vendedor),
                columns=rx.breakpoints(initial="1fr", lg="repeat(2, minmax(0, 1fr))"),
                spacing="4",
                width="100%",
            ),
            on_mount=DashboardState.load,
            class_name="page-stack dashboard-page",
            width="100%",
        ),
        "Dashboard",
        allowed=AuthState.authenticated,
    )
