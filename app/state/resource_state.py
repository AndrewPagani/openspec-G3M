from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from unicodedata import combining
from unicodedata import normalize as normalize_unicode
from zoneinfo import ZoneInfo

import reflex as rx

from app.services.catalogs import catalogs
from app.services.sales_query import sales_query_params
from app.services.vehicle_status import vehicle_status_class
from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState
from app.state.read_lifecycle import read_event

_LOCAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def _first_value(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _format_vehicle_price(value: str) -> str:
    if not value:
        return "Valor não informado"
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return value
    formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def _format_vehicle_mileage(value: str) -> str:
    if not value:
        return "Não informado"
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return value
    formatted = f"{amount:,.0f}".replace(",", ".")
    return formatted


def _format_part_quantity(value: str) -> str:
    if not value:
        return "0"
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation:
        return value
    return f"{amount:,.0f}".replace(",", ".")


def _parse_part_quantity(value: str) -> int:
    if not value:
        return 0
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation as exc:
        raise XanoError("A API retornou uma quantidade de peças inválida.") from exc
    if not amount.is_finite() or amount < 0 or amount != amount.to_integral_value():
        raise XanoError("A API retornou uma quantidade de peças inválida.")
    return int(amount)


def _format_cpf(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if len(digits) != 11:
        return value
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def _format_phone(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    country_prefix = ""
    if digits.startswith("55") and len(digits) in (12, 13):
        country_prefix, digits = "+55 ", digits[2:]
    if len(digits) == 11:
        return f"{country_prefix}({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"{country_prefix}({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return value


def _parse_api_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (int, float)) or (
            isinstance(value, str) and value.strip().isdigit()
        ):
            timestamp = float(value)
            if abs(timestamp) > 100_000_000_000:
                timestamp /= 1000
            parsed = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        elif isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            raise ValueError
    except (OverflowError, OSError, TypeError, ValueError) as exc:
        raise XanoError("A API retornou uma data de cliente ou venda inválida.") from exc
    return parsed.astimezone(_LOCAL_TIMEZONE)


def _client_activity_and_metrics(
    clients: list[dict[str, Any]],
    sales: list[dict[str, Any]],
    now: datetime | None = None,
) -> tuple[dict[str, str], int, int]:
    latest_sales: dict[str, datetime] = {}
    pending_count = 0

    for sale in sales:
        related_client = sale.get("cliente")
        related_client_id = (
            related_client.get("id") if isinstance(related_client, dict) else None
        )
        client_id = _first_value(sale, "cliente_id", "client_id") or (
            str(related_client_id) if related_client_id is not None else ""
        )

        status_value = sale.get("status")
        if status_value is None:
            status_value = sale.get("status_venda")
        if isinstance(status_value, dict):
            status_value = _first_value(
                status_value, "Descricao_venda", "descricao", "status"
            )
        status = _first_value(sale, "status_descricao", "Descricao_venda") or (
            str(status_value).strip() if status_value is not None else ""
        )
        normalized_status = "".join(
            char
            for char in normalize_unicode("NFKD", status)
            if not combining(char)
        ).casefold()
        if normalized_status in {"reservado", "pendente"}:
            pending_count += 1

        sale_date = _parse_api_datetime(sale.get("data_venda"))
        if client_id and sale_date and (
            client_id not in latest_sales or sale_date > latest_sales[client_id]
        ):
            latest_sales[client_id] = sale_date

    activity = {
        client_id: sale_date.strftime("%d/%m/%Y, %H:%M")
        for client_id, sale_date in latest_sales.items()
    }
    current_time = (now or datetime.now(_LOCAL_TIMEZONE)).astimezone(_LOCAL_TIMEZONE)
    new_this_month = 0
    for customer in clients:
        created_at = _parse_api_datetime(
            customer.get("created_at") or customer.get("Created_at")
        )
        if created_at and (created_at.year, created_at.month) == (
            current_time.year,
            current_time.month,
        ):
            new_this_month += 1
    return activity, new_this_month, pending_count


def _sort_client_records(
    records: list[dict[str, Any]], sort_order: str
) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda row: (
            _parse_api_datetime(row.get("created_at") or row.get("Created_at"))
            or datetime.min.replace(tzinfo=_LOCAL_TIMEZONE)
        ),
        reverse=sort_order == "newest_first",
    )


def _normalize_record(record: dict[str, Any], endpoint: str) -> dict[str, Any]:
    normalized = dict(record)
    if endpoint == "/clientes":
        name = _first_value(record, "CNome", "Nome", "nome", "name")
        cpf = _first_value(record, "CPF", "cpf")
        email = _first_value(record, "Email", "email", "E-mail")
        normalized["_display_label"] = f"{name} - {cpf}" if cpf else name
        normalized["_client_name"] = name or "Cliente sem nome"
        normalized["_client_initials"] = "".join(
            part[0] for part in normalized["_client_name"].split()[:2]
        ).upper()
        normalized["_client_cpf"] = _format_cpf(cpf) or "Não informado"
        phone = _first_value(record, "Telefone", "telefone")
        normalized["_client_phone"] = (
            _format_phone(phone) if phone else "Telefone não informado"
        )
        normalized["_client_email"] = email or "Não informado"
        normalized["_client_last_activity"] = _first_value(
            record, "_client_last_activity"
        ) or "Sem compras"
    elif endpoint == "/veiculos":
        make = _first_value(record, "Marca", "marca")
        model = _first_value(record, "Modelo", "modelo")
        image_url = _first_value(
            record,
            "imagem_url",
            "image_url",
            "Imagem",
            "imagem",
            "image",
        )
        price = _first_value(record, "Preco", "preco", "valor", "price")
        normalized["_vehicle_name"] = " ".join(part for part in (make, model) if part)
        year = _first_value(record, "Ano", "ano", "year")
        normalized["_vehicle_year"] = year
        normalized["_vehicle_year_display"] = f"Ano: {year or 'Não informado'}"
        normalized["_vehicle_price"] = _format_vehicle_price(price)
        normalized["_vehicle_price_display"] = f"Valor: {normalized['_vehicle_price']}"
        normalized["_image_url"] = image_url
        mileage = _first_value(record, "Quilometragem", "quilometragem", "mileage")
        fuel = _first_value(
            record,
            "Combustivel",
            "Combustível",
            "combustivel",
            "combustível",
            "fuel",
        )
        normalized["_vehicle_mileage"] = _format_vehicle_mileage(mileage)
        normalized["_vehicle_fuel"] = fuel or "Não informado"
        status = _first_value(
            record, "status_descricao", "Status", "status"
        )
        normalized["_vehicle_status"] = status
        normalized["_vehicle_status_class"] = vehicle_status_class(status)
    elif endpoint == "/pecas":
        name = _first_value(record, "PCNome", "nome", "Nome", "name")
        price = _first_value(record, "PCvalor", "preco", "Preco", "valor", "price")
        quantity = _first_value(
            record,
            "qtd_disp",
            "quantidade_disponivel",
            "quantidade",
            "estoque",
        )
        area = _first_value(
            record,
            "area_secao",
            "area_nome",
            "Secao",
            "area",
        )
        image_url = _first_value(
            record,
            "imagem_url",
            "image_url",
            "Imagem",
            "imagem",
            "image",
        )
        quantity_display = _format_part_quantity(quantity)
        quantity_number = _parse_part_quantity(quantity)
        normalized["_part_name"] = name or "Peça sem nome"
        normalized["_part_price"] = _format_vehicle_price(price)
        normalized["_part_area"] = area or "Área não informada"
        normalized["_part_quantity"] = quantity_display
        normalized["_part_quantity_number"] = quantity_number
        normalized["_part_image_url"] = image_url
        normalized["_part_stock_class"] = (
            "stock-out"
            if quantity_number == 0
            else "stock-low"
            if quantity_number <= 5
            else "stock-available"
        )
    return normalized


def _records_from_response(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, list):
        records = result
    elif isinstance(result, dict):
        records = result.get("items", result.get("data", []))
    else:
        raise XanoError("A API retornou uma resposta inválida para a listagem.")
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise XanoError("A API retornou registros em formato inválido para a listagem.")
    return records


def _pagination_total_pages(pagination: Any, title: str) -> int:
    if not isinstance(pagination, dict):
        raise XanoError(
            f"A API retornou paginação inválida para a listagem de {title.lower()}."
        )

    raw_total_pages = pagination.get("total_pages", 1)
    if isinstance(raw_total_pages, bool):
        invalid = True
    elif isinstance(raw_total_pages, int):
        total_pages = raw_total_pages
        invalid = False
    elif isinstance(raw_total_pages, float):
        total_pages = int(raw_total_pages)
        invalid = not raw_total_pages.is_integer()
    elif isinstance(raw_total_pages, str):
        normalized = raw_total_pages.strip()
        try:
            total_pages = int(normalized)
            invalid = not normalized or str(total_pages) != normalized
        except ValueError:
            total_pages = 0
            invalid = True
    else:
        total_pages = 0
        invalid = True

    if invalid or total_pages < 1:
        raise XanoError(
            f"A API retornou paginação inválida para a listagem de {title.lower()}."
        )
    return total_pages


async def _load_client_sales_activity(
    records: list[dict], token: str
) -> tuple[dict[str, str], int, int]:
    sales_result = await client.async_request(
        "GET",
        "/vendas",
        token=token,
        params=sales_query_params(),
    )
    sales = _records_from_response(sales_result)
    sales_pagination = (
        sales_result.get("pagination", {})
        if isinstance(sales_result, dict)
        else {}
    )
    sales_total_pages = (
        1
        if not sales
        and isinstance(sales_pagination, dict)
        and sales_pagination.get("total_pages") in (0, "0")
        else _pagination_total_pages(sales_pagination, "Vendas")
    )
    for page in range(2, sales_total_pages + 1):
        page_result = await client.async_request(
            "GET",
            "/vendas",
            token=token,
            params=sales_query_params(page=page),
        )
        sales.extend(_records_from_response(page_result))
    return _client_activity_and_metrics(records, sales)


class ResourceState(rx.State, mixin=True):
    """Mixin copied into each independent operational resource namespace."""

    read_generation: int = 0
    dialog_generation: int = 0
    part_detail_generation: int = 0
    complete: bool = False
    loaded_pages: int = 0
    total_pages: int = 0
    activity_pending: bool = False
    records: list[dict] = []
    query: str = ""
    loading: bool = False
    error: str = ""
    endpoint: str = ""
    title: str = ""
    clients_new_this_month: int = 0
    pending_purchases: int = 0
    client_sales_available: bool = False
    client_sales_warning: str = ""
    client_page: int = 1
    client_sort_order: str = "newest_first"
    client_dialog_open: bool = False
    client_dialog_mode: str = ""
    client_detail_loading: bool = False
    client_delete_loading: bool = False
    selected_client: dict[str, str] = {}
    client_form_name: str = ""
    client_form_cpf: str = ""
    client_form_phone: str = ""
    client_form_email: str = ""
    client_action_message: str = ""
    part_dialog_open: bool = False
    part_dialog_loading: bool = False
    part_dialog_saving: bool = False
    part_dialog_error: str = ""
    selected_part_id: str = ""
    part_form_name: str = ""
    part_form_price: str = ""
    part_form_area_id: str = ""
    part_edit_areas: list[dict[str, str]] = []

    @read_event(
        outputs=("records", "endpoint", "title", "loading", "error", "complete", "loaded_pages", "total_pages",
                 "clients_new_this_month", "pending_purchases", "client_sales_available", "client_sales_warning", "activity_pending"),
        clear=("records", "error", "complete", "loaded_pages", "total_pages"),
    )
    async def load(self, endpoint: str, title: str):
        self.endpoint, self.title = endpoint, title
        self.loading, self.error, self.complete = True, "", False
        self.loaded_pages, self.total_pages = 0, 0
        self.client_sales_available, self.activity_pending = False, endpoint == "/clientes"
        self.client_sales_warning = ""
        self.clients_new_this_month, self.pending_purchases = 0, 0
        self.records = []
        yield
        records = []
        try:
            auth_state = await self.get_state(AuthState)
            page, total = 1, 1
            while page <= total:
                params = {"page": page, "per_page": 100} if endpoint != "/usuarios" else None
                result = await client.async_request("GET", endpoint, token=auth_state.token, params=params)
                rows = _records_from_response(result)
                if page == 1:
                    pagination = result.get("pagination", {}) if isinstance(result, dict) else {}
                    total = (1 if not rows and pagination.get("total_pages") in (0, "0")
                             else _pagination_total_pages(pagination, title))
                # Normalize the entire new page before publishing it.
                normalized = [_normalize_record(row, endpoint) for row in rows]
                if endpoint == "/clientes":
                    for row in normalized:
                        row["_client_last_activity"] = "Aguardando lista completa"
                if endpoint == "/clientes":
                    _, new_this_month, _ = _client_activity_and_metrics([*records, *rows], [])
                records.extend(rows)
                self.records = [*self.records, *normalized]
                self.loaded_pages, self.total_pages = page, total
                self.loading = False
                self.complete = page == total
                if endpoint == "/clientes":
                    self.clients_new_this_month = new_this_month
                    if self.complete:
                        for row in self.records:
                            row["_client_last_activity"] = "Carregando atividade…"
                yield
                page += 1
            if endpoint == "/clientes":
                try:
                    activity, _, pending = await _load_client_sales_activity(records, auth_state.token)
                    self.pending_purchases = pending
                    self.client_sales_available = True
                    for row in self.records:
                        row["_client_last_activity"] = activity.get(str(row.get("id", "")), "Sem compras")
                except XanoError:
                    self.client_sales_warning = (
                        "Clientes carregados. Não foi possível consultar as vendas. Atividade e compras pendentes indisponíveis. Atualize para tentar novamente."
                    )
                    for row in self.records:
                        row["_client_last_activity"] = "Indisponível"
        except XanoError as exc:
            self.error = str(exc)
        finally:
            self.loading, self.activity_pending = False, False

    def set_query(self, value: str) -> None:
        self.query = value
        if self.endpoint == "/clientes":
            self.client_page = 1

    def set_client_sort_order(self, value: str) -> None:
        if value in ("oldest_first", "newest_first"):
            self.client_sort_order = value
            self.client_page = 1

    def _find_client(self, client_id: str) -> dict[str, Any] | None:
        return next(
            (row for row in self.records if str(row.get("id", "")) == client_id),
            None,
        )

    @read_event(outputs=("selected_client", "client_dialog_mode", "client_action_message", "client_dialog_open", "client_detail_loading"),
                loading="client_detail_loading", generation_field="dialog_generation")
    async def open_client_details(self, client_id: str):
        row = self._find_client(client_id)
        if row is None:
            self.client_action_message = "Não foi possível localizar este cliente."
            return
        self.selected_client = {
            "id": client_id,
            "name": row.get("_client_name", "Cliente sem nome"),
            "cpf": row.get("_client_cpf", "Não informado"),
            "phone": row.get("_client_phone", "Telefone não informado"),
            "email": row.get("_client_email", "Não informado"),
            "last_activity": row.get("_client_last_activity", "Sem compras"),
        }
        self.client_dialog_mode = "details"
        self.client_action_message = ""
        self.client_dialog_open = True
        self.client_detail_loading = True
        yield
        try:
            auth_state = await self.get_state(AuthState)
            result = await client.async_request(
                "GET",
                f"/clientes/{client_id}",
                token=auth_state.token,
            )
            if not isinstance(result, dict) or result.get("id") is None:
                raise XanoError("A API retornou os dados do cliente em formato inválido.")
            normalized = _normalize_record(result, "/clientes")
            self.selected_client.update(
                {
                    "id": str(result["id"]),
                    "name": normalized.get("_client_name", "Cliente sem nome"),
                    "cpf": normalized.get("_client_cpf", "Não informado"),
                    "phone": normalized.get(
                        "_client_phone", "Telefone não informado"
                    ),
                    "email": normalized.get("_client_email", "Não informado"),
                }
            )
        except XanoError as exc:
            self.client_action_message = str(exc)
        finally:
            self.client_detail_loading = False

    def open_client_edit(self, client_id: str) -> None:
        self.dialog_generation += 1
        row = self._find_client(client_id)
        if row is None:
            self.client_action_message = "Não foi possível localizar este cliente."
            return
        self.selected_client = {
            "id": client_id,
            "name": row.get("_client_name", ""),
            "cpf": row.get("_client_cpf", ""),
            "phone": row.get("Telefone", row.get("telefone", "")),
            "email": row.get("Email", row.get("email", "")),
            "last_activity": row.get("_client_last_activity", "Sem compras"),
        }
        self.client_form_name = self.selected_client["name"]
        self.client_form_cpf = self.selected_client["cpf"]
        self.client_form_phone = self.selected_client["phone"]
        self.client_form_email = self.selected_client["email"]
        self.client_dialog_mode = "edit"
        self.client_action_message = ""
        self.client_dialog_open = True

    def close_client_dialog(self, is_open: bool) -> None:
        self.client_dialog_open = is_open
        if not is_open:
            self.dialog_generation += 1

    def set_client_form_name(self, value: str) -> None:
        self.client_form_name = value

    def set_client_form_cpf(self, value: str) -> None:
        self.client_form_cpf = value

    def set_client_form_phone(self, value: str) -> None:
        self.client_form_phone = value

    def set_client_form_email(self, value: str) -> None:
        self.client_form_email = value

    def open_client_delete(self, client_id: str) -> None:
        self.dialog_generation += 1
        row = self._find_client(client_id)
        if row is None:
            self.client_action_message = "Não foi possível localizar este cliente."
            return
        self.selected_client = {
            "id": client_id,
            "name": row.get("_client_name", "Cliente sem nome"),
            "cpf": row.get("_client_cpf", "Não informado"),
            "phone": row.get("_client_phone", "Telefone não informado"),
            "email": row.get("_client_email", "Não informado"),
            "last_activity": row.get("_client_last_activity", "Sem compras"),
        }
        self.client_dialog_mode = "delete"
        self.client_action_message = ""
        self.client_delete_loading = False
        self.client_dialog_open = True

    async def delete_client(self) -> None:
        client_id = self.selected_client.get("id", "").strip()
        if not client_id.isdigit() or int(client_id) < 1:
            self.client_action_message = "Identificador de cliente inválido."
            return
        self.client_delete_loading = True
        self.client_action_message = ""
        try:
            auth_state = await self.get_state(AuthState)
            response = await client.async_request(
                "DELETE",
                f"/clientes/{client_id}",
                token=auth_state.token,
            )
            if not isinstance(response, dict) or response.get("deleted") is not True:
                raise XanoError("A API não confirmou a exclusão do cliente.")
            self.client_dialog_open = False
            self.read_generation += 1
            self.records = []
            self.client_action_message = response.get("message") or "Cliente excluído com sucesso."
            return ClientsState.load("/clientes", "Clientes")
        except XanoError as exc:
            self.client_action_message = str(exc)
        finally:
            self.client_delete_loading = False

    async def save_client_edits(self) -> None:
        client_id = self.selected_client.get("id", "")
        values = (
            self.client_form_name.strip(),
            self.client_form_cpf.strip(),
            self.client_form_phone.strip(),
            self.client_form_email.strip(),
        )
        if not client_id or not all(values):
            self.client_action_message = "Preencha nome, CPF, telefone e e-mail."
            return
        self.client_action_message = ""
        try:
            auth_state = await self.get_state(AuthState)
            await client.async_request(
                "PATCH",
                f"/clientes/{client_id}",
                token=auth_state.token,
                json={
                    "CNome": values[0],
                    "CPF": values[1],
                    "Telefone": values[2],
                    "Email": values[3],
                },
            )
            self.client_dialog_open = False
            self.client_action_message = "Cadastro do cliente atualizado."
            self.read_generation += 1
            self.records = []
            self.complete = False
            return ClientsState.load("/clientes", "Clientes")
        except XanoError as exc:
            self.client_action_message = str(exc)

    @read_event(outputs=("part_dialog_loading", "part_dialog_error", "part_edit_areas", "selected_part_id", "part_form_name", "part_form_price", "part_form_area_id", "part_dialog_open"),
                loading="part_dialog_loading", generation_field="part_detail_generation")
    async def open_part_edit(self, part_id: str):
        row = next(
            (item for item in self.records if str(item.get("id", "")) == part_id),
            None,
        )
        if row is None:
            self.client_action_message = "Não foi possível localizar esta peça."
            return
        self.part_dialog_loading = True
        self.part_dialog_error = ""
        self.selected_part_id = part_id
        self.part_form_name = str(row.get("PCNome", row.get("Nome", "")))
        self.part_form_price = str(row.get("PCvalor", ""))
        self.part_form_area_id = str(row.get("area_id", "") or "")
        self.part_dialog_open = True
        yield
        try:
            auth_state = await self.get_state(AuthState)
            areas = await catalogs.get("/veiculo-areas", auth_state.token)
            if not isinstance(areas, list) or any(
                not isinstance(area, dict)
                or area.get("id") is None
                or not isinstance(area.get("Secao"), str)
                for area in areas
            ):
                raise XanoError("A API retornou uma lista de áreas de peças inválida.")
            self.part_edit_areas = [
                {"id": str(area["id"]), "Secao": area["Secao"].strip()}
                for area in areas
                if area["Secao"].strip()
            ]
            self.selected_part_id = part_id
            self.part_form_name = str(
                row.get("PCNome", row.get("nome", row.get("Nome", "")))
            )
            self.part_form_price = str(
                row.get("PCvalor", row.get("preco", row.get("Preco", "")))
            )
            self.part_form_area_id = str(row.get("area_id", "") or "")
            self.part_dialog_open = True
        except XanoError as exc:
            self.part_dialog_error = str(exc)
        finally:
            self.part_dialog_loading = False

    def close_part_dialog(self, is_open: bool) -> None:
        self.part_dialog_open = is_open
        if not is_open:
            self.part_detail_generation += 1

    def set_part_form_name(self, value: str) -> None:
        self.part_form_name = value

    def set_part_form_price(self, value: str) -> None:
        self.part_form_price = value

    def set_part_form_area_id(self, value: str) -> None:
        self.part_form_area_id = value

    async def save_part_edits(self) -> None:
        name = self.part_form_name.strip()
        if not name:
            self.part_dialog_error = "O campo Nome é obrigatório."
            return
        try:
            price = Decimal(self.part_form_price.strip().replace(",", "."))
        except (InvalidOperation, ValueError):
            self.part_dialog_error = "Valor inválido no campo Preço."
            return
        if not price.is_finite() or price < 0:
            self.part_dialog_error = (
                "O campo Preço precisa ser um valor finito e não negativo."
            )
            return
        payload: dict[str, str | float | int] = {
            "PCNome": name,
            "PCvalor": float(price),
        }
        if self.part_form_area_id:
            valid_area_ids = {area["id"] for area in self.part_edit_areas}
            if self.part_form_area_id not in valid_area_ids:
                self.part_dialog_error = "Selecione uma área válida."
                return
            payload["area_id"] = int(self.part_form_area_id)

        self.part_dialog_saving = True
        self.part_dialog_error = ""
        try:
            auth_state = await self.get_state(AuthState)
            await client.async_request(
                "PATCH",
                f"/pecas/{self.selected_part_id}",
                token=auth_state.token,
                json=payload,
            )
            self.part_dialog_open = False
            self.read_generation += 1
            self.records = []
            self.complete = False
            return PartsState.load("/pecas", "Peças e estoque")
        except XanoError as exc:
            self.part_dialog_error = str(exc)
        finally:
            self.part_dialog_saving = False

    def set_client_page(self, page: int) -> None:
        self.client_page = max(1, min(page, self.client_total_pages))

    def previous_client_page(self) -> None:
        self.set_client_page(self.client_page - 1)

    def next_client_page(self) -> None:
        self.set_client_page(self.client_page + 1)

    @rx.var
    def filtered_records(self) -> list[dict]:
        rows = self.records
        if self.query:
            needle = self.query.lower()
            rows = [
                row for row in rows
                if needle in " ".join(str(v) for v in row.values()).lower()
            ]
        if self.endpoint == "/clientes":
            rows = _sort_client_records(rows, self.client_sort_order)
        return rows

    @rx.var
    def client_total_pages(self) -> int:
        return max(1, (len(self.filtered_records) + 9) // 10)

    @rx.var
    def paginated_clients(self) -> list[dict]:
        start = (self.client_page - 1) * 10
        return self.filtered_records[start : start + 10]


class ClientsState(ResourceState, rx.State):
    """Independent client list, search, pagination and dialogs."""


class VehiclesState(ResourceState, rx.State):
    """Independent vehicle collection."""


class PartsState(ResourceState, rx.State):
    """Independent parts and editing state."""


class UsersState(ResourceState, rx.State):
    """Independent user collection."""
