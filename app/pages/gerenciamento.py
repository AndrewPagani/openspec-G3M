import reflex as rx

from app.components.app_shell import shell
from app.components.states import feedback
from app.state.auth_state import AuthState
from app.state.dashboard_state import DashboardState
from app.state.settings_state import SettingsState

_BRL = "new Intl.NumberFormat('pt-BR', {style: 'currency', currency: 'BRL'}).format"
_INTEGER = "new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 0}).format"
_MONEY_TICK = "(value) => 'R$ ' + new Intl.NumberFormat('pt-BR', {notation: 'compact', maximumFractionDigits: 1}).format(value)"
_METRIC_NEUTRAL = "var(--app-metric-neutral, #94a3b8)"
_METRIC_WARNING = "var(--app-metric-warning, #f59e0b)"
_CHART_PRIMARY = "var(--app-chart-primary, #60a5fa)"


def _tooltip(*, money: bool = False, with_total: bool = False) -> rx.Component:
    value = f"{_BRL if money else _INTEGER}(value)"
    if with_total:
        value += f" + (item?.payload?.valor_total != null ? ' · Valor total: ' + {_BRL}(item.payload.valor_total) : '')"
    return rx.recharts.tooltip(
        content_style={
            "background": "var(--app-surface, #172033)",
            "border": "1px solid var(--app-border-strong, #475569)",
            "borderRadius": "10px",
            "color": "var(--app-text, #f1f5f9)",
            "fontSize": "13px",
            "maxWidth": "min(320px, 80vw)",
            "whiteSpace": "normal",
        },
        item_style={
            "color": "var(--app-text-secondary, #e2e8f0)",
            "whiteSpace": "normal",
        },
        label_style={
            "color": "var(--app-text, #f1f5f9)",
            "fontWeight": 600,
        },
        cursor={
            "fill": "rgba(148, 163, 184, 0.06)",
            "stroke": "var(--app-border-strong, #64748b)",
        },
        is_animation_active=False,
        custom_attrs={
            "formatter": rx.Var(_js_expr=f"(value, name, item) => [{value}, name]")
        },
    )


def _count_axis() -> rx.Component:
    return rx.recharts.y_axis(
        allow_decimals=False,
        axis_line=False,
        tick_line=False,
        width=44,
        tick_formatter=f"(value) => {_INTEGER}(value)",
        tick={"fontSize": 12},
    )


def _chart_data(rows: rx.Var, *, parts: bool = False, unit: str = "unidades") -> rx.Component:
    """Text alternative keeps full category names available to touch and keyboard."""
    return rx.el.details(
        rx.el.summary("Ver dados do gráfico"),
        rx.foreach(
            rows,
            lambda row: rx.hstack(
                rx.text(row["nome"], class_name="dashboard-data-name"),
                rx.vstack(
                    rx.text(row["quantidade"], " ", unit),
                    rx.cond(
                        row["valor_formatado"] != "",
                        rx.text(row["valor_formatado"]),
                        rx.fragment(),
                    )
                    if parts
                    else rx.fragment(),
                    align="end",
                    spacing="1",
                    class_name="dashboard-data-value",
                ),
                justify="between",
                align="start",
                width="100%",
                class_name="dashboard-data-row",
            ),
        ),
        class_name="dashboard-chart-data",
        hidden=rows.length() == 0,
    )


def _metric(
    title: str,
    value: rx.Var,
    detail: str = "",
    icon: str = "chart-no-axes-column-increasing",
    accent: str = _METRIC_NEUTRAL,
) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(title, class_name="dashboard-metric-label"),
                rx.text(value, class_name="dashboard-metric-value"),
                rx.cond(
                    detail != "", rx.text(detail, class_name="muted"), rx.fragment()
                ),
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
            rx.heading("Vendas por status", size="4", as_="h2"),
            rx.cond(
                DashboardState.vendas_por_status.length() > 0,
                rx.vstack(
                    rx.foreach(
                        DashboardState.vendas_por_status,
                        lambda row: rx.hstack(
                            rx.vstack(
                                rx.text(
                                    row["nome"], class_name="dashboard-breakdown-name"
                                ),
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
                _dashboard_empty("Sem vendas por status no período selecionado."),
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
            rx.heading("Vendas por vendedor", size="4", as_="h2"),
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
                _dashboard_empty("Nenhum vendedor encontrado. Revise o nome pesquisado ou o período."),
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
                rx.text("Quantidades registradas:", class_name="muted"),
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
            rx.heading(title, size="4", as_="h2"),
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
        aria_pressed=DashboardState.periodo_ativo == value,
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
                    rx.heading("Evolução das vendas", size="4", as_="h2"),
                    rx.text(
                        "Valor vendido ao longo do período selecionado.",
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
                    rx.recharts.x_axis(
                        data_key="periodo_formatado",
                        axis_line=False,
                        tick_line=False,
                        min_tick_gap=32,
                        tick={"fontSize": 12},
                    ),
                    rx.recharts.y_axis(
                        tick_formatter=_MONEY_TICK,
                        axis_line=False,
                        tick_line=False,
                        width=76,
                        tick={"fontSize": 12},
                    ),
                    _tooltip(money=True),
                    rx.recharts.area(
                        data_key="valor_total",
                        name="Valor (R$)",
                        stroke=_CHART_PRIMARY,
                        fill=_CHART_PRIMARY,
                        custom_attrs={"fillOpacity": 0.12},
                        stroke_width=2,
                        is_animation_active=False,
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
            rx.heading("Veículos vendidos por marca", size="4", as_="h2"),
            rx.text(
                "Quantidade de veículos vendidos por marca no período selecionado.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.chart_veiculos_vendidos_por_marca.length() > 0,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(
                        type_="number",
                        allow_decimals=False,
                        axis_line=False,
                        tick_line=False,
                        tick_formatter=f"(value) => {_INTEGER}(value)",
                    ),
                    rx.recharts.y_axis(
                        data_key="nome",
                        type_="category",
                        width=110,
                        axis_line=False,
                        tick_line=False,
                        interval=0,
                        tick={"fontSize": 12},
                        tick_formatter="(value) => value.length > 16 ? value.slice(0, 15) + '…' : value",
                    ),
                    _tooltip(),
                    rx.recharts.bar(
                        rx.foreach(
                            DashboardState.chart_veiculos_vendidos_por_marca,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data_key="quantidade",
                        name="Veículos vendidos",
                        unit=" unidades",
                        fill=_CHART_PRIMARY,
                        bar_size=20,
                        radius=[0, 4, 4, 0],
                        is_animation_active=False,
                    ),
                    data=DashboardState.chart_veiculos_vendidos_por_marca,
                    width="100%",
                    height=DashboardState.chart_veiculos_vendidos_por_marca.length()
                    * 40
                    + 60,
                    layout="vertical",
                ),
                _dashboard_empty(
                    "Não há veículos vendidos por marca no período selecionado."
                ),
            ),
            _chart_data(DashboardState.chart_veiculos_vendidos_por_marca),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _parts_sold_by_category_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Peças vendidas por categoria", size="4", as_="h2"),
            rx.text(
                "Quantidade de peças vendidas por categoria no período selecionado.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.chart_pecas_vendidas_por_categoria.length() > 0,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(
                        type_="number",
                        allow_decimals=False,
                        axis_line=False,
                        tick_line=False,
                        tick_formatter=f"(value) => {_INTEGER}(value)",
                    ),
                    rx.recharts.y_axis(
                        data_key="nome",
                        type_="category",
                        width=110,
                        axis_line=False,
                        tick_line=False,
                        interval=0,
                        tick={"fontSize": 12},
                        tick_formatter="(value) => value.length > 16 ? value.slice(0, 15) + '…' : value",
                    ),
                    _tooltip(with_total=True),
                    rx.recharts.bar(
                        rx.foreach(
                            DashboardState.chart_pecas_vendidas_por_categoria,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data_key="quantidade",
                        name="Peças vendidas",
                        fill=_CHART_PRIMARY,
                        bar_size=20,
                        radius=[0, 4, 4, 0],
                        is_animation_active=False,
                    ),
                    data=DashboardState.chart_pecas_vendidas_por_categoria,
                    width="100%",
                    height=DashboardState.chart_pecas_vendidas_por_categoria.length()
                    * 40
                    + 60,
                    layout="vertical",
                ),
                _dashboard_empty(
                    "Não há peças vendidas por categoria no período selecionado."
                ),
            ),
            _chart_data(DashboardState.chart_pecas_vendidas_por_categoria, parts=True),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _payment_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Vendas por forma de pagamento", size="4", as_="h2"),
            rx.text(
                "Quantidade de vendas por forma de pagamento.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.chart_formas_pagamento.length() > 0,
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        rx.foreach(
                            DashboardState.chart_formas_pagamento,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data=DashboardState.chart_formas_pagamento,
                        data_key="quantidade",
                        name_key="nome",
                        inner_radius=58,
                        outer_radius=92,
                        padding_angle=2,
                        stroke="var(--app-surface, #0f172a)",
                        is_animation_active=False,
                    ),
                    _tooltip(),
                    rx.recharts.legend(icon_type="circle", icon_size=8),
                    width="100%",
                    height=300,
                ),
                rx.callout(
                    "Sem vendas por forma de pagamento no período selecionado.",
                    icon="info",
                    color_scheme="gray",
                    class_name="dashboard-empty-notice",
                ),
            ),
            _chart_data(DashboardState.chart_formas_pagamento, unit="vendas"),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _mix_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Mix de itens vendidos", size="4", as_="h2"),
            rx.text(
                "Comparação entre quantidades de veículos e peças vendidas.",
                class_name="muted",
            ),
            rx.cond(
                DashboardState.mix_com_movimento,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="nome"),
                    _count_axis(),
                    _tooltip(),
                    rx.recharts.bar(
                        data_key="quantidade",
                        name="Quantidade",
                        fill=_CHART_PRIMARY,
                        max_bar_size=64,
                        is_animation_active=False,
                        radius=[6, 6, 0, 0],
                    ),
                    data=DashboardState.chart_mix_itens,
                    width="100%",
                    height=300,
                ),
                _chart_empty(
                    DashboardState.chart_mix_itens,
                    "Sem itens vendidos no período selecionado. Experimente outro intervalo de datas.",
                ),
            ),
            _chart_data(DashboardState.chart_mix_itens),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _vehicle_status_chart() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Estoque de veículos por status", size="4", as_="h2"),
            rx.text(
                "Quantidade atual de veículos agrupada pelo status.", class_name="muted"
            ),
            rx.cond(
                DashboardState.estoque_com_movimento,
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="nome"),
                    _count_axis(),
                    _tooltip(),
                    rx.recharts.bar(
                        rx.foreach(
                            DashboardState.chart_veiculos_por_status,
                            lambda row: rx.recharts.cell(fill=row["cor"]),
                        ),
                        data_key="quantidade",
                        name="Veículos",
                        max_bar_size=64,
                        is_animation_active=False,
                        radius=[6, 6, 0, 0],
                    ),
                    data=DashboardState.chart_veiculos_por_status,
                    width="100%",
                    height=300,
                ),
                _chart_empty(
                    DashboardState.chart_veiculos_por_status,
                    "Nenhum veículo registrado nesta distribuição de estoque.",
                ),
            ),
            _chart_data(DashboardState.chart_veiculos_por_status),
            align="start",
            width="100%",
        ),
        class_name="dashboard-card",
        width="100%",
    )


def _low_stock_parts() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Peças sem estoque ou com estoque baixo", size="4", as_="h2"),
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
                rx.heading("Filtros de análise", size="4", as_="h2"),
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
                    rx.vstack(
                        rx.text("Tipo de item", class_name="dashboard-filter-label"),
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
                        align="start",
                        spacing="2",
                        class_name="dashboard-filter-field",
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
                        "Selecione os filtros e clique em Atualizar dados para consultar.",
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


def _metrics_widget() -> rx.Component:
    return rx.grid(
        _metric(
            "Vendas no período",
            DashboardState.total_vendas,
            "Total de vendas filtradas",
            "shopping-cart",
            _METRIC_NEUTRAL,
        ),
        _metric(
            "Recebimento líquido",
            DashboardState.valor_liquido,
            "Valor líquido recebido no período",
            "banknote",
            _METRIC_NEUTRAL,
        ),
        _metric(
            "Vendas pagas",
            DashboardState.vendas_pagas,
            "Vendas com pagamento registrado",
            "badge-check",
            _METRIC_NEUTRAL,
        ),
        _metric(
            "Valor médio por venda",
            DashboardState.ticket_medio,
            "Valor bruto dividido pelo total de vendas",
            "receipt",
            _METRIC_NEUTRAL,
        ),
        _metric(
            "Valor bruto vendido",
            DashboardState.valor_bruto,
            "Total bruto no período",
            "chart-no-axes-column-increasing",
            _METRIC_NEUTRAL,
        ),
        _metric(
            "Cancelamentos",
            DashboardState.percentual_canceladas,
            DashboardState.vendas_canceladas + " vendas canceladas",
            "circle-alert",
            _METRIC_WARNING,
        ),
        columns=rx.breakpoints(
            initial="1fr",
            sm="repeat(2, minmax(0, 1fr))",
            lg="repeat(3, minmax(0, 1fr))",
        ),
        spacing="4",
        width="100%",
        class_name="dashboard-kpi-grid",
    )


def _sales_charts_widget() -> rx.Component:
    return rx.vstack(
        _trend_chart(),
        rx.grid(
            _payment_chart(),
            _mix_chart(),
            columns=rx.breakpoints(initial="1fr", lg="repeat(2, minmax(0, 1fr))"),
            spacing="4",
            width="100%",
            class_name="dashboard-analytics-grid",
        ),
        align="start",
        width="100%",
        class_name="dashboard-sales-charts",
    )


def _inventory_widget() -> rx.Component:
    return rx.cond(
        AuthState.is_manager,
        rx.vstack(
            rx.heading("Estoque atual", size="5", as_="h2"),
            rx.text(
                "Disponibilidade de veículos e peças, separada das vendas do período.",
                class_name="muted",
            ),
            rx.grid(
                _metric(
                    "Veículos disponíveis",
                    DashboardState.veiculos_disponiveis,
                    DashboardState.valor_veiculos + " em valor de estoque",
                    "car-front",
                    _METRIC_NEUTRAL,
                ),
                _metric(
                    "Peças disponíveis",
                    DashboardState.pecas_disponiveis,
                    DashboardState.valor_estoque_pecas + " em valor de estoque",
                    "boxes",
                    _METRIC_NEUTRAL,
                ),
                _metric(
                    "Peças sem estoque",
                    DashboardState.pecas_sem_estoque,
                    "Itens com quantidade disponível igual a zero",
                    "package-x",
                    _METRIC_WARNING,
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
                columns=rx.breakpoints(initial="1fr", lg="repeat(2, minmax(0, 1fr))"),
                spacing="4",
                width="100%",
            ),
            align="start",
            width="100%",
            class_name="dashboard-stock-section",
        ),
        rx.fragment(),
    )


def _sales_breakdown_widget() -> rx.Component:
    return rx.vstack(
        rx.heading("Detalhamento de vendas", size="5", as_="h2"),
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
    )


def _dashboard_widget(widget_id: rx.Var) -> rx.Component:
    return rx.match(
        widget_id,
        ("metrics", _metrics_widget()),
        ("sales_charts", _sales_charts_widget()),
        ("inventory", _inventory_widget()),
        ("sales_breakdown", _sales_breakdown_widget()),
        rx.fragment(),
    )


def gerenciamento() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(SettingsState.active_dashboard_title, size="6"),
                    rx.text(
                        "Acompanhe as vendas e os indicadores do negócio.",
                        class_name="muted",
                    ),
                    align="start",
                    spacing="1",
                    class_name="dashboard-heading",
                ),
                rx.spacer(),
                rx.hstack(
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
                        rx.cond(
                            DashboardState.loading, "Carregando…", rx.cond(DashboardState.needs_refresh, "Aplicar filtros", "Atualizar dados")
                        ),
                        on_click=DashboardState.load(True),
                        disabled=DashboardState.loading,
                        class_name="dashboard-refresh-button",
                    ),
                    rx.button(
                        rx.cond(DashboardState.report_status != "", "Exportando…", "Exportar Excel"),
                        on_click=DashboardState.export_excel,
                        disabled=~DashboardState.can_export,
                        variant="outline",
                        class_name="dashboard-export-button",
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
            rx.box(
                rx.cond(DashboardState.report_status != "",
                        rx.text(DashboardState.report_status, class_name="dashboard-export-status", size="2"),
                        rx.cond(DashboardState.report_started,
                                rx.text("Download iniciado", class_name="interaction-feedback", size="2"))),
                role="status",
                aria_atomic=True,
                width="100%",
                display=rx.cond((DashboardState.report_status != "") | DashboardState.report_started, "block", "contents"),
            ),
            rx.box(
                rx.cond(DashboardState.filters_applied,
                        rx.text("Indicadores atualizados", class_name="interaction-feedback", size="2")),
                role="status", aria_atomic=True,
                display=rx.cond(DashboardState.filters_applied, "block", "contents"),
            ),
            rx.cond(
                DashboardState.report_error != "",
                rx.callout(
                    DashboardState.report_error,
                    icon="circle-alert",
                    color_scheme="red",
                    class_name="dashboard-export-error",
                    role="alert",
                    width="100%",
                ),
            ),
            _filters(),
            feedback(DashboardState.error, DashboardState.loading),
            rx.cond(
                DashboardState.loading,
                rx.vstack(
                    rx.box(height="148px", width="100%", class_name="dashboard-loading-placeholder", aria_hidden=True),
                    rx.box(height="320px", width="100%", class_name="dashboard-loading-placeholder", aria_hidden=True),
                    width="100%",
                    spacing="4",
                    aria_label="Carregando indicadores",
                ),
                rx.fragment(),
            ),
            rx.cond(
                DashboardState.loading,
                rx.fragment(),
                rx.cond(
                    SettingsState.active_widget_order.length() > 0,
                    rx.box(
                        rx.foreach(
                            SettingsState.active_widget_order,
                            lambda widget_id: _dashboard_widget(widget_id),
                        ),
                        display="flex",
                        flex_direction="column",
                        gap="22px",
                        width="100%",
                        class_name="dashboard-results",
                    ),
                    rx.callout(
                        "Todos os widgets estão ocultos. Ajuste sua personalização para exibir dados.",
                        icon="layout-dashboard",
                        color_scheme="gray",
                        role="status",
                    ),
                ),
            ),

            class_name="page-stack dashboard-page",
            width="100%",
        ),
        "Dashboard",
        allowed=AuthState.authenticated,
    )
