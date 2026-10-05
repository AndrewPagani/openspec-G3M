import reflex as rx

from app.components.app_shell import shell
from app.state.auth_state import AuthState
from app.state.form_state import FormState


def form_page(
    title: str, endpoint: str, fields: tuple[str, ...], allowed: rx.Var = True
) -> rx.Component:
    return shell(
        rx.vstack(
            rx.text("Os campos serão validados e persistidos pelo Xano.", class_name="muted"),
            *[
                rx.input(
                    placeholder=field,
                    aria_label=field,
                    value=FormState.values.get(field, ""),
                    on_change=lambda value, name=field: FormState.set_field(name, value),
                )
                for field in fields
            ],
            rx.cond(FormState.error != "", rx.callout(FormState.error, color_scheme="red")),
            rx.cond(FormState.success != "", rx.callout(FormState.success, color_scheme="green")),
            rx.hstack(
                rx.button("Salvar", on_click=FormState.save(endpoint), loading=FormState.saving),
                rx.link(rx.button("Cancelar", variant="outline"), href=f"/{endpoint}"),
            ),
            class_name="form-card",
        ), title, allowed)


def forbidden() -> rx.Component:
    return shell(rx.callout("Acesso negado para o seu perfil.", color_scheme="red"), "Acesso negado")


def detail_page(title: str, endpoint: str, allowed: rx.Var = True) -> rx.Component:
    return shell(
        rx.vstack(
            rx.callout(
                "O detalhe será carregado pela API do Xano quando um identificador for informado.",
                icon="info",
            ),
            rx.link("Voltar para a lista", href=f"/{endpoint}"),
            class_name="page-stack",
        ),
        title,
        allowed,
    )
