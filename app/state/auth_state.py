from __future__ import annotations

import reflex as rx

from app.services.xano_client import XanoError, client


def _role_is_manager(role: str) -> bool:
    return role.strip().casefold() == "gerente"


class AuthState(rx.State):
    token: str = rx.LocalStorage("")
    user_name: str = rx.LocalStorage("")
    profile: str = rx.LocalStorage("")
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

    def login(self) -> rx.event.EventSpec:
        self.busy = True
        self.error = ""
        self.notice = ""
        try:
            if not self.email or not self.password:
                raise XanoError("Informe e-mail e senha.")
            result = client.login(self.email, self.password)
            raw_token = str(result.get("authToken") or result.get("token") or "").strip()
            self.token = raw_token[7:].strip() if raw_token.lower().startswith("bearer ") else raw_token
            user = result.get("user") or result
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

    def logout(self) -> rx.event.EventSpec:
        self.token = ""
        self.user_name = ""
        self.profile = ""
        self.email = ""
        self.password = ""
        self.error = ""
        self.notice = ""
        self.busy = False
        return rx.redirect("/login")
