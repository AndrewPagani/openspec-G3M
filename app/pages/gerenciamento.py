import reflex as rx

from app.components.app_shell import shell
from app.components.states import empty_state, feedback
from app.state.auth_state import AuthState
from app.state.dashboard_state import DashboardState


def _metric(
    title: str,
    value: rx.Var,
    detail: str = "",
    icon: str = "chart-no-axes-column-increasing",
    accent: str = "#3b82f6",
) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(title, class_name="dashboard-metric-label"),
                rx.heading(value, size="6", class_name="dashboard-metric-value"),
                rx.cond(detail != "", rx.text(detail, class_name="muted"), rx.fragment()),
                align="start",
                spacing="2",
                class_name="dashboard-metric-copy",
            ),
            rx.center(
                rx.icon(icon, size=20, color=accent, stroke_width=1.8),
                class_name="dashboard-metric-icon",
            ),
            align="start",
            justify="between",
            width="100%",
        ),
        class_name="dashboard-card dashboard-kpi",
        width="100%",
    )


def _sales_status_report() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Vendas por status", size="4"),
            rx.cond(
                DashboardState.vendas_por_status.length() > 0,
                rx.vstack(
                    rx.foreach(
                        DashboardState.vendas_por_status,
                        lambda row: rx.hstack(
                            rx.vstack(
                                rx.text(row["nome"], class_name="dashboard-breakdown-name"),
                                rx.text(
                                    "Total de vendas: " + row["quantidade"],
                                    class_name="dashboard-breakdown-detail",
                                ),
                                align="start",
                                spacing="1",
                            ),
                            rx.spacer(),
                            rx.cond(
                                row["valor_total"] != "",
                                rx.text(
                                    row["valor_total"],
                                    class_name="dashboard-breakdown-amount",
                                ),
                                rx.fragment(),
                            ),
                            align="center",
                            width="100%",
                            class_name="dashboard-breakdown-row",
                        ),
                    ),
                    align="start",
                    width="100%",
                ),
                empty_state("A API não retornou vendas agrupadas por status."),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _salespeople_report() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Vendas por vendedor", size="4"),
            rx.input(
                placeholder="Pesquisar vendedor pelo nome",
                aria_label="Pesquisar vendedor pelo nome",
                value=DashboardState.filtro_vendedor_nome,
                on_change=DashboardState.set_filtro_vendedor_nome,
                width="100%",
            ),
            rx.cond(
                DashboardState.vendedores_visiveis.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.foreach(
                            DashboardState.vendedores_visiveis,
                            lambda row: rx.text(row, class_name="report-row"),
                        ),
                        align="start",
                        width="100%",
                    ),
                    max_height="240px",
                    overflow_y="auto",
                    width="100%",
                ),
                empty_state("Nenhum vendedor encontrado."),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _chart_empty(rows: rx.Var, message: str) -> rx.Component:
    return rx.vstack(
        rx.callout(
            message,
            icon="info",
            color_scheme="gray",
            class_name="dashboard-empty-notice",
        ),
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


def _dashboard_empty(message: str) -> rx.Component:
    return rx.vstack(
        rx.icon("chart-no-axes-column-increasing", size=24, stroke_width=1.6),
        rx.text(message),
        align="center",
        justify="center",
        class_name="dashboard-empty-state",
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


def _filter_select(
    label: str,
    value: rx.Var,
    options: rx.Var,
    on_change,
) -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="dashboard-filter-label"),
        rx.select.root(
            rx.select.trigger(
                placeholder=label,
                aria_label=label,
                class_name="dashboard-filter-trigger",
            ),
            rx.select.content(
                rx.select.item("Todos", value="todos"),
                rx.foreach(
                    options,
                    lambda option: rx.select.item(
                        option["nome"],
                        value=option["id"],
                    ),
                ),
            ),
            value=value,
            on_change=on_change,
            disabled=options.length() == 0,
            class_name="dashboard-filter-select",
        ),
        align="start",
        spacing="2",
        class_name="dashboard-filter-field",
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
                    rx.recharts.x_axis(data_key="periodo_formatado"),
                    rx.recharts.y_axis(label={"value": "R$"}),
                    rx.recharts.tooltip(),
                    rx.recharts.area(
                        data_key="valor_total",
                        name="Valor (R$)",
                        stroke="#3b82f6",
                        fill="#3b82f6",
                        type="monotone",
                    ),
                    data=DashboardState.chart_vendas_por_periodo,
                    width="100%",
                    height=320,
                ),
                _dashboard_empty("Sem vendas para exibir no período selecionado."),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _vehicles_sold_by_brand_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Veículos vendidos por marca", size="4"),
            rx.text(
                "Quantidade de veículos vendidos por marca no período selecionado.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.chart_veiculos_vendidos_por_marca.length() > 0,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(
                        data_key="nome",
                        interval=0,
                        min_tick_gap=0,
                        text_anchor="middle",
                    ),
                    rx.recharts.y_axis(),
                    rx.recharts.tooltip(),
                    rx.recharts.bar(
                        rx.foreach(
                            DashboardState.chart_veiculos_vendidos_por_marca,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data_key="quantidade",
                        name="Veículos vendidos",
                        unit=" unidades",
                        fill="#10b981",
                        bar_size=40,
                        radius=[6, 6, 0, 0],
                    ),
                    data=DashboardState.chart_veiculos_vendidos_por_marca,
                    width="100%",
                    height=300,
                ),
                _dashboard_empty("Não há veículos vendidos por marca no período selecionado."),
            ),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _parts_sold_by_category_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Peças vendidas por categoria", size="4"),
            rx.text(
                "Quantidade de peças vendidas por categoria no período selecionado.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.chart_pecas_vendidas_por_categoria.length() > 0,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="nome"),
                    rx.recharts.y_axis(),
                    rx.recharts.tooltip(),
                    rx.recharts.bar(
                        rx.foreach(
                            DashboardState.chart_pecas_vendidas_por_categoria,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data_key="quantidade",
                        name="Peças vendidas",
                        unit=" unidades",
                        fill="#3b82f6",
                        bar_size=44,
                        radius=[6, 6, 0, 0],
                    ),
                    rx.recharts.y_axis(data_key="valor_total", y_axis_id="valor", hide=True),
                    rx.recharts.bar(
                        data_key="valor_total",
                        name="Valor total (R$)",
                        y_axis_id="valor",
                        fill="transparent",
                        stroke="transparent",
                        bar_size=44,
                        legend_type="none",
                    ),
                    data=DashboardState.chart_pecas_vendidas_por_categoria,
                    width="100%",
                    height=300,
                    bar_category_gap="5%",
                    bar_gap=0,
                ),
                _dashboard_empty("Não há peças vendidas por categoria no período selecionado."),
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
                DashboardState.chart_formas_pagamento.length() > 0,
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        rx.recharts.cell(fill="#3b82f6"),
                        rx.recharts.cell(fill="#10b981"),
                        rx.recharts.cell(fill="#8b5cf6"),
                        rx.recharts.cell(fill="#f59e0b"),
                        rx.recharts.cell(fill="#f43f5e"),
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
                rx.callout(
                    "A API não retornou vendas com quantidade positiva por forma de pagamento "
                    "para o período selecionado.",
                    icon="info",
                    color_scheme="gray",
                    class_name="dashboard-empty-notice",
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
                        fill="#8b5cf6",
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


def _low_stock_parts() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Peças sem estoque ou com estoque baixo", size="4"),
            rx.text(
                "Itens com quantidade disponível igual ou inferior a 5.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.pecas_baixo_estoque_labels.length() > 0,
                rx.vstack(
                    rx.foreach(
                        DashboardState.pecas_baixo_estoque_labels,
                        lambda label: rx.text(label, class_name="report-row"),
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.text(
                    "Nenhuma peça com estoque igual ou inferior a 5.",
                    class_name="muted",
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
                    _filter_select(
                        "Status da venda",
                        DashboardState.filtro_status_id,
                        DashboardState.status_venda_opcoes,
                        DashboardState.set_filtro_status_id,
                    ),
                    _filter_select(
                        "Vendedor",
                        DashboardState.filtro_vendedor_id,
                        DashboardState.vendedor_opcoes,
                        DashboardState.set_filtro_vendedor_id,
                    ),
                    _filter_select(
                        "Forma de pagamento",
                        DashboardState.filtro_forma_pagamento_id,
                        DashboardState.forma_pagamento_opcoes,
                        DashboardState.set_filtro_forma_pagamento_id,
                    ),
                    rx.select.root(
                        rx.select.trigger(
                            placeholder="Tipo de item",
                            aria_label="Tipo de item",
                            class_name="dashboard-filter-trigger",
                        ),
                        rx.select.content(
                            rx.select.item("Todos os tipos", value="todos"),
                            rx.select.item("Veículo", value="veiculo"),
                            rx.select.item("Peça", value="peca"),
                        ),
                        value=DashboardState.filtro_tipo_item,
                        on_change=DashboardState.set_filtro_tipo_item,
                        class_name="dashboard-filter-select",
                    ),
                    _filter_select(
                        "Status do veículo",
                        DashboardState.filtro_status_veiculo_id,
                        DashboardState.status_veiculo_opcoes,
                        DashboardState.set_filtro_status_veiculo_id,
                    ),
                    columns="repeat(5, minmax(0, 1fr))",
                    spacing="3",
                    width="100%",
                    class_name="dashboard-filters-grid",
                ),
                rx.hstack(
                    rx.icon("info", size=14, stroke_width=1.8),
                    rx.text(
                        "O Xano aplica o escopo de autorização por perfil; filtros "
                        "adicionais refinam os indicadores conforme o contrato atual.",
                        class_name="dashboard-filter-note",
                    ),
                    align="center",
                    spacing="2",
                    class_name="dashboard-filter-disclaimer",
                ),
                align="start",
                width="100%",
            ),
            class_name="dashboard-card dashboard-filter-panel",
            width="100%",
        ),
        rx.fragment(),
    )


def gerenciamento() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Vendas", size="6"),
                    align="start",
                    spacing="1",
                    class_name="dashboard-heading",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        "Exportar CSV",
                        on_click=DashboardState.export_csv,
                        variant="outline",
                        class_name="dashboard-export-button",
                    ),
                    rx.vstack(
                        rx.text("Data inicial", class_name="dashboard-filter-label"),
                        rx.input(
                            type="date",
                            aria_label="Data inicial",
                            value=DashboardState.data_inicio,
                            on_change=DashboardState.set_data_inicio,
                        ),
                        align="start",
                        spacing="1",
                        class_name="dashboard-date-field",
                    ),
                    rx.vstack(
                        rx.text("Data final", class_name="dashboard-filter-label"),
                        rx.input(
                            type="date",
                            aria_label="Data final",
                            value=DashboardState.data_fim,
                            on_change=DashboardState.set_data_fim,
                        ),
                        align="start",
                        spacing="1",
                        class_name="dashboard-date-field",
                    ),
                    rx.button(
                        rx.cond(DashboardState.loading, "Carregando…", "Atualizar dados"),
                        on_click=DashboardState.load,
                        disabled=DashboardState.loading,
                        class_name="dashboard-refresh-button",
                    ),
                    align="end",
                    wrap="wrap",
                    class_name="dashboard-header-actions",
                ),
                align="center",
                width="100%",
                wrap="wrap",
                class_name="dashboard-header",
            ),
            _filters(),
            feedback(DashboardState.error, DashboardState.loading),
            rx.grid(
                _metric(
                    "Vendas no período",
                    DashboardState.total_vendas,
                    "Total de vendas filtradas",
                    "shopping-cart",
                    "#60a5fa",
                ),
                _metric(
                    "Faturamento recebido",
                    DashboardState.valor_liquido,
                    "Baixas registradas no período",
                    "banknote",
                    "#10b981",
                ),
                _metric(
                    "Vendas pagas",
                    DashboardState.vendas_pagas,
                    "Transações com baixa registrada",
                    "badge-check",
                    "#818cf8",
                ),
                _metric(
                    "Ticket médio",
                    DashboardState.ticket_medio,
                    "Valor bruto dividido pela quantidade",
                    "receipt",
                    "#22d3ee",
                ),
                _metric(
                    "Valor bruto vendido",
                    DashboardState.valor_bruto,
                    "Total bruto no período",
                    "chart-no-axes-column-increasing",
                    "#a78bfa",
                ),
                _metric(
                    "Cancelamentos",
                    DashboardState.percentual_canceladas,
                    DashboardState.vendas_canceladas + " vendas canceladas",
                    "circle-alert",
                    "#f59e0b",
                ),
                columns=rx.breakpoints(
                    initial="1fr",
                    sm="repeat(2, minmax(0, 1fr))",
                    lg="repeat(3, minmax(0, 1fr))",
                ),
                spacing="4",
                width="100%",
                class_name="dashboard-kpi-grid",
            ),
            _trend_chart(),
            rx.grid(
                _payment_chart(),
                _mix_chart(),
                columns=rx.breakpoints(initial="1fr", lg="repeat(2, minmax(0, 1fr))"),
                spacing="4",
                width="100%",
                class_name="dashboard-analytics-grid",
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
                            "car-front",
                            "#10b981",
                        ),
                        _metric(
                            "Peças disponíveis",
                            DashboardState.pecas_disponiveis,
                            DashboardState.valor_estoque_pecas + " em valor de estoque",
                            "boxes",
                            "#60a5fa",
                        ),
                        _metric(
                            "Peças sem estoque / baixo estoque",
                            DashboardState.pecas_sem_estoque,
                            "Itens com quantidade igual ou inferior a 5",
                            "package-x",
                            "#f59e0b",
                        ),
                        columns=rx.breakpoints(
                            initial="1fr",
                            sm="repeat(2, minmax(0, 1fr))",
                            lg="repeat(3, minmax(0, 1fr))",
                        ),
                        spacing="4",
                        width="100%",
                        class_name="dashboard-kpi-grid",
                    ),
                    rx.grid(
                        _vehicle_status_chart(),
                        _low_stock_parts(),
                        columns=rx.breakpoints(
                            initial="1fr", lg="repeat(2, minmax(0, 1fr))"
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    align="start",
                    width="100%",
                    class_name="dashboard-stock-section",
                ),
                rx.fragment(),
            ),
            rx.vstack(
                rx.heading("Detalhamento de vendas", size="5"),
                rx.grid(
                    _vehicles_sold_by_brand_chart(),
                    _parts_sold_by_category_chart(),
                    _sales_status_report(),
                    rx.cond(AuthState.is_manager, _salespeople_report(), rx.fragment()),
                    columns=rx.breakpoints(initial="1fr", lg="repeat(2, minmax(0, 1fr))"),
                    spacing="4",
                    width="100%",
                ),
                align="start",
                width="100%",
                class_name="dashboard-breakdown-section",
            ),
            on_mount=DashboardState.load,
            class_name="page-stack dashboard-page",
            width="100%",
        ),
        "Dashboard",
        allowed=AuthState.authenticated,
    )
