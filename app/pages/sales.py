import reflex as rx

from app.components.app_shell import shell
from app.state.auth_state import AuthState
from app.state.vendas_state import VendasState


def sales_create_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.text(
                "Informe IDs já cadastrados. A venda e a reserva são criadas no Xano; "
                "o Xano também registra o cronograma de parcelas."
            ),
            rx.input(
                placeholder="ID do cliente",
                aria_label="ID do cliente",
                value=VendasState.cliente_id,
                on_change=VendasState.set_cliente_id,
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
            rx.text("Itens da venda (JSON)"),
            rx.text_area(
                value=VendasState.itens_json,
                on_change=VendasState.set_itens_json,
                min_height="130px",
                width="100%",
            ),
            rx.text(
                'Exemplo de veículo: [{"veiculo_id": 10, "qtd": 1}]. '
                'Peça: [{"peca_id": 25, "qtd": 2}]. É possível incluir vários itens.'
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
            on_mount=VendasState.load_payment_methods,
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
