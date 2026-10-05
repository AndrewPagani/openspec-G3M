import reflex as rx

from app.components.app_shell import shell
from app.components.states import empty_state, feedback
from app.state.resource_state import ResourceState


def _vehicle_card(row: rx.Var, endpoint: str) -> rx.Component:
    return rx.card(
        rx.cond(
            row["_image_url"] != "",
            rx.image(
                src=row["_image_url"],
                alt=row["_vehicle_name"],
                width="100%",
                height="190px",
                object_fit="cover",
            ),
            rx.box(
                rx.text("Imagem não cadastrada", class_name="muted"),
                width="100%",
                height="190px",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
        ),
        rx.vstack(
            rx.heading(row["_vehicle_name"], size="4"),
            rx.text(row["_vehicle_year_display"]),
            rx.text(row["_vehicle_price_display"]),
            rx.link(
                "Abrir veículo",
                href=rx.Var.create(f"{endpoint.rstrip('/')}/") + row["id"].to_string(),
            ),
            align="start",
            width="100%",
        ),
        width="100%",
    )


def resource_page(
    title: str, endpoint: str, new_href: str | None = None, allowed: rx.Var = True
) -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.input(
                    placeholder="Buscar…",
                    value=ResourceState.query,
                    on_change=ResourceState.set_query,
                ),
                rx.spacer(),
                rx.cond(new_href is not None, rx.link(rx.button("Novo"), href=new_href or "#"), rx.fragment()),
                class_name="toolbar",
            ),
            feedback(ResourceState.error, ResourceState.loading),
            rx.cond(
                ResourceState.endpoint == "/veiculos",
                rx.cond(
                    ResourceState.filtered_records.length() > 0,
                    rx.grid(
                        rx.foreach(
                            ResourceState.filtered_records,
                            lambda row: _vehicle_card(row, endpoint),
                        ),
                        columns="repeat(auto-fit, minmax(260px, 1fr))",
                        spacing="4",
                        width="100%",
                    ),
                    empty_state("A API não retornou veículos para esta consulta."),
                ),
                rx.cond(
                    ResourceState.filtered_records.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    rx.cond(
                                        ResourceState.endpoint == "/clientes",
                                        "Cliente - CPF",
                                        "Registro",
                                    )
                                ),
                                rx.table.column_header_cell("Ações"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                ResourceState.filtered_records,
                                lambda row: rx.table.row(
                                    rx.table.cell(
                                        rx.cond(
                                            ResourceState.endpoint == "/clientes",
                                            row["_display_label"],
                                            row.to_string(),
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.link(
                                            "Abrir",
                                            href=rx.Var.create(f"{endpoint.rstrip('/')}/")
                                            + row["id"].to_string(),
                                        )
                                    ),
                                ),
                            )
                        ),
                    ),
                    empty_state("A API não retornou registros para esta consulta."),
                ),
            ),
            on_mount=ResourceState.load(endpoint, title),
            class_name="page-stack",
        ),
        title,
        allowed,
    )
