import reflex as rx


def feedback(error: rx.Var, loading: rx.Var) -> rx.Component:
    return rx.cond(
        loading,
        rx.callout("Carregando dados…", icon="loader-circle"),
        rx.cond(error != "", rx.callout(error, color_scheme="red", icon="triangle-alert"), rx.fragment()),
    )


def empty_state(label: str = "Nenhum registro encontrado.") -> rx.Component:
    return rx.callout(label, icon="inbox", color_scheme="gray")
