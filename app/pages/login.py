import reflex as rx

from app.state.auth_state import AuthState


def login() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("AutoGestão", size="8"),
                rx.text("Acesse sua operação comercial", class_name="muted"),
                rx.input(placeholder="E-mail", type="email", on_change=AuthState.set_email),
                rx.input(placeholder="Senha", type="password", on_change=AuthState.set_password),
                rx.cond(AuthState.error != "", rx.callout(AuthState.error, color_scheme="red")),
                rx.button("Entrar", on_click=AuthState.login, width="100%"),
                rx.text("Entre com sua conta cadastrada no Xano.", class_name="hint"),
                class_name="login-card",
            )
        ),
        class_name="login-page",
    )
