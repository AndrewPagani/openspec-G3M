import reflex as rx

from app.components.app_shell import shell
from app.components.states import empty_state, feedback
from app.state.auth_state import AuthState
from app.state.resource_state import ResourceState


def _vehicle_card(row: rx.Var, endpoint: str) -> rx.Component:
    return rx.card(
        rx.box(
            rx.cond(
                row["_image_url"] != "",
                rx.image(
                    src=row["_image_url"],
                    alt=row["_vehicle_name"],
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
                _vehicle_info("Comb.", row["_vehicle_fuel"]),
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
                rx.image(
                    src=row["_part_image_url"],
                    alt=row["_part_name"],
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
                class_name="part-stock-badge",
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
                    on_click=ResourceState.open_part_edit(row["id"].to_string()),
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
                            value=ResourceState.part_form_name,
                            on_change=ResourceState.set_part_form_name,
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
                            value=ResourceState.part_form_price,
                            on_change=ResourceState.set_part_form_price,
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
                                    ResourceState.part_edit_areas,
                                    lambda area: rx.select.item(
                                        area["Secao"],
                                        value=area["id"],
                                    ),
                                )
                            ),
                            value=ResourceState.part_form_area_id,
                            on_change=ResourceState.set_part_form_area_id,
                            class_name="part-dialog-area-select",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.cond(
                        ResourceState.part_dialog_error != "",
                        rx.callout(
                            ResourceState.part_dialog_error,
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
                            on_click=ResourceState.save_part_edits,
                            disabled=ResourceState.part_dialog_saving
                            | ResourceState.part_dialog_loading,
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
        open=ResourceState.part_dialog_open,
        on_open_change=ResourceState.close_part_dialog,
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
                        on_select=ResourceState.open_client_edit(
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
                        on_select=ResourceState.open_client_delete(
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
                            ResourceState.client_dialog_mode == "edit",
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
                            ResourceState.client_dialog_mode == "edit",
                            "Editar cliente",
                            ResourceState.selected_client.get("name", "Cliente"),
                        ),
                        class_name="client-dialog-title",
                    ),
                    rx.dialog.description(
                        rx.cond(
                            ResourceState.client_dialog_mode == "edit",
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
                ResourceState.client_dialog_mode == "edit",
                rx.vstack(
                    rx.vstack(
                        rx.text("Nome completo", class_name="client-dialog-label"),
                        rx.input(
                            value=ResourceState.client_form_name,
                            on_change=ResourceState.set_client_form_name,
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
                                value=ResourceState.client_form_cpf,
                                on_change=ResourceState.set_client_form_cpf,
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
                                value=ResourceState.client_form_phone,
                                on_change=ResourceState.set_client_form_phone,
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
                            value=ResourceState.client_form_email,
                            on_change=ResourceState.set_client_form_email,
                            aria_label="E-mail",
                        ),
                        align="stretch",
                        width="100%",
                        spacing="1",
                    ),
                    rx.cond(
                        ResourceState.client_action_message != "",
                        rx.callout(
                            ResourceState.client_action_message,
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
                            on_click=ResourceState.save_client_edits,
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
                    ResourceState.client_dialog_mode == "delete",
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
                            ResourceState.selected_client.get("name", ""),
                            class_name="client-dialog-value",
                        ),
                        rx.cond(
                            ResourceState.client_action_message != "",
                            rx.callout(
                                ResourceState.client_action_message,
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
                                on_click=ResourceState.delete_client,
                                loading=ResourceState.client_delete_loading,
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
                        ResourceState.client_detail_loading,
                        rx.text(
                            "Carregando dados atualizados...",
                            class_name="client-dialog-description",
                        ),
                        rx.fragment(),
                    ),
                    rx.vstack(
                        rx.text("CPF", class_name="client-dialog-label"),
                        rx.text(
                            ResourceState.selected_client.get("cpf", ""),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.vstack(
                        rx.text("E-mail", class_name="client-dialog-label"),
                        rx.text(
                            ResourceState.selected_client.get("email", ""),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.vstack(
                        rx.text("Telefone", class_name="client-dialog-label"),
                        rx.text(
                            ResourceState.selected_client.get("phone", ""),
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
                            ResourceState.selected_client.get(
                                "last_activity", ""
                            ),
                            class_name="client-dialog-value",
                        ),
                        align="start",
                        spacing="1",
                        class_name="client-dialog-detail",
                    ),
                    rx.cond(
                        ResourceState.client_action_message != "",
                        rx.callout(
                            ResourceState.client_action_message,
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
        open=ResourceState.client_dialog_open,
        on_open_change=ResourceState.close_client_dialog,
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
                            ResourceState.records.length(),
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
                            ResourceState.clients_new_this_month,
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
                            ResourceState.pending_purchases,
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
                    value=ResourceState.query,
                    on_change=ResourceState.set_query,
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
                value=ResourceState.client_sort_order,
                on_change=ResourceState.set_client_sort_order,
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
        feedback(ResourceState.error, ResourceState.loading),
        rx.cond(
            ResourceState.client_action_message != "",
            rx.callout(
                ResourceState.client_action_message,
                role="status",
                class_name="client-action-feedback",
            ),
            rx.fragment(),
        ),
        rx.cond(
            ResourceState.paginated_clients.length() > 0,
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
                        rx.foreach(ResourceState.paginated_clients, _client_row)
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
                        on_click=ResourceState.previous_client_page,
                        variant="outline",
                        disabled=ResourceState.client_page <= 1,
                    ),
                    rx.text(
                        ResourceState.client_page.to_string()
                        + " / "
                        + ResourceState.client_total_pages.to_string(),
                        class_name="client-page-indicator",
                    ),
                    rx.button(
                        "Próxima",
                        on_click=ResourceState.next_client_page,
                        variant="outline",
                        disabled=ResourceState.client_page
                        >= ResourceState.client_total_pages,
                    ),
                    class_name="client-pagination",
                ),
                class_name="client-table-panel",
            ),
            empty_state(
                rx.cond(
                    ResourceState.query == "",
                    "A API não retornou clientes.",
                    "Nenhum cliente corresponde à busca.",
                )
            ),
        ),
        _client_dialog(),
        on_mount=ResourceState.load("/clientes", "Clientes"),
        class_name="page-stack client-page",
    )


def resource_page(
    title: str, endpoint: str, new_href: str | None = None, allowed: rx.Var = True
) -> rx.Component:
    can_create = AuthState.is_manager if endpoint == "/veiculos" else True
    return shell(
        rx.cond(
            endpoint == "/clientes",
            _clients_view(new_href),
            rx.vstack(
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
                        value=ResourceState.query,
                        on_change=ResourceState.set_query,
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
            feedback(ResourceState.error, ResourceState.loading),
            rx.cond(
                ResourceState.endpoint == "/veiculos",
                rx.cond(
                    ResourceState.filtered_records.length() > 0,
                    rx.grid(
                        rx.foreach(
                            ResourceState.filtered_records,
                            lambda row: _vehicle_card(row, endpoint),
                        ),
                        class_name="vehicle-grid",
                        width="100%",
                    ),
                    empty_state(
                        rx.cond(
                            ResourceState.query == "",
                            "A API não retornou veículos para esta consulta.",
                            "Nenhum veículo corresponde à busca.",
                        )
                    ),
                ),
                rx.cond(
                    ResourceState.endpoint == "/pecas",
                    rx.cond(
                        ResourceState.filtered_records.length() > 0,
                        rx.grid(
                            rx.foreach(
                                ResourceState.filtered_records,
                                lambda row: _part_card(row, endpoint),
                            ),
                            class_name="part-grid",
                            width="100%",
                        ),
                        empty_state(
                            rx.cond(
                                ResourceState.query == "",
                                "A API não retornou peças para esta consulta.",
                                "Nenhuma peça corresponde à busca.",
                            )
                        ),
                    ),
                    rx.cond(
                        ResourceState.filtered_records.length() > 0,
                        rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    rx.cond(
                                        ResourceState.endpoint == "/clientes",
                                        "Cliente - CPF",
                                        "Registro",
                                    )
                                ),
                                rx.table.column_header_cell("Ações"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                ResourceState.filtered_records,
                                lambda row: rx.table.row(
                                    rx.table.cell(
                                        rx.cond(
                                            ResourceState.endpoint == "/clientes",
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
                    endpoint == "/pecas",
                    _part_dialog(),
                    rx.fragment(),
                ),
                on_mount=ResourceState.load(endpoint, title),
                class_name="page-stack vehicle-page"
                if endpoint == "/veiculos"
                else "page-stack",
            ),
        ),
        title,
        allowed,
    )
