from contextlib import asynccontextmanager

import reflex as rx

from app.pages.client_detail import client_detail_page
from app.pages.gerenciamento import gerenciamento
from app.pages.login import login
from app.pages.resource import resource_page
from app.pages.sales import sales_create_page, sales_detail_page, sales_list_page
from app.pages.settings import settings_page
from app.pages.simple import detail_page, form_page
from app.pages.vehicle_detail import vehicle_detail_page
from app.state.auth_state import AuthState
from app.state.read_lifecycle import NavigationState


def index() -> rx.Component:
    return rx.cond(AuthState.authenticated, gerenciamento(), login())


from app.services.catalogs import catalogs
from app.services.xano_client import client


@asynccontextmanager
async def backend_services():
    async with client.lifespan():
        try:
            yield
        finally:
            await catalogs.close()


app = rx.App(stylesheets=["/styles.css"])
app.register_lifespan_task(backend_services)
app.add_page(index, route="/", on_load=NavigationState.changed)
app.add_page(login, route="/login", on_load=NavigationState.changed)
app.add_page(gerenciamento, route="/gerenciamento", on_load=NavigationState.changed)
app.add_page(
    lambda: resource_page("Clientes", "/clientes", "/clientes/novo"),
    route="/clientes",
    on_load=NavigationState.changed,
)
app.add_page(
    lambda: form_page(
        "Novo cliente", "clientes", ("Nome", "CPF", "Telefone", "E-mail")
    ),
    route="/clientes/novo",
    on_load=NavigationState.changed,
)
app.add_page(
    client_detail_page, route="/clientes/[id]", on_load=NavigationState.changed
)
app.add_page(
    lambda: resource_page("Veículos", "/veiculos", "/veiculos/novo"),
    route="/veiculos",
    on_load=NavigationState.changed,
)
app.add_page(
    lambda: form_page(
        "Novo veículo",
        "veiculos",
        (
            "Marca",
            "Modelo",
            "Cor",
            "Ano",
            "Placa",
            "Chassi",
            "Quilometragem",
            "Preço",
            "Status (ID)",
            "URL da imagem",
        ),
        AuthState.is_manager,
    ),
    route="/veiculos/novo",
    on_load=NavigationState.changed,
)
app.add_page(
    vehicle_detail_page, route="/veiculos/[id]", on_load=NavigationState.changed
)
app.add_page(
    lambda: resource_page("Peças e estoque", "/pecas", "/pecas/novo"),
    route="/pecas",
    on_load=NavigationState.changed,
)
app.add_page(
    lambda: form_page(
        "Nova peça",
        "pecas",
        ("Nome", "Preço", "Quantidade", "Área (ID)"),
        AuthState.is_manager,
    ),
    route="/pecas/novo",
    on_load=NavigationState.changed,
)
app.add_page(
    lambda: detail_page("Detalhe da peça", "pecas", AuthState.is_manager),
    route="/pecas/[id]",
    on_load=NavigationState.changed,
)
app.add_page(sales_list_page, route="/vendas", on_load=NavigationState.changed)
app.add_page(sales_create_page, route="/vendas/nova", on_load=NavigationState.changed)
app.add_page(sales_detail_page, route="/vendas/[id]", on_load=NavigationState.changed)
app.add_page(
    lambda: resource_page(
        "Usuários", "/usuarios", "/usuarios/novo", AuthState.is_admin
    ),
    route="/usuarios",
    on_load=NavigationState.changed,
)
app.add_page(
    lambda: form_page(
        "Novo usuário", "usuarios", ("Nome", "E-mail", "Perfil"), AuthState.is_admin
    ),
    route="/usuarios/novo",
    on_load=NavigationState.changed,
)
app.add_page(
    lambda: detail_page("Detalhe do usuário", "usuarios", AuthState.is_admin),
    route="/usuarios/[id]",
    on_load=NavigationState.changed,
)
app.add_page(settings_page, route="/configuracoes", on_load=NavigationState.changed)
