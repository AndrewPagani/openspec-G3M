import reflex as rx

from app.pages.login import login
from app.state.auth_state import AuthState


def nav_item(
    label: str,
    href: str,
    icon: str,
    active: rx.Var = False,
    visible: rx.Var = True,
) -> rx.Component:
    return rx.cond(
        visible,
        rx.link(
            rx.hstack(
                rx.icon(icon, size=18, stroke_width=1.7),
                rx.text(label),
                align="center",
                spacing="3",
            ),
            href=href,
            class_name=rx.cond(
                active,
                "nav-item nav-item-active",
                "nav-item",
            ),
        ),
        rx.fragment(),
    )


def shell(
    content: rx.Component, title: str = "Gerenciamento", allowed: rx.Var = True
) -> rx.Component:
    return rx.cond(
        AuthState.authenticated,
        rx.cond(
            allowed,
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.box("G3M", class_name="sidebar-brand-mark"),
                        rx.vstack(
                            rx.heading("AutoGestão", size="4"),
                            rx.text("GESTÃO AUTOMOTIVA", class_name="sidebar-brand-caption"),
                            align="start",
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                        class_name="sidebar-brand",
                    ),
                    rx.divider(class_name="sidebar-divider"),
                    nav_item(
                        "Dashboard", "/gerenciamento", "layout-dashboard",
                        title == "Gerenciamento",
                    ),
                    nav_item("Clientes", "/clientes", "users-round", title in ("Clientes", "Novo cliente", "Detalhe do cliente")),
                    nav_item(
                        "Veículos", "/veiculos", "car-front",
                        title in ("Veículos", "Novo veículo", "Detalhe do veículo"),
                    ),
                    nav_item(
                        "Peças e estoque", "/pecas", "boxes",
                        title in ("Peças e estoque", "Nova peça", "Detalhe da peça"),
                    ),
                    nav_item(
                        "Vendas", "/vendas", "receipt-text",
                        title in ("Vendas", "Nova venda", "Detalhe da venda"),
                    ),
                    nav_item(
                        "Usuários", "/usuarios", "user-round",
                        title in ("Usuários", "Novo usuário", "Detalhe do usuário"),
                        AuthState.is_admin,
                    ),
                    nav_item(
                        "Auditoria", "/auditoria", "scroll-text",
                        title == "Auditoria",
                        AuthState.is_manager,
                    ),
                    nav_item(
                        "Configurações", "/configuracoes", "settings-2",
                        title == "Configurações",
                        AuthState.is_manager,
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.center(
                            rx.icon("user-round", size=18, stroke_width=1.7),
                            class_name="sidebar-user-avatar",
                        ),
                        rx.vstack(
                            rx.text(
                                AuthState.profile + ": " + AuthState.user_name,
                                class_name="user-label",
                            ),
                            rx.hstack(
                                rx.box(class_name="sidebar-online-indicator"),
                                rx.text("On-line", class_name="sidebar-online-label"),
                                align="center",
                                spacing="2",
                            ),
                            align="start",
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                        class_name="sidebar-user",
                    ),
                    rx.button(
                        "Sair",
                        on_click=AuthState.logout,
                        variant="outline",
                        class_name="sidebar-logout",
                    ),
                    class_name="sidebar",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading(title, size="7"),
                        rx.spacer(),
                        rx.cond(
                            title in ("Veículos", "Novo veículo"),
                            rx.hstack(
                                rx.button(
                                    rx.icon("bell", size=19, stroke_width=1.7),
                                    variant="ghost",
                                    aria_label="Notificações",
                                    class_name="header-icon-button",
                                ),
                                rx.center(
                                    rx.icon("user-round", size=19, stroke_width=1.7),
                                    class_name="header-user-avatar",
                                ),
                                align="center",
                                spacing="3",
                                class_name="header-controls",
                            ),
                            rx.fragment(),
                        ),
                        class_name="topbar",
                    ),
                    rx.box(content, class_name="content"),
                    class_name="main",
                ),
                class_name=rx.cond(
                    title == "Veículos",
                    "app-shell internal-app-shell vehicle-app-shell",
                    rx.cond(
                        title == "Novo veículo",
                        "app-shell internal-app-shell vehicle-app-shell",
                        "app-shell internal-app-shell",
                    ),
                ),
            ),
            rx.center(rx.callout("Acesso negado para o seu perfil.", color_scheme="red"), min_height="100vh"),
        ),
        login(),
    )
