from __future__ import annotations

import reflex as rx

from app.services.xano_client import XanoError, client


def _role_is_manager(role: str) -> bool:
    return role.strip().casefold() == "gerente"


class AuthState(rx.State):
    token: str = rx.LocalStorage("")
    user_name: str = rx.LocalStorage("")
    profile: str = rx.LocalStorage("")
    account_id: str = rx.LocalStorage("")
    email: str = ""
    password: str = ""
    busy: bool = False
    error: str = ""
    notice: str = ""

    @rx.var
    def authenticated(self) -> bool:
        return bool(self.token)

    @rx.var
    def is_admin(self) -> bool:
        return self.profile.strip().casefold() == "administrador"

    @rx.var
    def is_manager(self) -> bool:
        return _role_is_manager(self.profile) or self.is_admin

    def set_email(self, value: str) -> None:
        self.email = value
        self.error = ""
        self.notice = ""

    def set_password(self, value: str) -> None:
        self.password = value
        self.error = ""
        self.notice = ""

    def show_password_help(self) -> None:
        self.error = ""
        self.notice = "Solicite a redefinição de senha ao administrador da concessionária."

    async def login(self) -> rx.event.EventSpec:
        self.busy = True
        self.error = ""
        self.notice = ""
        try:
            if not self.email or not self.password:
                raise XanoError("Informe e-mail e senha.")
            result = await client.async_login(self.email, self.password)
            raw_token = str(result.get("authToken") or result.get("token") or "").strip()
            normalized_token = raw_token[7:].strip() if raw_token.lower().startswith("bearer ") else raw_token
            if not normalized_token:
                raise XanoError("Resposta de autenticação inválida.")
            await clear_operational_state(self)
            self.token = normalized_token
            user = result.get("user") or result
            self.account_id = str(user.get("id") or self.email.strip().casefold())
            profile = user.get("perfil") or user.get("profile") or {}
            self.user_name = str(user.get("UNome") or user.get("name") or user.get("nome") or self.email)
            role = profile.get("Cargo") if isinstance(profile, dict) else profile
            self.profile = str(role or user.get("cargo") or "Vendedor")
            if not self.token:
                raise XanoError("Resposta de autenticação inválida.")
            return rx.redirect("/gerenciamento")
        except XanoError as exc:
            self.error = str(exc)
        finally:
            self.busy = False

    async def logout(self) -> rx.event.EventSpec:
        await clear_operational_state(self)
        self.token = ""
        self.account_id = ""
        self.user_name = ""
        self.profile = ""
        self.email = ""
        self.password = ""
        self.error = ""
        self.notice = ""
        self.busy = False
        return rx.redirect("/login")


async def clear_operational_state(auth):
    # LocalStorage preferences belong to SettingsState and are intentionally retained.
    from app.services.catalogs import catalogs
    from app.state.client_detail_state import ClientDetailState
    from app.state.dashboard_state import DashboardState
    from app.state.form_state import FormState
    from app.state.read_lifecycle import NavigationState, cancel_reads
    from app.state.resource_state import (
        ClientsState,
        PartsState,
        UsersState,
        VehiclesState,
    )
    from app.state.settings_state import SettingsState
    from app.state.vehicle_detail_state import VehicleDetailState
    from app.state.vendas_state import SaleDetailState, VendasState
    settings = await auth.get_state(SettingsState)
    settings.account_key = settings.base_display_name = ""
    catalogs.invalidate()
    nav = await auth.get_state(NavigationState)
    nav.generation += 1
    cancel_reads(auth.router.session.client_token)
    for cls in (ClientsState, VehiclesState, PartsState, UsersState, ClientDetailState,
                VehicleDetailState, VendasState, SaleDetailState, FormState, DashboardState):
        state = await auth.get_state(cls)
        state.reset()
