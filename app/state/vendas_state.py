from __future__ import annotations

import asyncio
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import reflex as rx

from app.services.catalogs import catalogs
from app.services.sales_query import sales_query_params
from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState
from app.state.read_lifecycle import read_event


def _parse_installment_count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as exc:
        raise XanoError("A quantidade de parcelas deve ser um número inteiro.") from exc
    if not 1 <= count <= 24:
        raise XanoError("A quantidade de parcelas deve estar entre 1 e 24.")
    return count


def _format_local_datetime(value: str | int | float, include_time: bool = False) -> str:
    if not value:
        return ""
    try:
        if isinstance(value, (int, float)):
            parsed = datetime.fromtimestamp(value / 1000, tz=ZoneInfo("America/Sao_Paulo"))
            if include_time:
                return parsed.strftime("%d/%m/%Y %H:%M")
            return parsed.strftime("%d/%m/%Y")
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(ZoneInfo("America/Sao_Paulo"))
        if include_time:
            return parsed.strftime("%d/%m/%Y %H:%M")
        return parsed.strftime("%d/%m/%Y")
    except ValueError as exc:
        raise XanoError("A API retornou uma data de parcela inválida.") from exc


def _format_currency(value: Decimal) -> str:
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _positive_integer(value: object, label: str) -> int:
    if isinstance(value, bool):
        raise XanoError(f"{label} precisa ser um número inteiro positivo.")
    try:
        parsed = Decimal(str(value))
        if not parsed.is_finite() or parsed < 1 or parsed != parsed.to_integral_value():
            raise ValueError
        return int(parsed)
    except (ValueError, InvalidOperation) as exc:
        raise XanoError(f"{label} precisa ser um número inteiro positivo.") from exc


class VendasState(rx.State):
    read_generation: int = 0
    methods_generation: int = 0
    references_generation: int = 0
    read_id: str = ""
    detail_generation: int = 0
    list_needs_refresh: bool = False
    list_loading: bool = False
    list_error: str = ""
    methods_loading: bool = True
    methods_error: str = ""
    detail_loading: bool = False
    detail_error: str = ""
    references_loading: bool = False
    references_error: str = ""
    clientes: list[dict[str, str]] = []
    veiculos_disponiveis: list[dict[str, str]] = []
    pecas_disponiveis: list[dict[str, str]] = []
    vendas: list[dict[str, str]] = []
    busca: str = ""
    filtro_forma_pagamento: str = ""
    filtro_data_inicio: str = ""
    filtro_data_fim: str = ""
    cliente_id: str = ""
    forma_pagamento_id: str = ""
    itens_json: str = "[]"
    desconto: str = "0"
    numero_parcelas: str = "1"
    payment_methods: list[dict[str, str]] = []
    venda_id: str = ""
    payment_url: str = ""
    payment_status: str = ""
    payment_flow: str = ""
    payment_due_date: str = ""
    total_confirmado: str = ""
    creation_uncertain: bool = False
    parcelas: list[dict[str, str]] = []
    forma_recebida_id: str = ""
    mensagem: str = ""
    erro: str = ""
    processando: bool = False
    selected_vehicle_id: str = ""
    selected_part_id: str = ""
    selected_part_quantity: str = "1"
    selected_items: list[dict[str, str]] = []

    def _invalidate_list_query(self):
        self.read_generation += 1
        self.list_loading = False
        self.list_needs_refresh = True
        self.vendas, self.list_error = [], ""

    def set_busca(self, value: str) -> None:
        self.busca = value
        self._invalidate_list_query()

    def set_filtro_forma_pagamento(self, value: str) -> None:
        self.filtro_forma_pagamento = value
        self._invalidate_list_query()

    def set_filtro_data_inicio(self, value: str) -> None:
        self.filtro_data_inicio = value
        self._invalidate_list_query()

    def set_filtro_data_fim(self, value: str) -> None:
        self.filtro_data_fim = value
        self._invalidate_list_query()

    def set_selected_vehicle_id(self, value: str) -> None:
        self.selected_vehicle_id = value

    def set_selected_part_id(self, value: str) -> None:
        self.selected_part_id = value

    def set_selected_part_quantity(self, value: str) -> None:
        self.selected_part_quantity = value

    def _rows(self, result: object, message: str) -> list[dict]:
        rows = result if isinstance(result, list) else (
            result.get("items", result.get("data", []))
            if isinstance(result, dict) else []
        )
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise XanoError(message)
        return rows

    @read_event(outputs=("vendas", "list_loading", "list_error", "list_needs_refresh"),
                inputs=("busca", "filtro_forma_pagamento", "filtro_data_inicio", "filtro_data_fim"),
                loading="list_loading", clear=("vendas", "list_error", "list_needs_refresh"))
    async def load_sales(self) -> None:
        self.list_loading, self.list_error, self.mensagem = True, "", ""
        try:
            auth_state = await self.get_state(AuthState)
            params = sales_query_params(
                busca=self.busca,
                forma_pagamento_id=self.filtro_forma_pagamento,
                data_inicio=self.filtro_data_inicio,
                data_fim=self.filtro_data_fim,
            )
            result = await client.async_request("GET", "/vendas", token=auth_state.token, params=params)
            self.vendas = [
                {
                    "id": str(row.get("id", "")),
                    "cliente": str((row.get("cliente") or {}).get("CNome", "Não informado")),
                    "vendedor": str((row.get("vendedor") or {}).get("UNome", "Não informado")),
                    "forma": str((row.get("forma_pagamento") or {}).get("Metodo", "Não informado")),
                    "valor_final": _format_currency(Decimal(str(row.get("Valor_final", 0)))),
                    "data": _format_local_datetime(row.get("data_venda") or "", include_time=True),
                }
                for row in self._rows(result, "A API retornou vendas em formato inválido.")
            ]
        except (XanoError, InvalidOperation, ValueError) as exc:
            self.vendas = []
            self.list_error = str(exc)
        finally:
            self.list_loading = False

    def load_sales_page(self):
        return [VendasState.load_sales, VendasState.load_payment_methods]

    @read_event(outputs=("clientes", "veiculos_disponiveis", "pecas_disponiveis", "references_loading", "references_error"),
                loading="references_loading", clear=("clientes", "veiculos_disponiveis", "pecas_disponiveis", "references_error"),
                generation_field="references_generation")
    async def load_sale_references(self) -> None:
        self.references_loading, self.references_error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            clients, vehicles, parts, statuses = await asyncio.gather(
                client.async_request("GET", "/clientes", token=auth_state.token, params={"page": 1, "per_page": 100}),
                client.async_request("GET", "/veiculos", token=auth_state.token, params={"page": 1, "per_page": 100}),
                client.async_request("GET", "/pecas", token=auth_state.token, params={"page": 1, "per_page": 100}),
                catalogs.get("/status-veiculos", auth_state.token),
            )
            status_rows = self._rows(statuses, "A API retornou status de veículos inválidos.")
            available_ids = {
                str(row.get("id")) for row in status_rows
                if str(row.get("Descricao", row.get("descricao", ""))).strip().lower() in {"disponível", "disponivel"}
            }
            client_rows = self._rows(clients, "A API retornou clientes em formato inválido.")
            vehicle_rows = self._rows(vehicles, "A API retornou veículos em formato inválido.")
            part_rows = self._rows(parts, "A API retornou peças em formato inválido.")
            self.clientes = [
                {"id": str(row.get("id")), "nome": str(row.get("CNome", row.get("Nome", "Cliente sem nome")))}
                for row in client_rows if row.get("id") is not None
            ]
            self.veiculos_disponiveis = [
                {
                    "id": str(row.get("id")),
                    "nome": f"{row.get('Marca', '')} {row.get('Modelo', '')}".strip() or "Veículo sem nome",
                    "preco": str(row.get("Preco", 0)),
                    "imagem": str(row.get("imagem_url", "") or ""),
                }
                for row in vehicle_rows
                if str(row.get("status_id", "")) in available_ids and row.get("id") is not None
            ]
            self.pecas_disponiveis = [
                {
                    "id": str(row.get("id")),
                    "nome": str(row.get("PCNome", row.get("Nome", "Peça sem nome"))),
                    "preco": str(row.get("PCvalor", 0)),
                    "estoque": str(row.get("qtd_disp", 0)),
                    "imagem": str(row.get("imagem_url", "") or ""),
                }
                for row in part_rows
                if row.get("id") is not None and Decimal(str(row.get("qtd_disp", 0) or 0)) > 0
            ]
        except (XanoError, InvalidOperation, ValueError) as exc:
            self.references_error = str(exc)
        finally:
            self.references_loading = False

    def add_vehicle(self, vehicle_id: str) -> None:
        self.selected_vehicle_id = vehicle_id
        vehicle = next((row for row in self.veiculos_disponiveis if row["id"] == vehicle_id), None)
        if vehicle and not any(
            item.get("tipo") == "veiculo" and item.get("id") == vehicle_id
            for item in self.selected_items
        ):
            self.selected_items.append({"tipo": "veiculo", "id": vehicle["id"], "nome": vehicle["nome"], "preco": vehicle["preco"], "qtd": "1"})

    def add_part(self) -> None:
        part = next((row for row in self.pecas_disponiveis if row["id"] == self.selected_part_id), None)
        if not part:
            self.erro = "Selecione uma peça antes de adicionar."
            return
        try:
            quantity = int(self.selected_part_quantity)
            stock = int(Decimal(part["estoque"]))
        except (ValueError, InvalidOperation):
            self.erro = "Informe uma quantidade válida para a peça."
            return
        if quantity < 1 or quantity > stock:
            self.erro = "A quantidade não pode superar o estoque disponível."
            return
        self.erro = ""
        self.selected_items = [item for item in self.selected_items if not (item.get("tipo") == "peca" and item.get("id") == part["id"])]
        self.selected_items.append({"tipo": "peca", "id": part["id"], "nome": part["nome"], "preco": part["preco"], "qtd": str(quantity)})

    def add_part_for_id(self, part_id: str) -> None:
        self.selected_part_id = part_id
        self.add_part()

    def remove_item(self, item_type: str, item_id: str) -> None:
        self.selected_items = [item for item in self.selected_items if not (item.get("tipo") == item_type and item.get("id") == item_id)]

    @rx.var
    def valor_bruto_display(self) -> str:
        total = sum(Decimal(str(item.get("preco", 0))) * int(item.get("qtd", 1)) for item in self.selected_items)
        return f"R$ {_format_currency(total)}"

    @rx.var
    def valor_final_display(self) -> str:
        total = sum(Decimal(str(item.get("preco", 0))) * int(item.get("qtd", 1)) for item in self.selected_items)
        try:
            discount = Decimal(self.desconto.replace(",", "."))
        except InvalidOperation:
            discount = Decimal("0")
        return f"R$ {_format_currency(max(total - discount, Decimal('0')))}"

    def set_cliente_id(self, value: str) -> None:
        self.cliente_id = value

    def set_forma_pagamento_id(self, value: str) -> None:
        self.forma_pagamento_id = value

    def set_itens_json(self, value: str) -> None:
        self.itens_json = value

    def set_desconto(self, value: str) -> None:
        self.desconto = value

    def set_numero_parcelas(self, value: str) -> None:
        self.numero_parcelas = value

    def set_forma_recebida_id(self, value: str) -> None:
        self.forma_recebida_id = value

    @read_event(outputs=("payment_methods", "methods_error", "methods_loading"), loading="methods_loading",
                clear=("payment_methods", "methods_error"), generation_field="methods_generation")
    async def load_payment_methods(self, force: bool = False) -> None:
        self.methods_loading, self.methods_error = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            result = await catalogs.get("/formas-pagamento", auth_state.token, force=force)
            rows = result if isinstance(result, list) else result.get(
                "items", result.get("data", [])
            )
            if not isinstance(rows, list):
                raise XanoError("A API de formas de pagamento retornou dados inválidos.")
            self.payment_methods = [
                {
                    "id": str(row.get("id") or row.get("Id") or ""),
                    "name": str(
                        row.get("Metodo")
                        or row.get("metodo")
                        or row.get("nome")
                        or row.get("Nome")
                        or ""
                    ),
                }
                for row in rows
                if isinstance(row, dict)
                and (row.get("id") or row.get("Id"))
                and (row.get("Metodo") or row.get("metodo"))
            ]
            if not self.payment_methods:
                raise XanoError(
                    "Nenhuma forma de pagamento foi encontrada. Cadastre/valide as referências no Xano."
                )
        except (XanoError, AttributeError) as exc:
            self.payment_methods = []
            self.methods_error = str(exc)
        finally:
            self.methods_loading = False

    def _sale_payload(self) -> dict[str, object]:
        if not self.cliente_id.strip():
            raise XanoError("Selecione o cliente da venda.")

        cliente_id = _positive_integer(self.cliente_id, "Cliente")

        if self.selected_items:
            items = [
                {
                    ("veiculo_id" if item["tipo"] == "veiculo" else "peca_id"): item["id"],
                    "qtd": item["qtd"],
                }
                for item in self.selected_items
            ]
        else:
            try:
                items = json.loads(self.itens_json)
            except json.JSONDecodeError as exc:
                raise XanoError("Os itens precisam estar em formato JSON válido.") from exc
        if not isinstance(items, list) or not items:
            raise XanoError("Adicione pelo menos um item à venda.")
        normalized_items: list[dict[str, int]] = []
        for item in items:
            if not isinstance(item, dict):
                raise XanoError("Cada item deve ser um objeto JSON.")
            has_vehicle = bool(item.get("veiculo_id"))
            has_part = bool(item.get("peca_id"))
            if has_vehicle == has_part:
                raise XanoError("Cada item precisa conter exatamente veiculo_id ou peca_id.")
            if item.keys() - {"veiculo_id", "peca_id", "qtd"}:
                raise XanoError("Um item contém campos não aceitos pela API.")
            normalized = {"qtd": _positive_integer(item.get("qtd", 1), "Quantidade")}
            identifier_key = "veiculo_id" if has_vehicle else "peca_id"
            normalized[identifier_key] = _positive_integer(item[identifier_key], "ID do item")
            if has_vehicle and normalized["qtd"] != 1:
                raise XanoError("Cada veículo deve ter quantidade igual a 1.")
            normalized_items.append(normalized)

        return {
            "cliente_id": cliente_id,
            "itens": normalized_items,
        }

    async def create_sale(self) -> None:
        if self.processando or self.venda_id or self.creation_uncertain:
            return
        self.processando, self.erro, self.mensagem = True, "", ""
        attempted = False
        try:
            payload = self._sale_payload()
            auth_state = await self.get_state(AuthState)
            attempted = True
            response = await client.async_request(
                "POST",
                "/vendas",
                token=auth_state.token,
                json=payload,
            )
            sale_id = (
                response.get("id") or response.get("Id")
                if isinstance(response, dict)
                else None
            )
            if sale_id is None and isinstance(response, dict):
                sale = response.get("venda")
                sale_id = sale.get("Id") if isinstance(sale, dict) else None
            if sale_id is None:
                raise XanoError(
                    "A venda foi enviada, mas a API não retornou o ID. "
                    "Verifique a venda no Xano antes de tentar criá-la novamente."
                )
            try:
                self.venda_id = str(_positive_integer(sale_id, "ID da venda retornado"))
            except XanoError as exc:
                raise XanoError("A API não retornou o ID válido da venda. Confira a listagem antes de repetir.") from exc
            self.read_generation += 1
            self.references_generation += 1
            self.vendas = []
            from app.state.resource_state import ClientsState, PartsState, VehiclesState
            for cls in (ClientsState, VehiclesState, PartsState):
                collection = await self.get_state(cls)
                collection.read_generation += 1
                collection.records = []
                collection.complete = False
            self.parcelas = []
            self.payment_flow = "ASAAS"
            amount = Decimal(str(response.get("Valor_final")))
            if not amount.is_finite() or amount <= 0:
                raise XanoError("A API não retornou o valor final válido. A reserva foi preservada.")
            self.total_confirmado = "R$ " + _format_currency(amount)
            self.mensagem = f"Venda #{sale_id} criada e reservada."
            await self.generate_payment_link()
        except (XanoError, ValueError, InvalidOperation) as exc:
            self.erro = str(exc)
            rejected = any(f"({status})" in self.erro for status in (400, 401, 403, 404, 409, 422))
            rejected = rejected or "sessão expirou" in self.erro or "não tem permissão" in self.erro
            if attempted and not self.venda_id and not rejected:
                self.creation_uncertain = True
                self.erro += " Confira a listagem de vendas antes de iniciar outra tentativa."
        finally:
            self.processando = False

    async def generate_payment_link(self) -> None:
        if not self.venda_id.isdigit() or int(self.venda_id) < 1:
            self.erro = "Selecione uma venda válida para gerar o link."
            return
        self.processando, self.erro, self.mensagem = True, "", ""
        try:
            auth_state = await self.get_state(AuthState)
            response = await client.async_request(
                "POST", f"/vendas/{self.venda_id}/link-pagamento", token=auth_state.token,
            )
            self._set_payment(response)
            if not self.payment_url:
                raise XanoError("A cobrança não retornou um link válido. A venda foi preservada.")
            self.mensagem = "Link salvo. O pagamento será confirmado automaticamente pelo ASAAS."
        except XanoError as exc:
            self.erro = f"Venda #{self.venda_id} preservada. {exc}"
        finally:
            self.processando = False

    def _set_payment(self, response: object) -> None:
        if not isinstance(response, dict):
            raise XanoError("A API retornou dados de pagamento inválidos.")
        payment = response.get("asaas_cobranca", response)
        if payment is None:
            payment = {}
        if not isinstance(payment, dict):
            raise XanoError("A API retornou uma cobrança inválida.")
        url = str(payment.get("invoice_url") or "").strip()
        parsed = urlparse(url)
        allowed_hosts = {"www.asaas.com", "asaas.com", "sandbox.asaas.com", "www.sandbox.asaas.com"}
        if url and (parsed.scheme != "https" or parsed.hostname not in allowed_hosts or parsed.username or parsed.password):
            raise XanoError("A API retornou um endereço de pagamento inválido.")
        self.payment_url = url
        self.payment_status = str(payment.get("status") or "")
        due = str(payment.get("due_date") or "")
        self.payment_due_date = _format_local_datetime(due) if due else ""

    @rx.var
    def payment_status_label(self) -> str:
        return {
            "": "Aguardando geração do link", "PENDING": "Aguardando pagamento",
            "OVERDUE": "Vencida", "CONFIRMED": "Pagamento confirmado",
            "RECEIVED": "Pagamento recebido", "RECEIVED_IN_CASH": "Pagamento recebido",
            "DELETED": "Cobrança cancelada", "REFUNDED": "Pagamento estornado",
            "CHARGEBACK_REQUESTED": "Pagamento em análise",
        }.get(self.payment_status, "Consulte a situação na fatura")

    def start_new_sale(self) -> None:
        self.venda_id = self.payment_url = self.payment_status = self.payment_flow = ""
        self.total_confirmado = self.payment_due_date = self.erro = self.mensagem = ""
        self.cliente_id = ""
        self.selected_items = []
        self.parcelas = []
        self.creation_uncertain = False

    @staticmethod
    def _extract_installments(response: object) -> list[dict[str, str]]:
        if not isinstance(response, dict):
            return []
        if "parcelas" not in response:
            return []
        rows = response["parcelas"]
        if not isinstance(rows, list):
            return []
        installments: list[dict[str, str]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                installment_id = int(row.get("id"))
                installment_number = int(row.get("numero_parcela"))
                installment_total = int(row.get("total_parcelas"))
                amount = Decimal(str(row.get("valor")))
            except (TypeError, ValueError, InvalidOperation):
                continue
            status = str(row.get("status") or "")
            if (
                installment_id < 1
                or not 1 <= installment_number <= installment_total <= 24
                or not amount.is_finite()
                or amount <= 0
                or status not in ("PENDENTE", "RECEBIDA", "CANCELADA")
            ):
                continue
            try:
                due_date = _format_local_datetime(row.get("vencimento") or "")
            except XanoError:
                continue
            if not due_date:
                continue
            try:
                received_at = _format_local_datetime(
                    row.get("recebido_em") or "",
                    include_time=True,
                )
            except XanoError:
                continue
            received_method = str(row.get("forma_recebida") or "")
            received_by = str(row.get("recebido_por") or "")
            if status == "RECEBIDA" and not (received_at and received_method and received_by):
                continue
            installments.append(
                {
                    "id": str(installment_id),
                    "numero_parcela": str(installment_number),
                    "total_parcelas": str(installment_total),
                    "valor": _format_currency(amount),
                    "vencimento": due_date,
                    "status": status,
                    "forma_recebida": received_method,
                    "recebido_em": received_at,
                    "recebido_por": received_by,
                }
            )
        return installments

    @read_event(outputs=("read_id", "venda_id", "payment_url", "payment_status", "payment_flow", "total_confirmado", "payment_due_date", "parcelas", "detail_error", "detail_loading", "payment_methods", "methods_error", "methods_loading"),
                loading="detail_loading", clear=("payment_url", "payment_status", "payment_flow", "total_confirmado", "payment_due_date", "parcelas", "detail_error", "erro", "mensagem"),
                generation_field="detail_generation")
    async def load_sale(self) -> None:
        self.payment_url = self.payment_status = self.payment_flow = ""
        self.total_confirmado = self.payment_due_date = ""
        self.parcelas = []
        sale_id = str(self.router.page.params.get("id", "")).strip()
        self.read_id = sale_id
        if not sale_id.isdigit() or int(sale_id) < 1:
            self.venda_id = ""
            self.detail_loading = False
            self.detail_error = "Identificador de venda inválido."
            return
        self.venda_id = sale_id
        self.detail_loading, self.detail_error, self.mensagem = True, "", ""
        try:
            auth_state = await self.get_state(AuthState)
            response = await client.async_request(
                "GET",
                f"/vendas/{sale_id}/pagamento",
                token=auth_state.token,
            )
            if not isinstance(response, dict):
                raise XanoError("A API retornou dados inválidos para as parcelas.")
            self.payment_flow = str(response.get("payment_flow") or "LEGADO")
            amount = Decimal(str(response.get("total_venda", 0)))
            if not amount.is_finite() or amount <= 0:
                raise XanoError("A API não retornou o valor válido da venda.")
            self._set_payment(response)
            self.total_confirmado = "R$ " + _format_currency(amount)
            self.parcelas = self._extract_installments(response)
            if self.payment_flow != "ASAAS":
                await VendasState.load_payment_methods.fn.read_body(self)
        except (XanoError, InvalidOperation, ValueError) as exc:
            self.detail_error = str(exc)
        finally:
            self.detail_loading = False

    async def receive_installment(self, parcela_id: str) -> None:
        self.processando, self.erro, self.mensagem = True, "", ""
        try:
            if self.payment_flow == "ASAAS":
                raise XanoError("Recebimentos desta venda são confirmados pelo ASAAS.")
            if (
                not self.venda_id
                or not parcela_id.isdigit()
                or int(parcela_id) < 1
            ):
                raise XanoError("Venda ou parcela inválida.")
            if not self.forma_recebida_id.isdigit() or int(self.forma_recebida_id) < 1:
                raise XanoError("Selecione a forma de pagamento realmente recebida.")
            auth_state = await self.get_state(AuthState)
            await client.async_request(
                "POST",
                f"/vendas/{self.venda_id}/parcelas/{parcela_id}/receber",
                token=auth_state.token,
                json={"forma_pagamento_id": int(self.forma_recebida_id)},
            )
            self.mensagem = "Baixa manual registrada no Xano."
            self.detail_generation += 1
            return SaleDetailState.load_sale
        except XanoError as exc:
            self.erro = str(exc)
        finally:
            self.processando = False


class SaleDetailState(rx.State):
    """Payment detail never overwrites a sale draft or its recovery identifier."""
    read_generation: int = 0
    methods_generation: int = 0
    read_id: str = ""
    detail_generation: int = 0
    venda_id: str = ""
    payment_url: str = ""
    payment_status: str = ""
    payment_flow: str = ""
    payment_due_date: str = ""
    total_confirmado: str = ""
    parcelas: list[dict[str, str]] = []  # noqa: RUF012 -- Reflex creates per-session defaults
    payment_methods: list[dict[str, str]] = []  # noqa: RUF012 -- Reflex creates per-session defaults
    methods_error: str = ""
    methods_loading: bool = False
    forma_recebida_id: str = ""
    detail_loading: bool = False
    detail_error: str = ""
    processando: bool = False
    erro: str = ""
    mensagem: str = ""

    _set_payment = VendasState._set_payment
    _extract_installments = staticmethod(VendasState._extract_installments)
    load_sale = VendasState.load_sale.fn
    load_payment_methods = VendasState.load_payment_methods.fn
    generate_payment_link = VendasState.generate_payment_link.fn
    receive_installment = VendasState.receive_installment.fn
    set_forma_recebida_id = VendasState.set_forma_recebida_id.fn

    @rx.var
    def payment_status_label(self) -> str:
        return {
            "": "Aguardando geração do link", "PENDING": "Aguardando pagamento",
            "OVERDUE": "Vencida", "CONFIRMED": "Pagamento confirmado",
            "RECEIVED": "Pagamento recebido", "RECEIVED_IN_CASH": "Pagamento recebido",
            "DELETED": "Cobrança cancelada", "REFUNDED": "Pagamento estornado",
            "CHARGEBACK_REQUESTED": "Pagamento em análise",
        }.get(self.payment_status, "Consulte a situação na fatura")
