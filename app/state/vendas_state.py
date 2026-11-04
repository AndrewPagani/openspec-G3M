from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import reflex as rx

from app.services.xano_client import XanoError, client
from app.state.auth_state import AuthState


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


class VendasState(rx.State):
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
    parcelas: list[dict[str, str]] = []
    forma_recebida_id: str = ""
    mensagem: str = ""
    erro: str = ""
    processando: bool = False
    selected_vehicle_id: str = ""
    selected_part_id: str = ""
    selected_part_quantity: str = "1"
    selected_items: list[dict[str, str]] = []

    def set_busca(self, value: str) -> None:
        self.busca = value

    def set_filtro_forma_pagamento(self, value: str) -> None:
        self.filtro_forma_pagamento = value

    def set_filtro_data_inicio(self, value: str) -> None:
        self.filtro_data_inicio = value

    def set_filtro_data_fim(self, value: str) -> None:
        self.filtro_data_fim = value

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

    async def load_sales(self) -> None:
        self.processando, self.erro = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            params = {
                "page": "1",
                "per_page": "100",
                "busca": self.busca.strip(),
                "cliente_id": "{}",
                "vendedor_id": "{}",
                "status_id": "{}",
                "forma_pagamento_id": (
                    self.filtro_forma_pagamento
                    if self.filtro_forma_pagamento
                    else "{}"
                ),
                "data_inicio": self.filtro_data_inicio if self.filtro_data_inicio else "{}",
                "data_fim": self.filtro_data_fim if self.filtro_data_fim else "{}",
            }
            result = client.request("GET", "/vendas", token=auth_state.token, params=params)
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
            self.erro = str(exc)
        finally:
            self.processando = False

    async def load_sales_page(self) -> None:
        await self.load_payment_methods()
        await self.load_sales()

    async def load_sale_references(self) -> None:
        self.processando, self.erro = True, ""
        try:
            auth_state = await self.get_state(AuthState)
            await self.load_payment_methods()
            clients = client.request("GET", "/clientes", token=auth_state.token, params={"page": 1, "per_page": 100})
            vehicles = client.request("GET", "/veiculos", token=auth_state.token, params={"page": 1, "per_page": 100})
            parts = client.request("GET", "/pecas", token=auth_state.token, params={"page": 1, "per_page": 100})
            statuses = client.request("GET", "/status-veiculos", token=auth_state.token)
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
            self.erro = str(exc)
        finally:
            self.processando = False

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
        self.selected_items = [item for item in self.selected_items if item.get("id") != part["id"]]
        self.selected_items.append({"tipo": "peca", "id": part["id"], "nome": part["nome"], "preco": part["preco"], "qtd": str(quantity)})

    def add_part_for_id(self, part_id: str) -> None:
        self.selected_part_id = part_id
        self.add_part()

    def remove_item(self, item_id: str) -> None:
        self.selected_items = [item for item in self.selected_items if item.get("id") != item_id]

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

    async def load_payment_methods(self) -> None:
        self.erro = ""
        try:
            auth_state = await self.get_state(AuthState)
            result = client.request(
                "GET",
                "/formas-pagamento",
                token=auth_state.token,
            )
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
            self.erro = str(exc)

    def _sale_payload(self) -> dict[str, object]:
        if not self.cliente_id.strip() or not self.forma_pagamento_id.strip():
            raise XanoError("Informe o ID do cliente e a forma de pagamento.")

        try:
            discount = Decimal(self.desconto.replace(",", "."))
            cliente_id = int(self.cliente_id)
            forma_pagamento_id = int(self.forma_pagamento_id)
        except (ValueError, InvalidOperation) as exc:
            raise XanoError(
                "IDs e desconto devem conter valores numéricos válidos."
            ) from exc
        if cliente_id < 1 or forma_pagamento_id < 1:
            raise XanoError("Os IDs do cliente e da forma de pagamento devem ser positivos.")

        numero_parcelas = _parse_installment_count(self.numero_parcelas)

        if self.selected_items:
            items = [
                {
                    ("veiculo_id" if item["tipo"] == "veiculo" else "peca_id"): int(item["id"]),
                    "qtd": int(item["qtd"]),
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
            try:
                normalized = {"qtd": int(item.get("qtd", 1))}
                if has_vehicle:
                    normalized["veiculo_id"] = int(item["veiculo_id"])
                else:
                    normalized["peca_id"] = int(item["peca_id"])
            except (TypeError, ValueError) as exc:
                raise XanoError("IDs de item e quantidades precisam ser números inteiros.") from exc
            if normalized["qtd"] < 1:
                raise XanoError("A quantidade de cada item deve ser positiva.")
            if any(
                identifier < 1
                for key, identifier in normalized.items()
                if key != "qtd"
            ):
                raise XanoError("Os IDs dos itens devem ser positivos.")
            normalized_items.append(normalized)
        if not discount.is_finite() or discount < 0:
            raise XanoError("O desconto precisa ser finito e não negativo.")

        return {
            "cliente_id": cliente_id,
            "forma_pagamento_id": forma_pagamento_id,
            "numero_parcelas": numero_parcelas,
            "Desconto": float(discount),
            "itens": normalized_items,
        }

    async def create_sale(self) -> None:
        self.processando, self.erro, self.mensagem = True, "", ""
        try:
            payload = self._sale_payload()
            auth_state = await self.get_state(AuthState)
            response = client.request(
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
            self.venda_id = str(sale_id)
            self.parcelas = []
            self.mensagem = f"Venda #{sale_id} criada e reservada."
        except (XanoError, ValueError) as exc:
            self.erro = str(exc)
        finally:
            self.processando = False

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
                due_date = _format_local_datetime(str(row.get("vencimento") or ""))
            except XanoError:
                continue
            if not due_date:
                continue
            try:
                received_at = _format_local_datetime(
                    str(row.get("recebido_em") or ""),
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

    async def load_sale(self) -> None:
        sale_id = str(self.router.page.params.get("id", "")).strip()
        if not sale_id.isdigit() or int(sale_id) < 1:
            self.erro = "Identificador de venda inválido."
            return
        self.venda_id = sale_id
        self.processando, self.erro, self.mensagem = True, "", ""
        try:
            auth_state = await self.get_state(AuthState)
            response = client.request(
                "GET",
                f"/vendas/{sale_id}/pagamento",
                token=auth_state.token,
            )
            if not isinstance(response, dict):
                raise XanoError("A API retornou dados inválidos para as parcelas.")
            self.parcelas = []
            await self.load_payment_methods()
        except XanoError as exc:
            self.erro = str(exc)
        finally:
            self.processando = False

    async def receive_installment(self, parcela_id: str) -> None:
        self.processando, self.erro, self.mensagem = True, "", ""
        try:
            if (
                not self.venda_id
                or not parcela_id.isdigit()
                or int(parcela_id) < 1
            ):
                raise XanoError("Venda ou parcela inválida.")
            if not self.forma_recebida_id.isdigit() or int(self.forma_recebida_id) < 1:
                raise XanoError("Selecione a forma de pagamento realmente recebida.")
            auth_state = await self.get_state(AuthState)
            client.request(
                "POST",
                f"/vendas/{self.venda_id}/parcelas/{parcela_id}/receber",
                token=auth_state.token,
                json={"forma_pagamento_id": int(self.forma_recebida_id)},
            )
            self.mensagem = "Baixa manual registrada no Xano."
            await self.load_sale()
        except XanoError as exc:
            self.erro = str(exc)
        finally:
            self.processando = False
