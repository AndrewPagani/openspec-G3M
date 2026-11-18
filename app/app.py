import reflex as rx

from app.state.auth_state import AuthState
from app.pages.gerenciamento import gerenciamento
from app.pages.login import login
from app.pages.resource import resource_page
from app.pages.sales import sales_create_page, sales_detail_page, sales_list_page
from app.pages.vehicle_detail import vehicle_detail_page
from app.pages.client_detail import client_detail_page
from app.pages.simple import detail_page, form_page
from app.pages.settings import settings_page


def index() -> rx.Component:
    return rx.cond(AuthState.authenticated, gerenciamento(), login())


app = rx.App(stylesheets=["/styles.css"])
app.add_page(index, route="/")
app.add_page(login, route="/login")
app.add_page(gerenciamento, route="/gerenciamento")
app.add_page(lambda: resource_page("Clientes", "/clientes", "/clientes/novo"), route="/clientes")
app.add_page(lambda: form_page("Novo cliente", "clientes", ("Nome", "CPF", "Telefone", "E-mail")), route="/clientes/novo")
app.add_page(client_detail_page, route="/clientes/[id]")
app.add_page(lambda: resource_page("Veículos", "/veiculos", "/veiculos/novo"), route="/veiculos")
app.add_page(lambda: form_page("Novo veículo", "veiculos", ("Marca", "Modelo", "Cor", "Ano", "Placa", "Chassi", "Quilometragem", "Preço", "Status (ID)", "URL da imagem"), AuthState.is_manager), route="/veiculos/novo")
app.add_page(vehicle_detail_page, route="/veiculos/[id]")
app.add_page(lambda: resource_page("Peças e estoque", "/pecas", "/pecas/novo"), route="/pecas")
app.add_page(lambda: form_page("Nova peça", "pecas", ("Nome", "Preço", "Quantidade", "Área (ID)"), AuthState.is_manager), route="/pecas/novo")
app.add_page(lambda: detail_page("Detalhe da peça", "pecas", AuthState.is_manager), route="/pecas/[id]")
app.add_page(sales_list_page, route="/vendas")
app.add_page(sales_create_page, route="/vendas/nova")
app.add_page(sales_detail_page, route="/vendas/[id]")
app.add_page(lambda: resource_page("Usuários", "/usuarios", "/usuarios/novo", AuthState.is_admin), route="/usuarios")
app.add_page(lambda: form_page("Novo usuário", "usuarios", ("Nome", "E-mail", "Perfil"), AuthState.is_admin), route="/usuarios/novo")
app.add_page(lambda: detail_page("Detalhe do usuário", "usuarios", AuthState.is_admin), route="/usuarios/[id]")
app.add_page(settings_page, route="/configuracoes")
