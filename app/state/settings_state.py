from __future__ import annotations

import json
from typing import Any

import reflex as rx

from app.state.auth_state import AuthState

WIDGETS = (
    ("metrics", "Indicadores principais"),
    ("sales_charts", "Gráficos de vendas"),
    ("inventory", "Estoque"),
    ("sales_breakdown", "Detalhamento de vendas"),
)
WIDGET_IDS = tuple(widget_id for widget_id, _ in WIDGETS)
THEME_MODES = ("dark", "light", "system")


def _default_preferences() -> dict[str, Any]:
    return {
        "display_name": "",
        "appearance_mode": "dark",
        "dashboard_title": "Dashboard",
        "visible_widgets": list(WIDGET_IDS),
        "widget_order": list(WIDGET_IDS),
    }


def _decode_store(raw: str) -> dict[str, dict[str, Any]]:
    try:
        store = json.loads(raw or "{}")
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("As preferências locais estão inválidas.") from exc
    if not isinstance(store, dict):
        raise ValueError("As preferências locais estão em formato inválido.")
    if any(not isinstance(value, dict) for value in store.values()):
        raise ValueError("As preferências locais estão em formato inválido.")
    return store


def _validate_preferences(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("As preferências da conta estão em formato inválido.")
    defaults = _default_preferences()
    display_name = value.get("display_name", defaults["display_name"])
    appearance_mode = value.get("appearance_mode", defaults["appearance_mode"])
    dashboard_title = value.get("dashboard_title", defaults["dashboard_title"])
    visible_widgets = value.get("visible_widgets", defaults["visible_widgets"])
    widget_order = value.get("widget_order", defaults["widget_order"])

    if not isinstance(display_name, str) or len(display_name.strip()) > 40:
        raise ValueError("O nome de exibição deve ter até 40 caracteres.")
    if appearance_mode not in THEME_MODES:
        raise ValueError("Selecione um tema válido.")
    if (
        not isinstance(dashboard_title, str)
        or not dashboard_title.strip()
        or len(dashboard_title.strip()) > 40
    ):
        raise ValueError("O título do Dashboard deve ter de 1 a 40 caracteres.")
    if (
        not isinstance(widget_order, list)
        or len(widget_order) != len(WIDGET_IDS)
        or any(not isinstance(widget_id, str) for widget_id in widget_order)
        or set(widget_order) != set(WIDGET_IDS)
    ):
        raise ValueError("A ordem dos widgets está inválida.")
    if (
        not isinstance(visible_widgets, list)
        or any(not isinstance(widget_id, str) for widget_id in visible_widgets)
        or any(widget_id not in WIDGET_IDS for widget_id in visible_widgets)
        or len(set(visible_widgets)) != len(visible_widgets)
    ):
        raise ValueError("A seleção de widgets está inválida.")
    return {
        "display_name": display_name.strip(),
        "appearance_mode": appearance_mode,
        "dashboard_title": dashboard_title.strip(),
        "visible_widgets": visible_widgets,
        "widget_order": widget_order,
    }


def _account_preferences(raw: str, account_id: str) -> dict[str, Any]:
    if not account_id:
        return _default_preferences()
    store = _decode_store(raw)
    return _validate_preferences(store.get(account_id, _default_preferences()))


def _apply_theme(mode: str) -> rx.event.EventSpec:
    return rx.call_script(
        "(()=>{const root=document.documentElement;const mode="
        + json.dumps(mode)
        + ";const media=window.matchMedia('(prefers-color-scheme: dark)');"
        "if(window.__openspecThemeMedia&&window.__openspecThemeListener){"
        "window.__openspecThemeMedia.removeEventListener('change',window.__openspecThemeListener);}"
        "const apply=()=>{const resolved=mode==='system'?(media.matches?'dark':'light'):mode;"
        "root.setAttribute('data-app-theme',resolved);"
        "const theme=root.querySelector('.radix-themes[data-is-root-theme=\"true\"]');"
        "if(theme){theme.classList.remove('dark','light');theme.classList.add(resolved);}};"
        "window.__openspecThemeMedia=media;window.__openspecThemeListener=apply;"
        "if(mode==='system'){media.addEventListener('change',apply);}apply();})()"
    )


class SettingsState(rx.State):
    preferences_json: str = rx.LocalStorage("{}")
    account_key: str = ""
    base_display_name: str = ""
    display_name: str = ""
    appearance_mode: str = "dark"
    dashboard_title: str = "Dashboard"
    visible_widgets: list[str] = list(WIDGET_IDS)
    widget_order: list[str] = list(WIDGET_IDS)
    error: str = ""
    notice: str = ""

    @rx.var
    def active_display_name(self) -> str:
        try:
            preferences = _account_preferences(
                self.preferences_json, self.account_key
            )
        except ValueError:
            return self.base_display_name
        return preferences["display_name"] or self.base_display_name

    @rx.var
    def active_dashboard_title(self) -> str:
        try:
            preferences = _account_preferences(
                self.preferences_json, self.account_key
            )
        except ValueError:
            return "Dashboard"
        return preferences["dashboard_title"]

    @rx.var
    def active_visible_widgets(self) -> list[str]:
        try:
            return _account_preferences(
                self.preferences_json, self.account_key
            )["visible_widgets"]
        except ValueError:
            return list(WIDGET_IDS)

    @rx.var
    def active_widget_order(self) -> list[str]:
        try:
            preferences = _account_preferences(
                self.preferences_json, self.account_key
            )
        except ValueError:
            return list(WIDGET_IDS)
        return [
            widget_id
            for widget_id in preferences["widget_order"]
            if widget_id in preferences["visible_widgets"]
        ]

    async def load(self) -> rx.event.EventSpec:
        auth_state = await self.get_state(AuthState)
        self.account_key = auth_state.account_id or auth_state.user_name.strip().casefold()
        self.base_display_name = auth_state.user_name
        self.error = ""
        self.notice = ""
        try:
            preferences = _account_preferences(
                self.preferences_json, self.account_key
            )
        except ValueError as exc:
            self.error = str(exc) + " Restaure os padrões para continuar."
            preferences = _default_preferences()
        self._set_draft(preferences)
        return _apply_theme(preferences["appearance_mode"])

    def set_display_name(self, value: str) -> None:
        self.display_name = value
        self.error = ""
        self.notice = ""

    def set_dashboard_title(self, value: str) -> None:
        self.dashboard_title = value
        self.error = ""
        self.notice = ""

    def set_appearance_mode(self, mode: str) -> rx.event.EventSpec:
        if mode not in THEME_MODES:
            raise ValueError("Selecione um tema válido.")
        self.appearance_mode = mode
        self.error = ""
        self.notice = ""
        return _apply_theme(mode)

    def set_widget_visibility(self, widget_id: str, enabled: bool) -> None:
        if widget_id not in WIDGET_IDS:
            raise ValueError("Widget desconhecido.")
        if enabled and widget_id not in self.visible_widgets:
            self.visible_widgets.append(widget_id)
        elif not enabled and widget_id in self.visible_widgets:
            self.visible_widgets.remove(widget_id)
        self.error = ""
        self.notice = ""

    def move_widget(self, widget_id: str, offset: int) -> None:
        if widget_id not in self.widget_order or offset not in (-1, 1):
            raise ValueError("Não foi possível alterar a ordem do widget.")
        current_index = self.widget_order.index(widget_id)
        target_index = current_index + offset
        if not 0 <= target_index < len(self.widget_order):
            return
        self.widget_order[current_index], self.widget_order[target_index] = (
            self.widget_order[target_index],
            self.widget_order[current_index],
        )
        self.error = ""
        self.notice = ""

    def save(self) -> rx.event.EventSpec | None:
        if not self.account_key:
            self.error = "Não foi possível identificar a conta autenticada."
            return
        try:
            preferences = _validate_preferences(
                {
                    "display_name": self.display_name,
                    "appearance_mode": self.appearance_mode,
                    "dashboard_title": self.dashboard_title,
                    "visible_widgets": self.visible_widgets,
                    "widget_order": self.widget_order,
                }
            )
            store = _decode_store(self.preferences_json)
        except ValueError as exc:
            self.error = str(exc)
            self.notice = ""
            return
        store[self.account_key] = preferences
        self.preferences_json = json.dumps(store, ensure_ascii=False)
        self._set_draft(preferences)
        self.error = ""
        self.notice = "Personalização salva neste navegador."
        return _apply_theme(preferences["appearance_mode"])

    def reset_preferences(self) -> rx.event.EventSpec | None:
        self.account_key = self.account_key.strip()
        if not self.account_key:
            self.error = "Não foi possível identificar a conta autenticada."
            return
        try:
            store = _decode_store(self.preferences_json)
        except ValueError:
            store = {}
        store.pop(self.account_key, None)
        self.preferences_json = json.dumps(store, ensure_ascii=False)
        self._set_draft(_default_preferences())
        self.error = ""
        self.notice = "Personalização restaurada para os padrões."
        return _apply_theme("dark")

    def _set_draft(self, preferences: dict[str, Any]) -> None:
        self.display_name = preferences["display_name"]
        self.appearance_mode = preferences["appearance_mode"]
        self.dashboard_title = preferences["dashboard_title"]
        self.visible_widgets = list(preferences["visible_widgets"])
        self.widget_order = list(preferences["widget_order"])
