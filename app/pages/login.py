from __future__ import annotations

import reflex as rx

from app.state.auth_state import AuthState


def _field(
    placeholder: str,
    field_type: str,
    on_change: rx.event.EventHandler,
    input_name: str,
) -> rx.Component:
    if input_name == "email":
        icon = rx.el.svg(
            rx.el.path(d="M20 21a8 8 0 0 0-16 0"),
            rx.el.circle(cx="12", cy="7", r="4"),
            view_box="0 0 24 24",
            aria_hidden=True,
            class_name="login-field-icon",
        )
    else:
        icon = rx.el.svg(
            rx.el.rect(x="5", y="11", width="14", height="10", rx="1.5"),
            rx.el.path(d="M8 11V8a4 4 0 0 1 8 0v3"),
            view_box="0 0 24 24",
            aria_hidden=True,
            class_name="login-field-icon",
        )

    return rx.hstack(
        icon,
        rx.input(
            id=f"login-{input_name}",
            name=input_name,
            type=field_type,
            placeholder=placeholder,
            aria_label=placeholder,
            required=True,
            on_change=on_change,
            class_name="login-input",
        ),
        class_name="login-field",
    )


def login() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.section(
                rx.vstack(
                    rx.box("G3M", class_name="login-emblem"),
                    rx.heading("Acesse sua concessionária", class_name="login-title"),
                    rx.text(
                        "Entre com as credenciais da sua operação.",
                        class_name="login-subtitle",
                    ),
                    rx.form(
                        rx.vstack(
                            _field(
                                "E-mail",
                                "email",
                                AuthState.set_email,
                                "email",
                            ),
                            _field(
                                "Senha",
                                "password",
                                AuthState.set_password,
                                "password",
                            ),
                            rx.cond(
                                AuthState.error != "",
                                rx.callout(
                                    AuthState.error,
                                    color_scheme="red",
                                    class_name="login-message login-error",
                                    role="alert",
                                ),
                            ),
                            rx.cond(
                                AuthState.notice != "",
                                rx.callout(
                                    AuthState.notice,
                                    color_scheme="blue",
                                    class_name="login-message login-notice",
                                    role="status",
                                ),
                            ),
                            rx.button(
                                rx.cond(AuthState.busy, "Entrando...", "Entrar"),
                                type="submit",
                                disabled=AuthState.busy,
                                class_name="login-button",
                            ),
                            class_name="login-form-fields",
                        ),
                        on_submit=AuthState.login,
                        reset_on_submit=False,
                        class_name="login-form",
                    ),
                    rx.button(
                        "esqueci a senha",
                        type="button",
                        variant="ghost",
                        on_click=AuthState.show_password_help,
                        class_name="login-link",
                    ),
                    class_name="login-form-content",
                ),
                class_name="login-form-panel",
                aria_label="Acesso à concessionária",
            ),
            rx.el.aside(
                rx.image(
                    src="/illustrations/g3m-diagnostics.svg",
                    alt="Ilustração técnica de um veículo em uma plataforma de diagnóstico",
                    class_name="login-illustration",
                ),
                rx.vstack(
                    rx.text("CENTRO DE DIAGNÓSTICO", class_name="visual-kicker"),
                    rx.heading(
                        "Sua operação em movimento.",
                        class_name="visual-title",
                    ),
                    rx.text(
                        "Gestão integrada para cada etapa da concessionária.",
                        class_name="visual-caption",
                    ),
                    class_name="visual-copy",
                ),
                class_name="login-visual-panel",
                aria_label="Ilustração técnica automotiva",
            ),
            class_name="login-layout",
        ),
        class_name="login-page",
    )
