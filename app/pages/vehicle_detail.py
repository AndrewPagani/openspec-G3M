import reflex as rx

from app.components.app_shell import shell
from app.state.vehicle_detail_state import VehicleDetailState


def _field(label: str, key: str, icon: str = "circle") -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=16, stroke_width=1.7),
            rx.text(label, class_name="vehicle-detail-label"),
            align="center",
            spacing="2",
        ),
        rx.text(
            VehicleDetailState.vehicle[key],
            class_name="vehicle-detail-value",
        ),
        align="start",
        class_name="vehicle-detail-field",
    )


def _section(title: str, icon: str, *children: rx.Component) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=19, stroke_width=1.7),
                rx.heading(title, size="4"),
                align="center",
                spacing="2",
                class_name="vehicle-detail-section-heading",
            ),
            rx.grid(
                *children,
                columns="repeat(2, minmax(0, 1fr))",
                class_name="vehicle-detail-fields",
            ),
            align="stretch",
            width="100%",
        ),
        class_name="vehicle-detail-card",
    )


def vehicle_detail_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.hstack(
                            rx.icon("arrow-left", size=16),
                            rx.text("Voltar"),
                            align="center",
                            spacing="2",
                        ),
                        variant="outline",
                    ),
                    href="/veiculos",
                ),
                rx.spacer(),
                rx.cond(
                    VehicleDetailState.vehicle["status"] != "",
                    rx.badge(VehicleDetailState.vehicle["status"], class_name="vehicle-detail-status"),
                    rx.fragment(),
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                VehicleDetailState.loading | (VehicleDetailState.read_id != VehicleDetailState.router.page.params.get("id", "")),
                rx.center(rx.spinner(), min_height="260px"),
                rx.cond(
                    VehicleDetailState.error != "",
                    rx.callout(
                        VehicleDetailState.error,
                        color_scheme="red",
                        role="alert",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.text("DETALHES DO VEÍCULO", class_name="vehicle-detail-kicker"),
                                rx.heading(
                                    rx.hstack(
                                        rx.text(VehicleDetailState.vehicle["marca"]),
                                        rx.text(VehicleDetailState.vehicle["modelo"]),
                                        spacing="2",
                                    ),
                                    size="7",
                                ),
                                rx.text(
                                    "Cadastro completo e especificações técnicas",
                                    class_name="muted",
                                ),
                                align="start",
                            ),
                            rx.cond(
                                VehicleDetailState.vehicle["imagem_url"] != "",
                                rx.image(
                                    src=VehicleDetailState.vehicle["imagem_url"],
                                    alt="Imagem do veículo",
                                    class_name="vehicle-detail-image",
                                ),
                                rx.fragment(),
                            ),
                            justify="between",
                            align="center",
                            width="100%",
                            class_name="vehicle-detail-hero",
                        ),
                        _section(
                            "Identificação completa",
                            "badge",
                            _field("Placa", "placa", "scan-line"),
                            _field("Chassi / VIN", "chassi", "fingerprint"),
                            _field("UF de registro", "uf_registro", "map"),
                            _field("Cidade de registro", "cidade_registro", "map-pin"),
                        ),
                        _section(
                            "Especificações técnicas",
                            "settings-2",
                            _field("Marca", "marca", "factory"),
                            _field("Modelo", "modelo", "car-front"),
                            _field("Ano de fabricação", "ano_fabricacao", "calendar"),
                            _field("Motorização / cilindrada", "motorizacao", "gauge"),
                            _field("Combustível", "combustivel", "fuel"),
                            _field("Câmbio / transmissão", "cambio", "settings"),
                            _field("Quilometragem atual", "quilometragem", "milestone"),
                            _field("Portas", "numero_portas", "door-open"),
                            _field("Lugares", "numero_lugares", "users"),
                        ),
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("sparkles", size=19, stroke_width=1.7),
                                    rx.heading("Opcionais e equipamentos", size="4"),
                                    align="center",
                                    spacing="2",
                                ),
                                rx.cond(
                                    VehicleDetailState.opcionais.length() > 0,
                                    rx.flex(
                                        rx.foreach(
                                            VehicleDetailState.opcionais,
                                            lambda item: rx.badge(item, variant="soft"),
                                        ),
                                        gap="2",
                                        wrap="wrap",
                                    ),
                                    rx.text("Nenhum opcional informado.", class_name="muted"),
                                ),
                                align="start",
                                width="100%",
                            ),
                            class_name="vehicle-detail-card",
                        ),
                        spacing="4",
                        align="stretch",
                        width="100%",
                    ),
                ),
            ),
            spacing="4",
            align="stretch",
            width="100%",

        ),
        "Detalhes do veículo",
    )
