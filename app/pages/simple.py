import reflex as rx

from app.components.app_shell import shell
from app.state.form_state import FormState


def _status_badge() -> rx.Component:
    return rx.cond(
        FormState.selected_status_class == "status-available",
        rx.badge(
            FormState.selected_status_label,
            class_name="vehicle-status status-available",
        ),
        rx.cond(
            FormState.selected_status_class == "status-reserved",
            rx.badge(
                FormState.selected_status_label,
                class_name="vehicle-status status-reserved",
            ),
            rx.cond(
                FormState.selected_status_class == "status-sold",
                rx.badge(
                    FormState.selected_status_label,
                    class_name="vehicle-status status-sold",
                ),
                rx.badge(
                    FormState.selected_status_label,
                    class_name="vehicle-status status-neutral",
                ),
            ),
        ),
    )


def _vehicle_field(label: str, icon: str, input_type: str = "text") -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="vehicle-form-label"),
        rx.hstack(
            rx.input(
                type=input_type,
                placeholder=label,
                aria_label=label,
                value=FormState.values.get(label, ""),
                on_change=lambda value, name=label: FormState.set_field(name, value),
                min="1900" if label == "Ano" else None,
                max="2100" if label == "Ano" else None,
                step="0.01" if label == "Preço" else ("1" if label == "Ano" else "any"),
                required=label in ("Marca", "Modelo", "Cor", "Ano", "Preço"),
                class_name="vehicle-form-input",
            ),
            rx.cond(
                label == "Preço",
                rx.text("R$", class_name="vehicle-form-currency-prefix"),
                rx.fragment(),
            ),
            rx.icon(icon, size=17, stroke_width=1.6, class_name="vehicle-form-field-icon"),
            align="center",
            class_name="vehicle-form-input-wrap",
        ),
        class_name="vehicle-form-field",
    )


def _vehicle_select_field(
    label: str, icon: str, options: rx.Var
) -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="vehicle-form-label"),
        rx.hstack(
            rx.select.root(
                rx.select.trigger(placeholder=f"Selecione {label.lower()}"),
                rx.select.content(
                    rx.foreach(
                        options,
                        lambda option: rx.select.item(option, value=option),
                    )
                ),
                value=FormState.values.get(label, ""),
                on_change=lambda value, name=label: FormState.set_field(name, value),
                class_name="vehicle-form-select",
            ),
            rx.icon(icon, size=17, stroke_width=1.6, class_name="vehicle-form-field-icon"),
            align="center",
            class_name="vehicle-form-input-wrap",
        ),
        class_name="vehicle-form-field",
    )


def _vehicle_status_select() -> rx.Component:
    return rx.vstack(
        rx.text("Status", class_name="vehicle-form-label"),
        rx.hstack(
            rx.select.root(
                rx.select.trigger(placeholder="Selecione o status"),
                rx.select.content(
                    rx.foreach(
                        FormState.vehicle_statuses,
                        lambda status: rx.select.item(
                            status["Descricao"],
                            value=status["id"],
                        ),
                    )
                ),
                value=FormState.values.get("Status (ID)", ""),
                on_change=lambda value: FormState.set_field("Status (ID)", value),
                disabled=FormState.loading_statuses
                | (FormState.vehicle_statuses.length() == 0),
                class_name="vehicle-form-select",
            ),
            rx.cond(
                FormState.selected_status_label != "",
                _status_badge(),
                rx.fragment(),
            ),
            align="center",
            class_name="vehicle-status-control",
        ),
        rx.cond(
            FormState.loading_statuses,
            rx.text("Carregando status do Xano...", class_name="vehicle-form-hint"),
            rx.fragment(),
        ),
        rx.cond(
            FormState.status_error != "",
            rx.callout(
                FormState.status_error,
                color_scheme="red",
                role="alert",
                class_name="vehicle-form-feedback",
            ),
            rx.fragment(),
        ),
        class_name="vehicle-form-field",
    )


def _vehicle_media_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.vstack(
                rx.icon("camera", size=25, stroke_width=1.5),
                rx.text("Imagem de capa", class_name="vehicle-panel-title"),
                rx.text(
                    "Insira a URL da imagem hospedada.",
                    class_name="vehicle-form-hint",
                ),
                rx.hstack(
                    rx.icon("link-2", size=16, stroke_width=1.7),
                    rx.input(
                        placeholder="https://...",
                        aria_label="URL da imagem de capa",
                        type="url",
                        value=FormState.values.get("URL da imagem", ""),
                        on_change=lambda value: FormState.set_field(
                            "URL da imagem", value
                        ),
                        class_name="vehicle-form-input",
                    ),
                    align="center",
                    class_name="vehicle-form-input-wrap",
                ),
                align="start",
                class_name="vehicle-image-dropzone",
            ),
            rx.box(
                rx.cond(
                    FormState.image_preview_url != "",
                    rx.image(
                        src=FormState.image_preview_url,
                        alt="Pré-visualização da imagem de capa do veículo",
                        class_name="vehicle-image-preview",
                    ),
                    rx.vstack(
                        rx.icon("image", size=27, stroke_width=1.5),
                        rx.text("Pré-visualização", class_name="vehicle-form-hint"),
                        align="center",
                        justify="center",
                        class_name="vehicle-image-preview-empty",
                    ),
                ),
                class_name="vehicle-image-preview-frame",
            ),
            _vehicle_status_select(),
            class_name="vehicle-media-layout",
        ),
        class_name="vehicle-form-panel vehicle-media-panel",
    )


def _vehicle_information_panel() -> rx.Component:
    return rx.grid(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("car-front", size=19, stroke_width=1.6),
                    rx.heading("Informações básicas", size="4"),
                    align="center",
                    spacing="2",
                    class_name="vehicle-form-panel-heading",
                ),
                rx.grid(
                    _vehicle_field("Marca", "factory"),
                    _vehicle_field("Modelo", "car-front"),
                    _vehicle_field("Cor", "palette"),
                    _vehicle_field("Ano", "calendar-days", "number"),
                    class_name="vehicle-form-fields-grid",
                ),
                align="stretch",
                class_name="vehicle-form-panel-content",
            ),
            class_name="vehicle-form-panel",
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("settings-2", size=19, stroke_width=1.6),
                    rx.heading("Especificações técnicas", size="4"),
                    align="center",
                    spacing="2",
                    class_name="vehicle-form-panel-heading",
                ),
                rx.grid(
                    _vehicle_field("Placa", "scan-line"),
                    _vehicle_field("Chassi", "barcode"),
                    _vehicle_field("Quilometragem", "gauge", "number"),
                    _vehicle_field("Preço", "banknote", "number"),
                    class_name="vehicle-form-fields-grid",
                ),
                align="stretch",
                class_name="vehicle-form-panel-content",
            ),
            class_name="vehicle-form-panel",
        ),
        columns="repeat(2, minmax(0, 1fr))",
        spacing="4",
        width="100%",
        class_name="vehicle-form-panels-grid",
    )


def _vehicle_details_panel() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("file-text", size=19, stroke_width=1.6),
                rx.heading("Identificação e especificações", size="4"),
                align="center",
                spacing="2",
                class_name="vehicle-form-panel-heading",
            ),
            rx.text(
                "Campos complementares do documento e da ficha técnica. Todos são opcionais.",
                class_name="vehicle-form-hint",
            ),
            rx.grid(
                _vehicle_select_field("UF de registro", "map", FormState.uf_options),
                _vehicle_field("Cidade de registro", "map-pin"),
                _vehicle_field("Motorização / cilindrada", "gauge"),
                _vehicle_select_field("Combustível", "fuel", FormState.fuel_options),
                _vehicle_select_field(
                    "Câmbio / transmissão", "settings", FormState.transmission_options
                ),
                _vehicle_select_field("Número de portas", "door-open", FormState.door_options),
                _vehicle_select_field("Número de lugares", "users", FormState.seat_options),
                class_name="vehicle-form-fields-grid",
            ),
            rx.vstack(
                rx.text("Opcionais e equipamentos", class_name="vehicle-form-label"),
                rx.text_area(
                    placeholder="Ex.: Teto Solar, Couro, Ar Digital, Sensor de Ré",
                    aria_label="Opcionais e equipamentos",
                    value=FormState.values.get("Opcionais e equipamentos", ""),
                    on_change=lambda value: FormState.set_field(
                        "Opcionais e equipamentos", value
                    ),
                    class_name="vehicle-form-input",
                    width="100%",
                ),
                rx.text(
                    "Separe os itens por vírgula.",
                    class_name="vehicle-form-hint",
                ),
                align="start",
                width="100%",
            ),
            align="stretch",
            class_name="vehicle-form-panel-content",
        ),
        class_name="vehicle-form-panel",
    )


def _vehicle_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            _vehicle_media_panel(),
            _vehicle_information_panel(),
            _vehicle_details_panel(),
            rx.cond(
                FormState.error != "",
                rx.callout(
                    FormState.error,
                    color_scheme="red",
                    role="alert",
                    class_name="vehicle-form-feedback",
                ),
                rx.fragment(),
            ),
            rx.cond(
                FormState.success != "",
                rx.callout(
                    FormState.success,
                    color_scheme="green",
                    role="status",
                    class_name="vehicle-form-feedback",
                ),
                rx.fragment(),
            ),
            rx.vstack(
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("save", size=17, stroke_width=1.8),
                            rx.text(
                                rx.cond(
                                    FormState.saving,
                                    "Salvando...",
                                    "Salvar Veículo",
                                )
                            ),
                            align="center",
                            spacing="2",
                        ),
                        type="submit",
                        disabled=FormState.saving
                        | FormState.loading_statuses
                        | (FormState.vehicle_statuses.length() == 0),
                        class_name="vehicle-save-button",
                    ),
                    rx.link(
                        rx.button(
                            "Cancelar",
                            type="button",
                            class_name="vehicle-cancel-button",
                        ),
                        href="/veiculos",
                    ),
                    justify="end",
                    class_name="vehicle-form-actions",
                ),
                rx.text(
                    "Os campos serão validados e persistidos por Xano.",
                    class_name="vehicle-form-footer-note",
                ),
                align="end",
                width="100%",
                class_name="vehicle-form-footer",
            ),
            align="stretch",
            width="100%",
            class_name="vehicle-form-layout",
        ),
        on_submit=FormState.save("veiculos"),
        reset_on_submit=False,
        class_name="vehicle-create-form",
    )


def _part_field(label: str, icon: str, input_type: str = "text") -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="vehicle-form-label"),
        rx.hstack(
            rx.input(
                type=input_type,
                placeholder=label,
                aria_label=label,
                value=FormState.values.get(label, ""),
                on_change=lambda value, name=label: FormState.set_field(name, value),
                min="0" if label == "Quantidade" else None,
                step="0.01" if label == "Preço" else "1",
                required=label in ("Nome", "Preço"),
                class_name="vehicle-form-input",
            ),
            rx.cond(
                label == "Preço",
                rx.text("R$", class_name="vehicle-form-currency-prefix"),
                rx.fragment(),
            ),
            rx.icon(icon, size=17, stroke_width=1.6, class_name="vehicle-form-field-icon"),
            align="center",
            class_name="vehicle-form-input-wrap",
        ),
        rx.cond(
            label == "Quantidade",
            rx.text("Opcional; se vazio, a API grava 0.", class_name="vehicle-form-hint"),
            rx.fragment(),
        ),
        class_name="vehicle-form-field",
    )


def _part_area_select() -> rx.Component:
    return rx.vstack(
        rx.text("Área do veículo", class_name="vehicle-form-label"),
        rx.select.root(
            rx.select.trigger(placeholder="Selecione a área (opcional)"),
            rx.select.content(
                rx.foreach(
                    FormState.part_areas,
                    lambda area: rx.select.item(area["Secao"], value=area["id"]),
                )
            ),
            value=FormState.values.get("Área (ID)", ""),
            on_change=lambda value: FormState.set_field("Área (ID)", value),
            disabled=FormState.loading_part_areas,
            class_name="vehicle-form-select",
        ),
        rx.cond(
            FormState.loading_part_areas,
            rx.text("Carregando áreas do Xano...", class_name="vehicle-form-hint"),
            rx.fragment(),
        ),
        rx.cond(
            FormState.part_area_error != "",
            rx.callout(
                FormState.part_area_error,
                color_scheme="red",
                role="alert",
                class_name="vehicle-form-feedback",
            ),
            rx.fragment(),
        ),
        class_name="vehicle-form-field",
    )


def _part_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("package", size=19, stroke_width=1.6),
                        rx.heading("Informações da peça", size="4"),
                        align="center",
                        spacing="2",
                        class_name="vehicle-form-panel-heading",
                    ),
                    rx.grid(
                        _part_field("Nome", "tag"),
                        _part_field("Preço", "banknote", "number"),
                        _part_field("Quantidade", "boxes", "number"),
                        _part_area_select(),
                        columns="repeat(2, minmax(0, 1fr))",
                        class_name="vehicle-form-fields-grid",
                    ),
                    align="stretch",
                    class_name="vehicle-form-panel-content",
                ),
                class_name="vehicle-form-panel",
            ),
            rx.cond(
                FormState.error != "",
                rx.callout(
                    FormState.error,
                    color_scheme="red",
                    role="alert",
                    class_name="vehicle-form-feedback",
                ),
                rx.fragment(),
            ),
            rx.cond(
                FormState.success != "",
                rx.callout(
                    FormState.success,
                    color_scheme="green",
                    role="status",
                    class_name="vehicle-form-feedback",
                ),
                rx.fragment(),
            ),
            rx.vstack(
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("save", size=17, stroke_width=1.8),
                            rx.text(
                                rx.cond(FormState.saving, "Salvando...", "Salvar Peça")
                            ),
                            align="center",
                            spacing="2",
                        ),
                        type="submit",
                        disabled=FormState.saving | FormState.loading_part_areas,
                        class_name="vehicle-save-button",
                    ),
                    rx.link(
                        rx.button(
                            "Cancelar",
                            type="button",
                            class_name="vehicle-cancel-button",
                        ),
                        href="/pecas",
                    ),
                    justify="end",
                    class_name="vehicle-form-actions",
                ),
                rx.text(
                    "Nome e preço são obrigatórios. Quantidade e área são opcionais.",
                    class_name="vehicle-form-footer-note",
                ),
                align="end",
                width="100%",
                class_name="vehicle-form-footer",
            ),
            align="stretch",
            width="100%",
            class_name="vehicle-form-layout",
        ),
        on_submit=FormState.save("pecas"),
        reset_on_submit=False,
        class_name="vehicle-create-form",
    )


def form_page(
    title: str, endpoint: str, fields: tuple[str, ...], allowed: rx.Var = True
) -> rx.Component:
    if endpoint == "veiculos":
        return shell(
            rx.vstack(
                _vehicle_form(),

                class_name="vehicle-create-page",
            ),
            title,
            allowed,
        )
    if endpoint == "pecas":
        return shell(
            rx.vstack(
                _part_form(),

                class_name="vehicle-create-page",
            ),
            title,
            allowed,
        )
    return shell(
        rx.vstack(
            rx.text("Os campos serão validados e persistidos pelo Xano.", class_name="muted"),
            *[
                rx.input(
                    placeholder=field,
                    aria_label=field,
                    value=FormState.values.get(field, ""),
                    on_change=lambda value, name=field: FormState.set_field(name, value),
                )
                for field in fields
            ],
            rx.cond(FormState.error != "", rx.callout(FormState.error, color_scheme="red")),
            rx.cond(FormState.success != "", rx.callout(FormState.success, color_scheme="green")),
            rx.hstack(
                rx.button("Salvar", on_click=FormState.save(endpoint), loading=FormState.saving),
                rx.link(rx.button("Cancelar", variant="outline"), href=f"/{endpoint}"),
            ),
            class_name="form-card generic-form-card",
        ), title, allowed)


def forbidden() -> rx.Component:
    return shell(rx.callout("Acesso negado para o seu perfil.", color_scheme="red"), "Acesso negado")


def detail_page(title: str, endpoint: str, allowed: rx.Var = True) -> rx.Component:
    return shell(
        rx.vstack(
            rx.callout(
                "O detalhe será carregado pela API do Xano quando um identificador for informado.",
                icon="info",
            ),
            rx.link("Voltar para a lista", href=f"/{endpoint}"),
            class_name="page-stack",
        ),
        title,
        allowed,
    )
