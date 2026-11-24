import reflex as rx

from app.components.app_shell import shell
from app.components.states import empty_state, feedback
from app.state.auth_state import AuthState
from app.state.resource_state import ClientsState, PartsState, UsersState, VehiclesState


def _vehicle_card(row: rx.Var, endpoint: str) -> rx.Component:
    return rx.card(
        rx.box(
            rx.cond(
                row["_image_url"] != "",
                rx.el.img(
                    src=row["_image_url"],
                    alt=row["_vehicle_name"],
                    loading="lazy",
                    decoding="async",
                    class_name="vehicle-card-image",
                ),
                rx.box(
                    rx.icon("car-front", size=38, stroke_width=1.25),
                    rx.text("Imagem não cadastrada"),
                    class_name="vehicle-card-image vehicle-card-image-empty",
                ),
            ),
            class_name="vehicle-card-media",
        ),
        rx.vstack(
            rx.cond(
                row["_vehicle_status"] != "",
                _vehicle_status_badge(
                    row["_vehicle_status"],
                    row["_vehicle_status_class"],
                ),
                rx.fragment(),
            ),
            rx.heading(row["_vehicle_name"], size="4", class_name="vehicle-card-title"),
            rx.grid(
                _vehicle_info("Ano", row["_vehicle_year"]),
                _vehicle_info("Valor", row["_vehicle_price"]),
                _vehicle_info("Km", row["_vehicle_mileage"]),
                class_name="vehicle-card-info",
            ),
            rx.link(
                rx.hstack(
                    rx.text("Ver Detalhes"),
                    rx.icon("arrow-right", size=16, stroke_width=1.7),
                    justify="center",
                    align="center",
                    width="100%",
                ),
                href=rx.Var.create(f"{endpoint.rstrip('/')}/") + row["id"].to_string(),
                class_name="vehicle-details-link",
            ),
            align="start",
            width="100%",
            class_name="vehicle-card-content",
        ),
        class_name="vehicle-card",
    )


def _vehicle_status_badge(label: rx.Var, status_class: rx.Var) -> rx.Component:
    return rx.cond(
        status_class == "status-available",
        rx.badge(label, class_name="vehicle-status status-available"),
        rx.cond(
            status_class == "status-reserved",
            rx.badge(label, class_name="vehicle-status status-reserved"),
            rx.cond(
                status_class == "status-sold",
                rx.badge(label, class_name="vehicle-status status-sold"),
                rx.badge(label, class_name="vehicle-status status-neutral"),
            ),
        ),
    )


def _vehicle_info(label: str, value: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="vehicle-info-label"),
        rx.text(value, class_name="vehicle-info-value"),
        align="start",
        class_name="vehicle-info-item",
    )


def _part_card(row: rx.Var, endpoint: str) -> rx.Component:
    return rx.card(
        rx.box(
            rx.cond(
                row["_part_image_url"] != "",
                rx.el.img(
                    src=row["_part_image_url"],
                    alt=row["_part_name"],
                    loading="lazy",
                    decoding="async",
                    class_name="part-card-image",
                ),
                rx.box(
                    rx.icon("package", size=38, stroke_width=1.25),
                    rx.text("Imagem não cadastrada"),
                    class_name="part-card-image part-card-image-empty",
                ),
            ),
            class_name="part-card-media",
        ),
        rx.vstack(
            rx.badge(
                rx.cond(
                    row["_part_stock_class"] == "stock-out",
                    "Sem estoque",
                    rx.cond(
                        row["_part_stock_class"] == "stock-low",
                        "Estoque baixo",
                        "Disponível",
                    ),
                ),
                class_name=rx.cond(
                    row["_part_stock_class"] == "stock-out",
                    "part-stock-badge stock-out",
                    rx.cond(
                        row["_part_stock_class"] == "stock-low",
                        "part-stock-badge stock-low",
                        "part-stock-badge stock-available",
                    ),
                ),
            ),
            rx.heading(row["_part_name"], size="4", class_name="vehicle-card-title"),
            rx.text(row["_part_area"], class_name="part-card-area"),
            rx.text(row["_part_price"], class_name="part-card-price"),
            rx.hstack(
                rx.text(row["_part_quantity"]),
                rx.text(" unidades disponíveis"),
                class_name="part-card-quantity",
            ),
                rx.button(
                    rx.hstack(
                        rx.icon("square-pen", size=16, stroke_width=1.8),
                        rx.text("Editar"),
                        align="center",
                        spacing="2",
                    ),
                    on_click=PartsState.open_part_edit(row["id"].to_string()),
                    width="100%",
                    class_name="part-edit-button",
                ),
                align="start",
                width="100%",
                class_name="part-card-content",
        ),
        class_name="part-card",
    )


def _part_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
                rx.hstack(
                    rx.center(
                        rx.icon("square-pen", size=19),
                        class_name="client-dialog-icon part-dialog-icon",
                    ),
                    rx.vstack(
                        rx.dialog.title(
                            "Editar peça",
                            class_name="client-dialog-title",
                        ),
                        rx.dialog.description(
                            "Atualize os dados cadastrados da peça.",
                            class_name="client-dialog-description",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=18),
                            variant="ghost",
                            aria_label="Fechar",
                            class_name="client-dialog-close",
                        )
                    ),
                    align="center",
                    width="100%",
                    class_name="client-dialog-header",
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text("Nome", class_name="client-dialog-label"),
                        rx.input(
                            value=PartsState.part_form_name,
                            on_change=PartsState.set_part_form_name,
                            disabled=PartsState.part_dialog_loading,
                            aria_label="Nome da peça",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Preço", class_name="client-dialog-label"),
                        rx.input(
                            type="number",
                            min="0",
                            step="0.01",
                            value=PartsState.part_form_price,
                            on_change=PartsState.set_part_form_price,
                            disabled=PartsState.part_dialog_loading,
                            aria_label="Preço da peça",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Área", class_name="client-dialog-label"),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecione uma área"),
                            rx.select.content(
                                rx.foreach(
                                    PartsState.part_edit_areas,
                                    lambda area: rx.select.item(
                                        area["Secao"],
                                        value=area["id"],
                                    ),
                                )
                            ),
                            value=PartsState.part_form_area_id,
                            on_change=PartsState.set_part_form_area_id,
                            disabled=PartsState.part_dialog_loading,
                            class_name="part-dialog-area-select",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.cond(
                        PartsState.part_dialog_error != "",
                        rx.callout(
                            PartsState.part_dialog_error,
                            color_scheme="red",
                            role="alert",
                        ),
                        rx.fragment(),
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancelar", variant="outline")
                        ),
                        rx.button(
                            rx.icon("save", size=16),
                            rx.text("Salvar alterações"),
                            on_click=PartsState.save_part_edits,
                            disabled=PartsState.part_dialog_saving
                            | PartsState.part_dialog_loading,
                            class_name="client-dialog-save",
                        ),
                        justify="end",
                        width="100%",
                        class_name="client-dialog-actions",
                    ),
                    width="100%",
                    align="stretch",
                    spacing="4",
                    class_name="client-dialog-body",
                ),
                class_name="client-dialog-content",
        ),
        open=PartsState.part_dialog_open,
        on_open_change=PartsState.close_part_dialog,
    )


def _client_row(row: rx.Var) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.center(
                    row["_client_initials"],
                    class_name="client-avatar",
                ),
                rx.vstack(
                    rx.text(row["_client_name"], class_name="client-name"),
                    rx.text(row["_client_phone"], class_name="client-row-secondary"),
                    align="start",
                    spacing="0",
                ),
                align="center",
                spacing="3",
                class_name="client-identity",
            )
        ),
        rx.table.cell(row["_client_cpf"]),
        rx.table.cell(row["_client_email"]),
        rx.table.cell(row["_client_last_activity"]),
        rx.table.cell(
            rx.dropdown_menu.root(
                rx.dropdown_menu.trigger(
                    rx.button(
                        rx.icon("eye", size=17, stroke_width=1.7),
                        variant="outline",
                        aria_label="Opções do cliente",
                        class_name="client-action-button",
                    )
                ),
                rx.dropdown_menu.content(
                    rx.text(
                        "Opções do cliente",
                        class_name="client-action-menu-heading",
                    ),
                    rx.dropdown_menu.item(
                        rx.hstack(
                            rx.icon("eye", size=16),
                            rx.text("Visualizar detalhes"),
                            align="center",
                            spacing="2",
                        ),
                        on_select=rx.redirect(
                            rx.Var.create("/clientes/") + row["id"].to_string()
                        ),
                    ),
                    rx.dropdown_menu.item(
                        rx.hstack(
                            rx.icon("square-pen", size=16),
                            rx.text("Editar cliente"),
                            align="center",
                            spacing="2",
                        ),
                        on_select=ClientsState.open_client_edit(
                            row["id"].to_string()
                        ),
                    ),
                    rx.dropdown_menu.item(
                        rx.hstack(
                            rx.icon("trash-2", size=16),
                            rx.text("Excluir perfil"),
                            align="center",
                            spacing="2",
                        ),
                        on_select=ClientsState.open_client_delete(
                            row["id"].to_string()
                        ),
                        class_name="client-delete-option",
                    ),
                    class_name="client-action-menu",
                ),
            )
        ),
    )


def _client_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.hstack(
                rx.center(
                    rx.icon(
                        rx.cond(
                            ClientsState.client_dialog_mode == "edit",
                            "square-pen",
                            "user-round",
                        ),
                        size=19,
                    ),
                    class_name="client-dialog-icon",
                ),
                rx.vstack(
                    rx.dialog.title(
                        rx.cond(
                            ClientsState.client_dialog_mode == "edit",
                            "Editar cliente",
                            ClientsState.selected_client.get("name", "Cliente"),
                        ),
                        class_name="client-dialog-title",
                    ),
                    rx.dialog.description(
                        rx.cond(
                            ClientsState.client_dialog_mode == "edit",
                            "Atualize os dados e contatos cadastrados.",
                            "Dados do cadastro e atividade comercial.",
                        ),
                        class_name="client-dialog-description",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.dialog.close(
                    rx.button(
                        rx.icon("x", size=18),
                        variant="ghost",
                        aria_label="Fechar",
                        class_name="client-dialog-close",
                    )
                ),
                align="center",
                width="100%",
                class_name="client-dialog-header",
            ),
            rx.cond(
                ClientsState.client_dialog_mode == "edit",
                rx.vstack(
                    rx.vstack(
                        rx.text("Nome completo", class_name="client-dialog-label"),
                        rx.input(
                            value=ClientsState.client_form_name,
                            on_change=ClientsState.set_client_form_name,
                            aria_label="Nome completo",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("CPF", class_name="client-dialog-label"),
                            rx.input(
                                value=ClientsState.client_form_cpf,
                                on_change=ClientsState.set_client_form_cpf,
                                aria_label="CPF",
                            ),
                            align="stretch",
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text(
                                "Telefone / WhatsApp",
                                class_name="client-dialog-label",
                            ),
                            rx.input(
                                value=ClientsState.client_form_phone,
                                on_change=ClientsState.set_client_form_phone,
                                aria_label="Telefone / WhatsApp",
                            ),
                            align="stretch",
                            spacing="1",
                        ),
                        columns="repeat(2, minmax(0, 1fr))",
                        class_name="client-dialog-fields",
                    ),
                    rx.vstack(
                        rx.text("E-mail", class_name="client-dialog-label"),
                        rx.input(
                            type="email",
                            value=ClientsState.client_form_email,
                            on_change=ClientsState.set_client_form_email,
                            aria_label="E-mail",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.cond(
                        ClientsState.client_action_message != "",
                        rx.callout(
                            ClientsState.client_action_message,
                            color_scheme="red",
                            role="alert",
                        ),
                        rx.fragment(),
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancelar", variant="outline")
                        ),
                        rx.button(
                            rx.icon("save", size=16),
                            rx.text("Salvar alterações"),
                            on_click=ClientsState.save_client_edits,
                            class_name="client-dialog-save",
                        ),
                        justify="end",
                        width="100%",
                        class_name="client-dialog-actions",
                    ),
                    width="100%",
                    align="stretch",
                    spacing="4",
                    class_name="client-dialog-body",
                ),
                rx.cond(
                    ClientsState.client_dialog_mode == "delete",
                    rx.vstack(
                        rx.text(
                            "Excluir perfil",
                            class_name="client-dialog-label",
                        ),
                        rx.text(
                            "O cliente e seu cadastro serão removidos. O histórico de vendas será preservado sem vínculo com este cliente.",
                            class_name="client-dialog-description",
                        ),
                        rx.text(
                            ClientsState.selected_client.get("name", ""),
                            class_name="client-dialog-value",
                        ),
                        rx.cond(
                            ClientsState.client_action_message != "",
                            rx.callout(
                                ClientsState.client_action_message,
                                color_scheme="red",
                                role="alert",
                            ),
                            rx.fragment(),
                        ),
                        rx.hstack(
                            rx.dialog.close(
                                rx.button("Cancelar", variant="outline")
                            ),
                            rx.button(
                                rx.icon("trash-2", size=16),
                                rx.text("Confirmar exclusão"),
                                on_click=ClientsState.delete_client,
                                loading=ClientsState.client_delete_loading,
                                color_scheme="red",
                            ),
                            justify="end",
                            width="100%",
                        ),
                        width="100%",
                        align="stretch",
                        spacing="4",
                        class_name="client-dialog-body",
                    ),
                    rx.vstack(
                        rx.cond(
                        ClientsState.client_detail_loading,
                        rx.text(
                            "Carregando dados atualizados...",
                            class_name="client-dialog-description",
                        ),
                        rx.fragment(),
                    ),
                    rx.vstack(
                        rx.text("CPF", class_name="client-dialog-label"),
                        rx.text(
                            ClientsState.selected_client.get("cpf", ""),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.vstack(
                        rx.text("E-mail", class_name="client-dialog-label"),
                        rx.text(
                            ClientsState.selected_client.get("email", ""),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.vstack(
                        rx.text("Telefone", class_name="client-dialog-label"),
                        rx.text(
                            ClientsState.selected_client.get("phone", ""),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.vstack(
                        rx.text(
                            "Última atividade",
                            class_name="client-dialog-label",
                        ),
                        rx.text(
                            ClientsState.selected_client.get(
                                "last_activity", ""
                            ),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.cond(
                        ClientsState.client_action_message != "",
                        rx.callout(
                            ClientsState.client_action_message,
                            color_scheme="red",
                            role="alert",
                        ),
                        rx.fragment(),
                    ),
                    width="100%",
                    align="stretch",
                    spacing="3",
                        class_name="client-dialog-body",
                    ),
                ),
            ),
            class_name="client-dialog-content",
        ),
        open=ClientsState.client_dialog_open,
        on_open_change=ClientsState.close_client_dialog,
    )


def _collection_status(state, endpoint: str, title: str) -> rx.Component:
    return rx.hstack(
        rx.cond(
            state.loaded_pages > 0,
            rx.text("Páginas carregadas: ", state.loaded_pages, " / ", state.total_pages,
                    rx.cond(state.complete, " · Lista completa", " · Lista parcial"), role="status"),
            rx.text("Aguardando dados da lista…", role="status"),
        ),
        rx.spacer(),
        rx.button("Atualizar lista", on_click=state.load(endpoint, title), variant="outline",
                  disabled=state.loading, class_name="collection-refresh"),
        align="center", wrap="wrap", class_name="collection-status", width="100%",
    )


def _clients_view(new_href: str | None) -> rx.Component:
    return rx.vstack(
        rx.grid(
            rx.card(
                rx.hstack(
                    rx.center(
                        rx.icon("users-round", size=19),
                        class_name="client-metric-icon client-metric-blue",
                    ),
                    rx.vstack(
                        rx.text("Total de clientes", class_name="client-metric-label"),
                        rx.text(
                            rx.cond(ClientsState.complete, ClientsState.records.length().to_string(), "Carregando…"),
                            class_name="client-metric-value client-value-blue",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    align="center",
                    spacing="3",
                ),
                class_name="client-metric-card",
            ),
            rx.card(
                rx.hstack(
                    rx.center(
                        rx.icon("user-round-plus", size=19),
                        class_name="client-metric-icon client-metric-purple",
                    ),
                    rx.vstack(
                        rx.text("Novos neste mês", class_name="client-metric-label"),
                        rx.text(
                            rx.cond(ClientsState.complete, ClientsState.clients_new_this_month.to_string(), "Carregando…"),
                            class_name="client-metric-value client-value-purple",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    align="center",
                    spacing="3",
                ),
                class_name="client-metric-card",
            ),
            rx.card(
                rx.hstack(
                    rx.center(
                        rx.icon("clock-3", size=19),
                        class_name="client-metric-icon client-metric-amber",
                    ),
                    rx.vstack(
                        rx.text("Compras pendentes", class_name="client-metric-label"),
                        rx.text(
                            rx.cond(
                                ClientsState.client_sales_available,
                                ClientsState.pending_purchases.to_string(),
                                rx.cond(ClientsState.activity_pending, "Carregando…", "Indisponível"),
                            ),
                            class_name="client-metric-value client-value-amber",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    align="center",
                    spacing="3",
                ),
                class_name="client-metric-card",
            ),
            class_name="client-metrics-grid",
        ),
        rx.hstack(
            rx.hstack(
                rx.icon("search", size=18, stroke_width=1.8),
                rx.input(
                    placeholder="Buscar por nome, CPF, telefone ou e-mail...",
                    aria_label="Buscar clientes por nome, CPF, telefone ou e-mail",
                    id="client-search-focus",
                    value=ClientsState.query,
                    on_change=ClientsState.set_query,
                    class_name="client-search-input",
                ),
                class_name="client-search",
            ),
            rx.select.root(
                rx.select.trigger(placeholder="Ordenar por"),
                rx.select.content(
                    rx.select.item(
                        "Mais antigo para o mais novo",
                        value="oldest_first",
                    ),
                    rx.select.item(
                        "Mais novo para o mais antigo",
                        value="newest_first",
                    ),
                ),
                value=ClientsState.client_sort_order,
                on_change=ClientsState.set_client_sort_order,
                class_name="client-sort-select",
            ),
            rx.spacer(),
            rx.cond(
                new_href is not None,
                rx.link(
                    rx.button(
                            rx.hstack(
                                rx.icon("plus", size=17, stroke_width=2),
                                rx.text("Novo Cliente"),
                                align="center",
                                spacing="2",
                            ),
                            class_name="client-new-button",
                        ),
                    href=new_href or "#",
                ),
                rx.fragment(),
            ),
            class_name="client-toolbar",
            align="center",
        ),
        feedback(ClientsState.error, ClientsState.loading),
        _collection_status(ClientsState, "/clientes", "Clientes"),
        rx.cond(
            ClientsState.client_sales_warning != "",
            rx.callout(
                ClientsState.client_sales_warning,
                color_scheme="amber",
                role="status",
            ),
            rx.fragment(),
        ),
        rx.cond(
            (ClientsState.client_action_message != "") & ~ClientsState.client_dialog_open,
            rx.callout(
                ClientsState.client_action_message,
                role=rx.cond(ClientsState.client_action_success, "status", "alert"),
                icon=rx.cond(ClientsState.client_action_success, "check", "circle-alert"),
                color_scheme=rx.cond(ClientsState.client_action_success, "green", "red"),
                class_name=rx.cond(ClientsState.client_action_success, "interaction-result", "client-action-feedback"),
            ),
            rx.fragment(),
        ),
        rx.cond(
            ClientsState.paginated_clients.length() > 0,
            rx.vstack(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Cliente"),
                            rx.table.column_header_cell("CPF"),
                            rx.table.column_header_cell("E-mail"),
                            rx.table.column_header_cell("Última atividade"),
                            rx.table.column_header_cell("Ações"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(ClientsState.paginated_clients, _client_row)
                    ),
                    class_name="client-table",
                ),
                rx.hstack(
                    rx.text(
                        "Última atividade baseada na compra mais recente registrada.",
                        class_name="client-pagination-note",
                    ),
                    rx.spacer(),
                    rx.button(
                        "Anterior",
                        on_click=ClientsState.previous_client_page,
                        variant="outline",
                        disabled=ClientsState.client_page <= 1,
                    ),
                    rx.text(
                        ClientsState.client_page.to_string()
                        + " / "
                        + ClientsState.client_total_pages.to_string(),
                        class_name="client-page-indicator",
                    ),
                    rx.button(
                        "Próxima",
                        on_click=ClientsState.next_client_page,
                        variant="outline",
                        disabled=ClientsState.client_page
                        >= ClientsState.client_total_pages,
                    ),
                    class_name="client-pagination",
                ),
                class_name="client-table-panel",
            ),
            empty_state(
                rx.cond(
                    ClientsState.query == "",
                    rx.cond(ClientsState.complete, "A API não retornou clientes.", "Aguardando clientes. A lista ainda está incompleta."),
                    rx.cond(ClientsState.complete, "Nenhum cliente corresponde à busca.", "Nenhum resultado entre os clientes carregados até agora."),
                )
            ),
        ),
        _client_dialog(),

        class_name="page-stack client-page",
    )


def resource_page(
    title: str, endpoint: str, new_href: str | None = None, allowed: rx.Var = True
) -> rx.Component:
    state = {"/clientes": ClientsState, "/veiculos": VehiclesState, "/pecas": PartsState, "/usuarios": UsersState}[endpoint]
    can_create = AuthState.is_manager if endpoint == "/veiculos" else True
    return shell(
        (_clients_view(new_href) if endpoint == "/clientes" else rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("search", size=18, stroke_width=1.8),
                    rx.input(
                        placeholder=(
                            "Buscar por modelo, marca, placa..."
                            if endpoint == "/veiculos"
                            else "Buscar…"
                        ),
                        aria_label="Buscar veículos por modelo, marca ou placa"
                        if endpoint == "/veiculos"
                        else "Buscar registros",
                        value=state.query,
                        id="stock-search-focus",
                        on_change=state.set_query,
                        class_name="vehicle-search-input"
                        if endpoint == "/veiculos"
                        else "resource-search-input",
                    ),
                    class_name="vehicle-search"
                    if endpoint == "/veiculos"
                    else "resource-search",
                ),
                rx.spacer(),
                rx.cond(
                    new_href is not None and can_create,
                    rx.link(
                        rx.button(
                            rx.hstack(
                                rx.icon("plus", size=17, stroke_width=2),
                                rx.text("Novo"),
                                align="center",
                                spacing="2",
                            ),
                            class_name="vehicle-new-button"
                            if endpoint == "/veiculos"
                            else "",
                        ),
                        href=new_href or "#",
                    ),
                    rx.fragment(),
                ),
                class_name="toolbar vehicle-toolbar"
                if endpoint == "/veiculos"
                else "toolbar",
            ),
            feedback(state.error, state.loading),
            rx.cond(
                PartsState.part_action_notice != "",
                rx.callout(PartsState.part_action_notice, icon="check", color_scheme="green",
                           role="status", class_name="interaction-result"),
            ) if endpoint == "/pecas" else rx.fragment(),
            _collection_status(state, endpoint, title),
            rx.box(id="stock-card-list"),
            rx.cond(
                endpoint == "/veiculos",
                rx.cond(
                    state.filtered_records.length() > 0,
                    rx.grid(
                        rx.foreach(
                            state.visible_cards,
                            lambda row: _vehicle_card(row, endpoint),
                        ),
                        class_name="vehicle-grid",
                        width="100%",
                    ),
                    empty_state(
                        rx.cond(
                            state.query == "",
                            rx.cond(state.complete, "A API não retornou veículos para esta consulta.", "Aguardando veículos. Lista incompleta."),
                            rx.cond(state.complete, "Nenhum veículo corresponde à busca.", "Sem correspondências nos veículos carregados até agora."),
                        )
                    ),
                ),
                rx.cond(
                    endpoint == "/pecas",
                    rx.cond(
                        state.filtered_records.length() > 0,
                        rx.grid(
                            rx.foreach(
                                state.visible_cards,
                                lambda row: _part_card(row, endpoint),
                            ),
                            class_name="part-grid",
                            width="100%",
                        ),
                        empty_state(
                            rx.cond(
                                state.query == "",
                                rx.cond(state.complete, "A API não retornou peças para esta consulta.", "Aguardando peças. Lista incompleta."),
                                rx.cond(state.complete, "Nenhuma peça corresponde à busca.", "Sem correspondências nas peças carregadas até agora."),
                            )
                        ),
                    ),
                    rx.cond(
                        state.filtered_records.length() > 0,
                        rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    rx.cond(
                                        endpoint == "/clientes",
                                        "Cliente - CPF",
                                        "Registro",
                                    )
                                ),
                                rx.table.column_header_cell("Ações"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                state.filtered_records,
                                lambda row: rx.table.row(
                                    rx.table.cell(
                                        rx.cond(
                                            endpoint == "/clientes",
                                            row["_display_label"],
                                            row.to_string(),
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.link(
                                            "Abrir",
                                            href=rx.Var.create(f"{endpoint.rstrip('/')}/")
                                            + row["id"].to_string(),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                        empty_state("A API não retornou registros para esta consulta."),
                    ),
                ),
            ),
                rx.cond(
                    (endpoint in ("/veiculos", "/pecas")) & (state.card_total_pages > 1),
                    rx.hstack(
                        rx.button("Anterior", variant="outline", disabled=state.card_page <= 1,
                                  on_click=state.move_card_page(-1)),
                        rx.text("Página ", state.card_page, " de ", state.card_total_pages,
                                rx.cond(state.complete, "", " carregadas"), role="status"),
                        rx.button("Próxima", variant="outline", disabled=state.card_page >= state.card_total_pages,
                                  on_click=state.move_card_page(1)),
                        align="center", justify="center", wrap="wrap", width="100%",
                    ),
                ),
                rx.cond(
                    endpoint == "/pecas",
                    _part_dialog(),
                    rx.fragment(),
                ),

                class_name="page-stack vehicle-page"
                if endpoint == "/veiculos"
                else "page-stack",
            )),
        title,
        allowed,
    )
