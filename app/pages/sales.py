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
        rx.table.cell(rx.link("Parcelas", href="/vendas/" + row["id"])),
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
                rx.link(rx.button("Criar venda"), href="/vendas/nova"),
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
        rx.text("R$ " + row["preco"]),
        rx.button("Selecionar", on_click=VendasState.add_vehicle(row["id"])),
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
                aria_label="Quantidade da peça",
            ),
            rx.button(
                "Adicionar",
                on_click=VendasState.add_part_for_id(row["id"]),
            ),
            align="center",
        ),
        class_name="sale-picker-card",
    )


def sales_create_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.text("Selecione o cliente, os itens disponíveis e confirme os valores da venda."),
            rx.select.root(
                rx.select.trigger(placeholder="Selecione o cliente"),
                rx.select.content(
                    rx.foreach(
                        VendasState.clientes,
                        lambda client: rx.select.item(client["nome"], value=client["id"]),
                    )
                ),
                value=VendasState.cliente_id,
                on_change=VendasState.set_cliente_id,
                width="100%",
            ),
            rx.heading("Veículos disponíveis", size="4"),
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(VendasState.veiculos_disponiveis, _vehicle_picker),
                    spacing="4",
                ),
                type="scroll",
                scrollbars="horizontal",
                class_name="sale-picker-carousel",
            ),
            rx.heading("Peças com estoque", size="4"),
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(VendasState.pecas_disponiveis, _part_picker),
                    spacing="4",
                ),
                type="scroll",
                scrollbars="horizontal",
                class_name="sale-picker-carousel",
            ),
            rx.heading("Itens selecionados", size="4"),
            rx.foreach(
                VendasState.selected_items,
                lambda item: rx.hstack(
                    rx.text(item["nome"] + " x" + item["qtd"]),
                    rx.text("R$ " + item["preco"]),
                    rx.button("Remover", on_click=VendasState.remove_item(item["id"]), size="1"),
                    justify="between",
                    width="100%",
                    class_name="sale-selected-item",
                ),
            ),
            rx.select.root(
                rx.select.trigger(placeholder="Selecione a forma de pagamento"),
                rx.select.content(
                    rx.foreach(
                        VendasState.payment_methods,
                        lambda method: rx.select.item(
                            method["name"],
                            value=method["id"],
                        ),
                    )
                ),
                value=VendasState.forma_pagamento_id,
                on_change=VendasState.set_forma_pagamento_id,
                width="100%",
            ),
            rx.input(
                placeholder="Desconto (0 se não houver)",
                aria_label="Desconto",
                value=VendasState.desconto,
                on_change=VendasState.set_desconto,
            ),
            rx.input(
                type="number",
                min="1",
                max="24",
                placeholder="Quantidade de parcelas (1 a 24)",
                aria_label="Quantidade de parcelas",
                value=VendasState.numero_parcelas,
                on_change=VendasState.set_numero_parcelas,
            ),
            rx.hstack(
                rx.text("Valor bruto: " + VendasState.valor_bruto_display),
                rx.text("Valor final: " + VendasState.valor_final_display),
                justify="between",
                width="100%",
                class_name="sale-totals",
            ),
            rx.cond(
                VendasState.venda_id == "",
                rx.button(
                    "Criar e reservar venda",
                    on_click=VendasState.create_sale,
                    loading=VendasState.processando,
                ),
                rx.fragment(),
            ),
            rx.cond(
                VendasState.venda_id != "",
                rx.vstack(
                    rx.heading(f"Venda #{VendasState.venda_id} reservada", size="4"),
                    rx.link(
                        "Ver parcelas e registrar recebimentos",
                        href=f"/vendas/{VendasState.venda_id}",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(VendasState.mensagem != "", rx.callout(VendasState.mensagem)),
            rx.cond(
                VendasState.erro != "",
                rx.callout(VendasState.erro, color_scheme="red"),
            ),
            spacing="4",
            align="start",
            width="100%",
            max_width="760px",
            on_mount=VendasState.load_sale_references,
        ),
        "Nova venda",
    )


def sales_detail_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.text(
                "Parcelas registradas no Xano. A baixa manual apenas registra "
                "a informação confirmada pela equipe; não processa pagamentos."
            ),
            rx.cond(
                AuthState.is_manager & (VendasState.payment_methods.length() > 0),
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
                        (parcela["status"] == "PENDENTE") & AuthState.is_manager,
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
            rx.link("Voltar para vendas", href="/vendas"),
            spacing="4",
            align="start",
            width="100%",
            max_width="760px",
            on_mount=VendasState.load_sale,
        ),
        "Parcelas da venda",
    )
