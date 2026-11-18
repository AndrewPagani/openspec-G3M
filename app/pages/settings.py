from __future__ import annotations

import reflex as rx

from app.components.app_shell import shell
from app.components.states import feedback
from app.state.auth_state import AuthState
from app.state.settings_state import WIDGETS, SettingsState


def _widget_label(widget_id: rx.Var) -> rx.Component:
    return rx.match(
        widget_id,
        ("metrics", "Indicadores principais"),
        ("sales_charts", "Gráficos de vendas"),
        ("inventory", "Estoque"),
        ("sales_breakdown", "Detalhamento de vendas"),
        "Widget",
    )


def _widget_row(widget_id: str, label: str) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(label, class_name="settings-option-title"),
            rx.text(
                "Exibir esta seção no Dashboard",
                class_name="settings-option-description",
            ),
            align="start",
            spacing="1",
        ),
        rx.spacer(),
        rx.switch(
            checked=SettingsState.visible_widgets.contains(widget_id),
            on_change=lambda enabled: SettingsState.set_widget_visibility(
                widget_id, enabled
            ),
            aria_label=f"Exibir {label}",
        ),
        align="center",
        width="100%",
        class_name="settings-option-row",
    )


def _order_row(widget_id: rx.Var, index: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.icon("grip", size=16, stroke_width=1.8),
            class_name="settings-order-handle",
            aria_hidden=True,
        ),
        _widget_label(widget_id),
        rx.spacer(),
        rx.button(
            rx.icon("chevron-up", size=16),
            variant="soft",
            aria_label="Mover widget para cima",
            on_click=SettingsState.move_widget(widget_id, -1),
            disabled=index == 0,
            class_name="settings-order-button",
        ),
        rx.button(
            rx.icon("chevron-down", size=16),
            variant="soft",
            aria_label="Mover widget para baixo",
            on_click=SettingsState.move_widget(widget_id, 1),
            disabled=index == len(WIDGETS) - 1,
            class_name="settings-order-button",
        ),
        align="center",
        width="100%",
        class_name="settings-order-row",
    )


def _theme_option(
    mode: str, label: str, description: str, icon: str
) -> rx.Component:
    return rx.button(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=17),
                rx.text(label, class_name="settings-theme-title"),
                rx.spacer(),
                rx.cond(
                    SettingsState.appearance_mode == mode,
                    rx.text("Selecionado", class_name="settings-theme-selected-label"),
                    rx.fragment(),
                ),
                align="center",
                width="100%",
            ),
            rx.box(
                rx.hstack(
                    rx.box(class_name="settings-theme-preview-sidebar"),
                    rx.vstack(
                        rx.box(class_name="settings-theme-preview-line"),
                        rx.box(class_name="settings-theme-preview-line"),
                        rx.box(class_name="settings-theme-preview-block"),
                        align="start",
                        width="100%",
                        class_name="settings-theme-preview-content",
                    ),
                    width="100%",
                    height="100%",
                    class_name=f"settings-theme-preview-layout settings-theme-preview-{mode}",
                ),
                class_name="settings-theme-preview",
                aria_hidden=True,
            ),
            rx.text(description, class_name="settings-option-description"),
            align="start",
            spacing="3",
            width="100%",
        ),
        variant="outline",
        aria_pressed=SettingsState.appearance_mode == mode,
        on_click=SettingsState.set_appearance_mode(mode),
        class_name=rx.cond(
            SettingsState.appearance_mode == mode,
            "settings-theme-option settings-theme-selected",
            "settings-theme-option",
        ),
        width="100%",
        height="auto",
    )


def _personalization_form() -> rx.Component:
    return rx.vstack(
        rx.card(
            rx.vstack(
                rx.heading("Tema e aparência", size="4", as_="h2"),
                rx.text(
                    "Escolha como as telas internas são exibidas. A alteração é aplicada imediatamente e salva ao confirmar.",
                    class_name="muted",
                ),
                rx.grid(
                    _theme_option(
                        "dark",
                        "Escuro",
                        "O tema escuro fica sempre ativo.",
                        "moon",
                    ),
                    _theme_option(
                        "light",
                        "Claro",
                        "Uma interface clara e suave.",
                        "sun",
                    ),
                    _theme_option(
                        "system",
                        "Automático",
                        "Acompanha o tema do dispositivo.",
                        "monitor",
                    ),
                    columns=rx.breakpoints(
                        initial="1fr", md="repeat(3, minmax(0, 1fr))"
                    ),
                    spacing="3",
                    width="100%",
                ),
                align="start",
                width="100%",
            ),
            class_name="settings-card",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Identidade do painel", size="4", as_="h2"),
                rx.text(
                    "Personalize como seu painel e seu perfil aparecem neste navegador.",
                    class_name="muted",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Nome de exibição", class_name="settings-field-label"),
                        rx.input(
                            value=SettingsState.display_name,
                            placeholder=AuthState.user_name,
                            max_length=40,
                            aria_label="Nome de exibição",
                            on_change=SettingsState.set_display_name,
                        ),
                        rx.text(
                            "Usado apenas na interface; não altera seu cadastro.",
                            class_name="settings-field-help",
                        ),
                        align="start",
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Título do Dashboard", class_name="settings-field-label"),
                        rx.input(
                            value=SettingsState.dashboard_title,
                            max_length=40,
                            aria_label="Título do Dashboard",
                            on_change=SettingsState.set_dashboard_title,
                        ),
                        rx.text(
                            "O título padrão é Dashboard.",
                            class_name="settings-field-help",
                        ),
                        align="start",
                        spacing="2",
                        width="100%",
                    ),
                    columns=rx.breakpoints(initial="1fr", md="repeat(2, minmax(0, 1fr))"),
                    spacing="4",
                    width="100%",
                ),
                align="start",
                width="100%",
            ),
            class_name="settings-card",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Widgets do Dashboard", size="4", as_="h2"),
                rx.text(
                    "Escolha as seções existentes que deseja exibir e organize sua ordem.",
                    class_name="muted",
                ),
                rx.grid(
                    rx.vstack(
                        rx.foreach(
                            WIDGETS,
                            lambda option: _widget_row(option[0], option[1]),
                        ),
                        align="start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Ordem das seções", class_name="settings-field-label"),
                        rx.foreach(
                            SettingsState.widget_order,
                            lambda widget_id, index: _order_row(widget_id, index),
                        ),
                        align="start",
                        width="100%",
                    ),
                    columns=rx.breakpoints(initial="1fr", md="repeat(2, minmax(0, 1fr))"),
                    spacing="5",
                    width="100%",
                ),
                align="start",
                width="100%",
            ),
            class_name="settings-card",
            width="100%",
        ),
        feedback(SettingsState.error, False),
        rx.cond(
            SettingsState.notice != "",
            rx.callout(
                SettingsState.notice,
                icon="circle-check",
                color_scheme="green",
                role="status",
            ),
            rx.fragment(),
        ),
        rx.hstack(
            rx.button(
                "Restaurar padrões",
                variant="outline",
                on_click=SettingsState.reset_preferences,
            ),
            rx.spacer(),
            rx.button(
                "Salvar personalização",
                on_click=SettingsState.save,
                class_name="settings-save-button",
            ),
            align="center",
            width="100%",
            class_name="settings-actions",
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def settings_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Personalização do painel", size="6"),
                    rx.text(
                        "Ajuste sua experiência sem alterar os dados da conta ou da empresa.",
                        class_name="muted",
                    ),
                    align="start",
                    spacing="1",
                ),
                align="start",
                width="100%",
            ),
            _personalization_form(),
            align="start",
            spacing="4",
            width="100%",
            class_name="page-stack settings-page",
        ),
        "Configurações",
        allowed=AuthState.is_manager,
    )
