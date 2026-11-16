import reflex as rx

from app.components.app_shell import shell
from app.state.auth_state import AuthState
from app.state.vendas_state import VendasState


def _sale_log_row(row: rx.Var) -> rx.Component:
    return rx.table.row(
        rx.table.cell("#" + row["id"]),
        rx.table.cell(row["cliente"]),
        rx.table.cell(row["vendedor"]),
        rx.table.cell(row["forma"]),
        rx.table.cell("R$ " + row["valor_final"]),
        rx.table.cell(row["data"]),
        rx.table.cell(rx.link("Ver pagamento", href="/vendas/" + row["id"])),
    )


def sales_list_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.input(
                    placeholder="Pesquisar cliente, vendedor ou ID",
                    value=VendasState.busca,
                    on_change=VendasState.set_busca,
                    width="280px",
                ),
                rx.input(
                    type="date",
                    aria_label="Data inicial",
                    value=VendasState.filtro_data_inicio,
                    on_change=VendasState.set_filtro_data_inicio,
                ),
                rx.input(
                    type="date",
                    aria_label="Data final",
                    value=VendasState.filtro_data_fim,
                    on_change=VendasState.set_filtro_data_fim,
                ),
                rx.select.root(
                    rx.select.trigger(placeholder="Forma de pagamento"),
                    rx.select.content(
                        rx.foreach(
                            VendasState.payment_methods,
                            lambda method: rx.select.item(method["name"], value=method["id"]),
                        )
                    ),
                    value=VendasState.filtro_forma_pagamento,
                    on_change=VendasState.set_filtro_forma_pagamento,
                    width="210px",
                ),
                rx.button("Filtrar", on_click=VendasState.load_sales),
                rx.link(rx.button("Criar venda"), href="/vendas/nova", on_click=VendasState.start_new_sale),
                wrap="wrap",
                spacing="3",
                width="100%",
            ),
            rx.cond(
                VendasState.vendas.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Venda"),
                            rx.table.column_header_cell("Cliente"),
                            rx.table.column_header_cell("Vendedor"),
                            rx.table.column_header_cell("Pagamento"),
                            rx.table.column_header_cell("Valor final"),
                            rx.table.column_header_cell("Data"),
                            rx.table.column_header_cell("Ações"),
                        )
                    ),
                    rx.table.body(rx.foreach(VendasState.vendas, _sale_log_row)),
                    width="100%",
                ),
                rx.callout("Nenhuma venda encontrada."),
            ),
            rx.cond(VendasState.erro != "", rx.callout(VendasState.erro, color_scheme="red")),
            rx.cond(VendasState.processando, rx.spinner()),
            width="100%",
            align="start",
            on_mount=VendasState.load_sales_page,
        ),
        "Vendas realizadas",
    )


def _vehicle_picker(row: rx.Var) -> rx.Component:
    return rx.card(
        rx.cond(
            row["imagem"] != "",
            rx.image(src=row["imagem"], alt=row["nome"], class_name="sale-picker-image"),
            rx.box(rx.icon("car-front", size=34), class_name="sale-picker-image sale-picker-empty"),
        ),
        rx.heading(row["nome"], size="3"),
        rx.text("R$ " + row["preco"], class_name="sale-price"),
        rx.button("Selecionar veículo", on_click=VendasState.add_vehicle(row["id"]), variant="outline"),
        class_name="sale-picker-card",
    )


def _part_picker(row: rx.Var) -> rx.Component:
    return rx.card(
        rx.cond(
            row["imagem"] != "",
            rx.image(src=row["imagem"], alt=row["nome"], class_name="sale-picker-image"),
            rx.box(rx.icon("package", size=34), class_name="sale-picker-image sale-picker-empty"),
        ),
        rx.heading(row["nome"], size="3"),
        rx.text("R$ " + row["preco"] + " • estoque: " + row["estoque"]),
        rx.hstack(
            rx.input(
                type="number",
                min="1",
                max=row["estoque"],
                value=VendasState.selected_part_quantity,
                on_change=VendasState.set_selected_part_quantity,
                width="78px",
                aria_label="Quantidade de " + row["nome"],
            ),
            rx.button(
                "Adicionar",
                on_click=VendasState.add_part_for_id(row["id"]),
            ),
            align="center",
        ),
        class_name="sale-picker-card",
    )


def _payment_panel() -> rx.Component:
    return rx.vstack(
        rx.heading("Pagamento da venda #" + VendasState.venda_id, size="4"),
        rx.text(VendasState.total_confirmado, class_name="sale-total-amount"),
        rx.text(VendasState.payment_status_label, role="status"),
        rx.cond(VendasState.payment_due_date != "", rx.text("Vencimento: " + VendasState.payment_due_date)),
        rx.cond(
            VendasState.payment_url != "",
            rx.vstack(
                rx.text("O cliente escolhe como pagar na fatura do ASAAS."),
                rx.hstack(
                    rx.link(rx.button("Abrir link de pagamento"), href=VendasState.payment_url,
                            is_external=True, rel="noopener noreferrer"),
                    rx.button("Copiar link", variant="outline",
                              on_click=rx.set_clipboard(VendasState.payment_url)),
                    wrap="wrap", spacing="3",
                ),
                rx.text("O link fica salvo nesta venda. Não enviamos e-mails.", class_name="sale-help"),
                align="start", spacing="3", width="100%",
            ),
            rx.vstack(
                rx.text("A venda está reservada. Você pode gerar ou recuperar o link sem criar outra venda."),
                rx.button("Gerar ou recuperar link", on_click=VendasState.generate_payment_link,
                          loading=VendasState.processando),
                align="start", spacing="3",
            ),
        ),
        align="start", spacing="4", width="100%", class_name="sale-payment-panel",
    )


def _selected_item(item: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(item["nome"], weight="medium"),
            rx.text(item["qtd"] + " × R$ " + item["preco"], class_name="sale-help"),
            align="start", spacing="1",
        ),
        rx.button("Remover", on_click=VendasState.remove_item(item["tipo"], item["id"]),
                  variant="ghost", size="1", disabled=VendasState.processando | (VendasState.venda_id != "")),
        justify="between", align="center", width="100%", class_name="sale-selected-item",
    )


def sales_create_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.text("Escolha o cliente e os itens. Depois, compartilhe o link de pagamento.", class_name="sale-intro"),
            rx.cond(VendasState.erro != "", rx.callout(VendasState.erro, color_scheme="red", role="alert", class_name="sale-error")),
            rx.cond(VendasState.mensagem != "", rx.callout(VendasState.mensagem, role="status")),
            rx.box(
                rx.el.fieldset(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Cliente", size="4"), rx.spacer(),
                            rx.link("Cadastrar cliente", href="/clientes/novo"),
                            width="100%", align="center",
                        ),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecione o cliente", aria_label="Cliente da venda"),
                            rx.select.content(rx.foreach(VendasState.clientes,
                                lambda customer: rx.select.item(customer["nome"], value=customer["id"]))),
                            value=VendasState.cliente_id, on_change=VendasState.set_cliente_id, width="100%",
                        ),
                        rx.heading("Veículos disponíveis", size="4"),
                        rx.cond(VendasState.veiculos_disponiveis.length() > 0,
                            rx.scroll_area(rx.hstack(rx.foreach(VendasState.veiculos_disponiveis, _vehicle_picker), spacing="4"),
                                           type="scroll", scrollbars="horizontal", class_name="sale-picker-carousel"),
                            rx.text("Nenhum veículo disponível. Você ainda pode incluir peças.", class_name="sale-help")),
                        rx.heading("Peças com estoque", size="4"),
                        rx.cond(VendasState.pecas_disponiveis.length() > 0,
                            rx.scroll_area(rx.hstack(rx.foreach(VendasState.pecas_disponiveis, _part_picker), spacing="4"),
                                           type="scroll", scrollbars="horizontal", class_name="sale-picker-carousel"),
                            rx.text("Nenhuma peça com estoque disponível.", class_name="sale-help")),
                        spacing="5", align="stretch", width="100%",
                    ),
                    disabled=VendasState.processando | (VendasState.venda_id != "") | VendasState.creation_uncertain,
                    class_name="sale-selection",
                ),
                rx.vstack(
                    rx.cond(
                        VendasState.venda_id != "",
                        rx.vstack(
                            _payment_panel(),
                            rx.link("Ver detalhes da venda", href="/vendas/" + VendasState.venda_id),
                            rx.button("Iniciar outra venda", on_click=VendasState.start_new_sale, variant="outline",
                                      disabled=VendasState.processando),
                            align="start", spacing="4", width="100%",
                        ),
                        rx.vstack(
                            rx.heading("Resumo da venda", size="4"),
                            rx.cond(VendasState.selected_items.length() > 0,
                                rx.foreach(VendasState.selected_items, _selected_item),
                                rx.text("Selecione um veículo ou adicione peças para montar a venda.", class_name="sale-help")),
                            rx.separator(),
                            rx.text("Total previsto", class_name="sale-help"),
                            rx.text(VendasState.valor_bruto_display, class_name="sale-total-amount"),
                            rx.text("O valor será conferido ao reservar os itens.", class_name="sale-help"),
                            rx.separator(),
                            rx.text("O cliente escolhe como pagar no link do ASAAS."),
                            rx.text("Sem envio de e-mail. O link ficará salvo na venda.", class_name="sale-help"),
                            rx.button("Criar venda e gerar link", on_click=VendasState.create_sale,
                                      loading=VendasState.processando, width="100%",
                                      disabled=(VendasState.cliente_id == "") | (VendasState.selected_items.length() == 0) | VendasState.creation_uncertain),
                            rx.cond(VendasState.creation_uncertain,
                                rx.link("Conferir vendas registradas", href="/vendas")),
                            align="stretch", spacing="4", width="100%",
                        ),
                    ),
                    class_name="sale-summary", align="stretch", spacing="4",
                ),
                class_name="sale-workspace",
            ),
            width="100%", spacing="5", on_mount=VendasState.load_sale_references,
        ),
        "Nova venda",
    )


def sales_detail_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.cond(VendasState.payment_flow == "ASAAS", _payment_panel(),
                rx.text("Histórico de parcelas da venda anterior à integração ASAAS.")),
            rx.cond(
                AuthState.is_manager & (VendasState.payment_flow != "ASAAS") & (VendasState.payment_methods.length() > 0),
                rx.select.root(
                    rx.select.trigger(placeholder="Forma realmente recebida"),
                    rx.select.content(
                        rx.foreach(
                            VendasState.payment_methods,
                            lambda method: rx.select.item(
                                method["name"],
                                value=method["id"],
                            ),
                        )
                    ),
                    value=VendasState.forma_recebida_id,
                    on_change=VendasState.set_forma_recebida_id,
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.foreach(
                VendasState.parcelas,
                lambda parcela: rx.hstack(
                    rx.vstack(
                        rx.text(
                            f"Parcela {parcela['numero_parcela']} de "
                            f"{parcela['total_parcelas']}"
                        ),
                        rx.text(f"Valor: R$ {parcela['valor']}"),
                        rx.text(f"Vencimento: {parcela['vencimento']}"),
                        rx.text(f"Status: {parcela['status']}"),
                        rx.cond(
                            parcela["status"] == "RECEBIDA",
                            rx.text(
                                f"Recebido em {parcela['recebido_em']} por "
                                f"{parcela['recebido_por']} via "
                                f"{parcela['forma_recebida']}"
                            ),
                            rx.fragment(),
                        ),
                        align="start",
                    ),
                    rx.cond(
                        (parcela["status"] == "PENDENTE") & AuthState.is_manager & (VendasState.payment_flow != "ASAAS"),
                        rx.button(
                            "Confirmar recebimento integral",
                            on_click=VendasState.receive_installment(parcela["id"]),
                            loading=VendasState.processando,
                        ),
                        rx.fragment(),
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                    class_name="form-card",
                ),
            ),
            rx.cond(VendasState.processando, rx.spinner()),
            rx.cond(VendasState.mensagem != "", rx.callout(VendasState.mensagem)),
            rx.cond(
                VendasState.erro != "",
                rx.callout(VendasState.erro, color_scheme="red"),
            ),
            rx.button("Atualizar pagamento", on_click=VendasState.load_sale, variant="outline", loading=VendasState.processando),
            rx.link("Voltar para vendas", href="/vendas"),
            spacing="4",
            align="start",
            width="100%",
            max_width="760px",
            on_mount=VendasState.load_sale,
        ),
        "Pagamento da venda",
    )
