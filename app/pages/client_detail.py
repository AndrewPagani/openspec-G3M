import reflex as rx

from app.components.app_shell import shell
from app.state.client_detail_state import ClientDetailState


def _field(label: str, key: str, icon: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=16, stroke_width=1.7),
            rx.text(label, class_name="vehicle-detail-label"),
            align="center",
            spacing="2",
        ),
        rx.text(ClientDetailState.client[key], class_name="vehicle-detail-value"),
        align="start",
        class_name="vehicle-detail-field",
    )


def client_detail_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.link(
                rx.button(
                    rx.hstack(
                        rx.icon("arrow-left", size=16),
                        rx.text("Voltar para clientes"),
                        align="center",
                        spacing="2",
                    ),
                    variant="outline",
                ),
                href="/clientes",
            ),
            rx.cond(
                ClientDetailState.loading | (ClientDetailState.read_id != ClientDetailState.router.page.params.get("id", "")),
                rx.center(rx.spinner(), min_height="260px"),
                rx.cond(
                    ClientDetailState.error != "",
                    rx.callout(
                        ClientDetailState.error,
                        color_scheme="red",
                        role="alert",
                    ),
                    rx.vstack(
                        rx.text("DETALHES DO CLIENTE", class_name="vehicle-detail-kicker"),
                        rx.heading(ClientDetailState.client["name"], size="7"),
                        rx.text("Dados cadastrais consultados diretamente no Xano.", class_name="muted"),
                        rx.card(
                            rx.grid(
                                _field("CPF", "cpf", "fingerprint"),
                                _field("Telefone / WhatsApp", "phone", "phone"),
                                _field("E-mail", "email", "mail"),
                                _field("Cadastro realizado em", "created_at", "calendar"),
                                columns="repeat(2, minmax(0, 1fr))",
                                class_name="vehicle-detail-fields",
                            ),
                            class_name="vehicle-detail-card",
                        ),
                        spacing="4",
                        align="stretch",
                        width="100%",
                    ),
                ),
            ),
            spacing="4",
            align="stretch",
            width="100%",

        ),
        "Detalhe do cliente",
    )
