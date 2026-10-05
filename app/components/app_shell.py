import reflex as rx

from app.pages.login import login
from app.state.auth_state import AuthState


def nav_item(label: str, href: str, visible: rx.Var = True) -> rx.Component:
    return rx.cond(
        visible,
        rx.link(label, href=href, class_name="nav-item"),
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
                    rx.heading("AutoGestão", size="6"),
                    rx.text("Unidade principal", class_name="muted"),
                    rx.divider(),
                    nav_item("Dashboard", "/gerenciamento"),
                    nav_item("Clientes", "/clientes"),
                    nav_item("Veículos", "/veiculos"),
                    nav_item("Peças e estoque", "/pecas"),
                    nav_item("Vendas", "/vendas"),
                    nav_item("Usuários", "/usuarios", AuthState.is_admin),
                    nav_item("Auditoria", "/auditoria", AuthState.is_manager),
                    nav_item("Configurações", "/configuracoes", AuthState.is_manager),
                    rx.spacer(),
                    rx.text(AuthState.user_name, class_name="user-label"),
                    rx.text(AuthState.profile, class_name="muted"),
                    rx.button("Sair", on_click=AuthState.logout, variant="outline"),
                    class_name="sidebar",
                ),
                rx.vstack(
                    rx.hstack(rx.heading(title, size="7"), rx.spacer(), class_name="topbar"),
                    rx.box(content, class_name="content"),
                    class_name="main",
                ),
                class_name="app-shell",
            ),
            rx.center(rx.callout("Acesso negado para o seu perfil.", color_scheme="red"), min_height="100vh"),
        ),
        login(),
    )
