"""Prepare the historical ASAAS migration from its verified baseline. Never publishes.

The 14 required inputs match docs/contexto/xano-2026-11-13. Use that retained
snapshot as --source to reproduce this migration after local temporary cleanup.
Compare current remote definitions before publishing any generated patch.
"""
import argparse
import re
from pathlib import Path


def prepare(source: Path, output: Path) -> None:
    def read(name: str) -> str:
        return (source / name).read_text(encoding="utf-8-sig")

    def write(name: str, text: str) -> None:
        # Xano block assignments require line breaks, even in compact templates.
        text = re.sub(r"[ \t]+(?=(?:field_name|field_value|data|error_type|error|where|lock|return)\s*=)", "\n    ", text)
        text = text.replace("input { text id text event json payment }", "input {\n    text id\n    text event\n    json payment\n  }")
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        # Retain identities assigned by the first successful publication.
        if path.exists() and not re.search(r'guid\s*=', text):
            published_guid = re.search(r'guid\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8-sig"))
            if published_guid:
                text = text.rstrip().removesuffix("}") + f'\n  guid = "{published_guid[1]}"\n}}\n'
        path.write_text("\n".join(line.rstrip() for line in text.strip().splitlines()) + "\n", encoding="utf-8")

    def original(name: str, text: str) -> None:
        guid = re.search(r'guid\s*=\s*"([^"]+)"', read(name))
        if guid and "guid =" not in text:
            text = text.rstrip().removesuffix("}") + f'\n  guid = "{guid[1]}"\n}}\n'
        write(name, text)

    # Existing GUIDs and fields are retained. No records or environment values.
    for name in ("cliente", "venda", "asaas_cobranca", "asaas_cliente", "pagamento", "venda_parcela"):
        text = read(f"table/{name}.xs")
        if name == "cliente":
            text = text.replace("    int id", "    text asaas_sync_state?\n    int id", 1)
        if name == "venda":
            text = text.replace("    int forma_pagamento_id {", "    int forma_pagamento_id? {", 1)
            text = text.replace("    int id", '    text payment_flow?="LEGADO"\n    text asaas_request_state?\n    int id', 1)
        if name == "asaas_cobranca":
            text = text.replace("    int id", "    timestamp recebido_em?\n    text billing_type?\n    decimal valor_recebido?\n    int id", 1)
        if name == "venda_parcela":
            text = text.replace('filters=min:"1,max":24', 'filters=min:1|max:24')
        write(f"table/{name}.xs", text)
    write("table/asaas_evento.xs", '''
table asaas_evento {
  auth = false
  schema {
    int id
    text event_id
    text payment_id
    text evento
    timestamp processado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "event_id", op: "asc"}]}
  ]
}
''')
    write("function/asaas/request.xs", '''
// A chave e o ambiente sao configurados somente no Xano. Sem fallback para producao.
function "asaas/request" {
  input {
    text method
    text path
    json? body?
  }
  stack {
    precondition ($env.ASAAS_ENV == "sandbox" || $env.ASAAS_ENV == "production") {
      error_type = "badrequest"
      error = "Configure ASAAS_ENV no Xano antes de usar a integracao"
    }
    precondition ($env.ASAAS != null && $env.ASAAS != "") {
      error_type = "badrequest"
      error = "Credencial ASAAS nao configurada no Xano"
    }
    var $base { value = "https://api-sandbox.asaas.com/v3" }
    conditional {
      if ($env.ASAAS_ENV == "production") {
        var.update $base { value = "https://api.asaas.com/v3" }
      }
    }
    api.request {
      url = $base ~ $input.path
      method = $input.method
      params = $input.body ?? {}
      timeout = 20
      follow_location = false
      headers = []|push:("access_token: " ~ $env.ASAAS)|push:"Content-Type: application/json"|push:"User-Agent: AutoGestao/1.0"
    } as $http
    var $http_status { value = ($http.response.status ?? $http.status ?? 0)|to_int }
    precondition ($http_status >= 200 && $http_status < 300) {
      error_type = "badrequest"
      error = "ASAAS indisponivel ou recusou a operacao; a tentativa foi preservada para recuperacao"
    }
  }
  response = ($http.response.result ?? $http.body)
}
''')
    write("function/asaas/customer.xs", '''
// Recupera vinculo e confirma notificacoes desabilitadas antes de qualquer cobranca.
function "asaas/customer" {
  input { int cliente_id }
  stack {
    db.get cliente { field_name = "id" field_value = $input.cliente_id } as $cliente
    precondition ($cliente != null) { error_type = "notfound" error = "Cliente nao encontrado" }
    db.query asaas_cliente {
      where = $db.asaas_cliente.cliente_id == $cliente.id
      return = {type: "single"}
    } as $link
    var $customer_id { value = $link.asaas_customer_id ?? "" }
    var $reference { value = "cliente-" ~ $cliente.id }
    conditional {
      if ($customer_id == "") {
        function.run "asaas/request" {
          input = {method: "GET", path: "/customers", body: {cpfCnpj: $cliente.CPF, limit: 100}}
        } as $found
        precondition (($found.totalCount ?? 0) <= 1 && $found.hasMore != true) {
          error_type = "badrequest" error = "Mais de um cliente ASAAS para este CPF; reconciliar antes de continuar"
        }
        conditional {
          if (($found.data|count) == 1) {
            var.update $customer_id { value = ($found.data|first).id }
          }
          else {
            // A marca fica persistida se o POST sofrer timeout. Nunca reenviar cegamente.
            db.transaction {
              stack {
                db.query cliente {
                  where = $db.cliente.id == $cliente.id
                  lock = true
                  return = {type: "single"}
                } as $locked
                precondition ($locked.asaas_sync_state == null || $locked.asaas_sync_state == "") {
                  error_type = "badrequest" error = "Cadastro ASAAS com resultado incerto; reconciliar antes de nova criacao"
                }
                db.patch cliente {
                  field_name = "id" field_value = $cliente.id data = {asaas_sync_state: "SENDING"}
                } as $marked
              }
            }
            function.run "asaas/request" {
              input = {method: "POST", path: "/customers", body: {
                name: $cliente.CNome, cpfCnpj: $cliente.CPF, email: $cliente.Email,
                mobilePhone: $cliente.Telefone, externalReference: $reference, notificationDisabled: true
              }}
            } as $created
            precondition ($created.id != null) { error_type = "badrequest" error = "ASAAS nao retornou cliente; reconciliar tentativa" }
            var.update $customer_id { value = $created.id }
          }
        }
        db.transaction {
          stack {
            db.query cliente { where = $db.cliente.id == $cliente.id lock = true return = {type: "single"} } as $locked_link
            db.query asaas_cliente { where = $db.asaas_cliente.cliente_id == $cliente.id return = {type: "single"} } as $existing
            conditional {
              if ($existing == null) {
                db.add asaas_cliente { data = {cliente_id: $cliente.id, asaas_customer_id: $customer_id} } as $saved
              }
              else {
                precondition ($existing.asaas_customer_id == $customer_id) { error_type = "badrequest" error = "Vinculo ASAAS divergente" }
              }
            }
          }
        }
      }
    }
    function.run "asaas/request" {
      input = {method: "PUT", path: "/customers/" ~ $customer_id, body: {notificationDisabled: true}}
    } as $muted
    function.run "asaas/request" {
      input = {method: "GET", path: "/customers/" ~ $customer_id ~ "/notifications", body: {limit: 100}}
    } as $notifications
    precondition ($notifications.hasMore != true) { error_type = "badrequest" error = "Revisar todas as notificacoes ASAAS antes de cobrar" }
    foreach ($notifications.data) {
      each as $notification {
        function.run "asaas/request" {
          input = {method: "PUT", path: "/notifications/" ~ $notification.id, body: {
            enabled: false, emailEnabledForProvider: false, emailEnabledForCustomer: false,
            smsEnabledForProvider: false, smsEnabledForCustomer: false,
            phoneCallEnabledForCustomer: false, whatsappEnabledForCustomer: false
          }}
        } as $disabled
        precondition ($disabled.enabled == false) { error_type = "badrequest" error = "Nao foi possivel desativar notificacoes ASAAS" }
      }
    }
    function.run "asaas/request" {
      input = {method: "GET", path: "/customers/" ~ $customer_id ~ "/notifications", body: {limit: 100}}
    } as $verified
    precondition ($verified.hasMore != true && (($verified.data|filter:$$.enabled == true)|count) == 0) {
      error_type = "badrequest" error = "Notificacoes ASAAS ainda habilitadas"
    }
    db.patch cliente { field_name = "id" field_value = $cliente.id data = {asaas_sync_state: "SYNCED"} } as $synced
  }
  response = {id: $customer_id}
}
''')
    # Customer creation: recover an unfinished same-identity registration; never delete on timeout.
    name = "api/cadastros/clientes_POST.xs"
    text = read(name)
    start = text.index("    // Verificar unicidade de CPF")
    text = text[:start] + '''
    db.transaction {
      stack {
        db.query cliente { where = $db.cliente.CPF == $cpf_clean return = {type: "single"} } as $existing
        conditional {
          if ($existing != null) {
            precondition ($existing.Email == $email_norm && $existing.CNome == $input.CNome && $existing.Telefone == $input.Telefone) {
              error_type = "badrequest" error = "CPF ja cadastrado com dados diferentes"
            }
            var $novo_cliente { value = $existing }
          }
          else {
            db.query cliente { where = $db.cliente.Email == $email_norm return = {type: "single"} } as $email_existing
            precondition ($email_existing == null) { error_type = "badrequest" error = "Email ja cadastrado" }
            db.add cliente {
              data = {CNome: $input.CNome, CPF: $cpf_clean, Telefone: $input.Telefone, Email: $email_norm, created_at: now}
            } as $novo_cliente
          }
        }
      }
    }
    function.run "asaas/customer" { input = {cliente_id: $novo_cliente.id} } as $asaas_customer
  }
  response = {id: $novo_cliente.id, CNome: $novo_cliente.CNome, CPF: $novo_cliente.CPF,
              Telefone: $novo_cliente.Telefone, Email: $novo_cliente.Email, created_at: $novo_cliente.created_at}
}
'''
    original(name, text)

    # Reuse pricing/item validation, but perform all stock reads/writes in a single transaction.
    name = "api/vendas/vendas_POST.xs"
    text = read(name)
    text = text.replace("int? veiculo_id", "int? veiculo_id?").replace("int? peca_id", "int? peca_id?")
    text = re.sub(r'    int forma_pagamento_id \{.*?\n    \}\s*\n\s*int numero_parcelas[^\n]*\n\s*decimal Desconto\?[^\n]*\n', '', text, count=1, flags=re.S)
    a = text.index("    // 2. Validar forma de pagamento")
    b = text.index("    // 3. Validar perfil", a)
    text = text[:a] + text[b:]
    text = text.replace("$input.Desconto ?? 0", "0")
    text = text.replace("    // 4. Validar presenca de itens", '''
    precondition ($perfil_vendedor.Cargo == "Vendedor" || $perfil_vendedor.Cargo == "Gerente" || $perfil_vendedor.Cargo == "Administrador") {
      error_type = "accessdenied" error = "Perfil sem permissao para criar venda"
    }
    // 4. Validar presenca de itens''')
    stack = text.index("  stack {") + len("  stack {")
    end_validation = text.index("    var $centavos_por_parcela")
    validation = text[stack:end_validation]
    write_start = text.index("        db.add venda {")
    schedule = text.index("            // Criar cronograma local")
    writes = text[write_start:schedule] + "          }\n        }\n"
    writes = writes.replace("forma_pagamento_id: $input.forma_pagamento_id", 'forma_pagamento_id: null\n            payment_flow      : "ASAAS"')
    # Lock and re-read each item immediately before reserving; use current piece balance.
    locking = '''
            conditional {
              if ($proc_item.veiculo_id != null) {
                db.query veiculo { where = $db.veiculo.id == $proc_item.veiculo_id lock = true return = {type: "single"} } as $current_vehicle
                precondition ($current_vehicle.status_id == $status_veiculo_disp.id && $current_vehicle.Preco == $proc_item.preco_unit) {
                  error_type = "badrequest" error = "Veiculo alterado ou reservado por outra venda; atualize a selecao"
                }
              }
              else {
                db.query peca { where = $db.peca.id == $proc_item.peca_id lock = true return = {type: "single"} } as $current_part
                precondition ($current_part != null && $current_part.qtd_disp >= $proc_item.qtd && $current_part.PCvalor == $proc_item.preco_unit) {
                  error_type = "badrequest" error = "Estoque ou preco alterado; atualize a selecao"
                }
              }
            }
'''
    writes = writes.replace("            db.add venda_item {", locking + "            db.add venda_item {", 1)
    writes = writes.replace("$proc_item.qtd_anterior - $proc_item.qtd", "$current_part.qtd_disp - $proc_item.qtd")
    response = '''
  response = {id: $nova_venda.id, cliente_id: $nova_venda.cliente_id, vendedor_id: $nova_venda.vendedor_id,
              status_id: $nova_venda.status_id, status_descricao: $status_venda_reservado.Descricao_venda,
              Valor_bruto: $valor_bruto, Desconto: 0, Valor_final: $valor_final,
              data_venda: $nova_venda.data_venda, payment_flow: "ASAAS", itens: $itens_processados}
}
'''
    new = text[:stack] + "\n    db.transaction {\n      stack {\n" + validation + '''
        precondition ($valor_final > 0) { error_type = "badrequest" error = "Valor da venda deve ser positivo" }
''' + writes + "\n      }\n    }\n  }\n" + response
    original(name, new)

    # Existing payment response contract with explicit legacy/ASAAS discriminator.
    name = "api/vendas/vendas/id/pagamento_GET.xs"
    text = read(name)
    text = text.replace("    venda_id          : $venda.id", "    payment_flow      : ($venda.payment_flow ?? \"LEGADO\")\n    venda_id          : $venda.id")
    text = text.replace("    var $parcelas_sanitizadas {", '''    conditional {
      if ($venda.payment_flow == "ASAAS") {
        var.update $valor_recebido { value = $cobranca_asaas.valor_recebido ?? 0 }
      }
    }

    var $parcelas_sanitizadas {''')
    text = text.replace("    // Buscar descricao do status", '''
    precondition ($perfil.Cargo == "Vendedor" || $perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador") {
      error_type = "accessdenied" error = "Perfil sem permissao para consultar pagamento"
    }
    // Buscar descricao do status''')
    original(name, text)
    # Close the manual write path for new sales even if an old client calls it directly.
    name = "api/vendas/vendas/id/parcelas/parcela_id/receber_POST.xs"
    text = read(name)
    pos = text.index("    db.get venda_parcela")
    text = text[:pos] + '''
    precondition ($venda.payment_flow != "ASAAS") {
      error_type = "badrequest" error = "Recebimentos desta venda sao confirmados pelo ASAAS"
    }
''' + text[pos:]
    original(name, text)

    # Exact, allow-listed permissions are shared by link/retrieval routes.
    authorize = '''
    db.get venda { field_name = "id" field_value = $input.id } as $venda
    precondition ($venda != null) { error_type = "notfound" error = "Venda nao encontrada" }
    db.get user { field_name = "id" field_value = $auth.id } as $user
    db.get perfil { field_name = "id" field_value = $user.perfil_id } as $perfil
    precondition ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador" || ($perfil.Cargo == "Vendedor" && $venda.vendedor_id == $auth.id)) {
      error_type = "accessdenied" error = "Sem permissao para esta venda"
    }
'''
    name = "api/vendas/vendas/id/link_pagamento_POST.xs"
    original(name, '''
// Gera ou recupera fatura ASAAS persistida, com escopo por perfil e protecao de tentativas ambiguas.
query "vendas/{id}/link-pagamento" verb=POST {
  api_group = "vendas"
  auth = "user"
  input { int id }
  stack {
''' + authorize + '''
    precondition ($venda.payment_flow == "ASAAS") { error_type = "badrequest" error = "Venda legada usa seu historico original" }
    db.get status_venda { field_name = "id" field_value = $venda.status_id } as $status
    precondition ($status.Descricao_venda == "Reservado" || $status.Descricao_venda == "Paga" || $status.Descricao_venda == "Concluída") {
      error_type = "badrequest" error = "Venda nao permite gerar cobranca"
    }
    db.query asaas_cobranca { where = $db.asaas_cobranca.venda_id == $venda.id return = {type: "single"} } as $cobranca
    conditional {
      if ($cobranca == null) {
        precondition ($status.Descricao_venda == "Reservado") { error_type = "badrequest" error = "Venda nao permite nova cobranca" }
        var $due { value = now|transform_timestamp:"+30 days":"America/Sao_Paulo"|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
        // Claim the lookup phase before any external request. Cancellation cannot
        // release stock while customer/charge lookup or creation is in progress.
        db.transaction {
          stack {
            db.query venda { where = $db.venda.id == $venda.id lock = true return = {type: "single"} } as $lookup_sale
            precondition ($lookup_sale.status_id == $venda.status_id && $lookup_sale.payment_flow == "ASAAS") {
              error_type = "badrequest" error = "Venda alterada; atualize antes de gerar o link"
            }
            conditional {
              if ($lookup_sale.asaas_request_state == null || $lookup_sale.asaas_request_state == "") {
                db.patch venda { field_name = "id" field_value = $venda.id data = {asaas_request_state: "LOOKUP"} } as $lookup_started
              }
            }
          }
        }
        function.run "asaas/customer" { input = {cliente_id: $venda.cliente_id} } as $customer
        var $reference { value = "venda-" ~ $venda.id }
        function.run "asaas/request" {
          input = {method: "GET", path: "/payments", body: {externalReference: $reference, customer: $customer.id, limit: 100}}
        } as $found
        precondition (($found.data|count) <= 1 && $found.hasMore != true) { error_type = "badrequest" error = "Cobrancas divergentes; reconciliar antes de continuar" }
        conditional {
          if (($found.data|count) == 1) {
            var $payment { value = $found.data|first }
          }
          else {
            db.transaction {
              stack {
                db.query venda { where = $db.venda.id == $venda.id lock = true return = {type: "single"} } as $locked
                precondition ($locked.status_id == $venda.status_id && $locked.asaas_request_state == "LOOKUP") {
                  error_type = "badrequest" error = "Tentativa anterior em andamento ou com resultado incerto; reconciliar no ASAAS"
                }
                db.patch venda { field_name = "id" field_value = $venda.id data = {asaas_request_state: "SENDING"} } as $marked
              }
            }
            function.run "asaas/request" {
              input = {method: "POST", path: "/payments", body: {
                customer: $customer.id, billingType: "UNDEFINED", value: $venda.Valor_final,
                dueDate: $due, description: "Venda #" ~ $venda.id, externalReference: $reference
              }}
            } as $payment
          }
        }
        precondition ($payment.id != null && $payment.invoiceUrl != null && $payment.customer == $customer.id && $payment.value == $venda.Valor_final && $payment.deleted != true) {
          error_type = "badrequest" error = "Cobranca ASAAS invalida; reconciliar a tentativa preservada"
        }
        db.transaction {
          stack {
            db.query venda { where = $db.venda.id == $venda.id lock = true return = {type: "single"} } as $locked_save
            precondition ($locked_save.status_id == $venda.status_id && $locked_save.payment_flow == "ASAAS") {
              error_type = "badrequest" error = "Venda alterada durante geracao; reconciliar cobranca sem criar outra"
            }
            db.query asaas_cobranca { where = $db.asaas_cobranca.venda_id == $venda.id return = {type: "single"} } as $existing
            conditional {
              if ($existing == null) {
                db.add asaas_cobranca { data = {
                  venda_id: $venda.id, asaas_payment_id: $payment.id, invoice_url: $payment.invoiceUrl,
                  status: $payment.status, due_date: $payment.dueDate
                }} as $cobranca
              }
              else {
                precondition ($existing.asaas_payment_id == $payment.id) { error_type = "badrequest" error = "Cobranca divergente" }
                var $cobranca { value = $existing }
              }
            }
            db.patch venda { field_name = "id" field_value = $venda.id data = {asaas_request_state: "LINKED"} } as $linked
          }
        }
      }
    }
  }
  response = {venda_id: $venda.id, invoice_url: $cobranca.invoice_url, status: $cobranca.status, due_date: $cobranca.due_date}
}
''')
    # Synchronization fetches current external state, not the possibly stale webhook body.
    write("function/asaas/reconcile.xs", '''
function "asaas/reconcile" {
  input { text payment_id }
  stack {
    db.query asaas_cobranca { where = $db.asaas_cobranca.asaas_payment_id == $input.payment_id return = {type: "single"} } as $cobranca
    precondition ($cobranca != null) { error_type = "badrequest" error = "Cobranca ainda nao vinculada; tentar evento novamente" }
    db.transaction {
      stack {
        db.query venda { where = $db.venda.id == $cobranca.venda_id lock = true return = {type: "single"} } as $venda
        precondition ($venda.payment_flow == "ASAAS") { error_type = "badrequest" error = "Cobranca fora do fluxo ASAAS" }
        function.run "asaas/request" { input = {method: "GET", path: "/payments/" ~ $input.payment_id} } as $payment
        db.query asaas_cliente { where = $db.asaas_cliente.cliente_id == $venda.cliente_id return = {type: "single"} } as $customer
        precondition ($payment.id == $input.payment_id && $payment.customer == $customer.asaas_customer_id && $payment.value == $venda.Valor_final) {
          error_type = "badrequest" error = "Cobranca divergente da venda"
        }
        var $external_status { value = ($payment.deleted == true ? "DELETED" : $payment.status) }
        var $received { value = $external_status == "RECEIVED" || $external_status == "CONFIRMED" || $external_status == "RECEIVED_IN_CASH" }
        var $received_at { value = null }
        conditional {
          if ($received) {
            precondition ($payment.paymentDate != null || $payment.clientPaymentDate != null || $payment.confirmedDate != null) {
              error_type = "badrequest" error = "Pagamento sem data autoritativa; reconciliar no ASAAS"
            }
            var.update $received_at { value = ($payment.paymentDate ?? $payment.clientPaymentDate ?? $payment.confirmedDate)|to_timestamp }
          }
        }
        db.patch asaas_cobranca { field_name = "id" field_value = $cobranca.id data = {
          status: $external_status, billing_type: $payment.billingType, recebido_em: $received_at,
          valor_recebido: ($received ? $payment.value : 0)
        }} as $updated
        db.query pagamento { where = $db.pagamento.asaas_payment_id == $payment.id return = {type: "single"} } as $ledger
        conditional {
          if ($ledger == null) {
            db.add pagamento { data = {
              venda_id: $venda.id, asaas_payment_id: $payment.id, status_asaas: $external_status,
              billing_type: $payment.billingType, valor: $payment.value, valor_liquido: $payment.netValue,
              recebido_em: $received_at, updated_at: now
            }} as $saved_ledger
          }
          else {
            db.patch pagamento { field_name = "id" field_value = $ledger.id data = {
              status_asaas: $external_status, billing_type: $payment.billingType, valor: $payment.value,
              valor_liquido: $payment.netValue, recebido_em: $received_at, updated_at: now
            }} as $saved_ledger
          }
        }
        conditional {
          if ($received) {
            db.get status_venda { field_name = "id" field_value = $venda.status_id } as $current_status
            precondition ($current_status.Descricao_venda != "Cancelada") { error_type = "badrequest" error = "Pagamento de venda cancelada exige reconciliacao" }
            db.query status_venda { where = $db.status_venda.Descricao_venda == "Paga" return = {type: "single"} } as $paid_status
            precondition ($paid_status != null) { error_type = "badrequest" error = "Status Paga nao configurado" }
            var $method_name { value = "" }
            conditional {
              if ($payment.billingType == "PIX") { var.update $method_name { value = "pix" } }
              elseif ($payment.billingType == "BOLETO") { var.update $method_name { value = "boleto" } }
              elseif ($payment.billingType == "CREDIT_CARD") { var.update $method_name { value = "cartão de crédito" } }
            }
            db.query forma_pagamento { return = {type: "list"} } as $methods
            var $matching { value = $methods|filter:(($$.Metodo|trim|to_lower) == $method_name || ($method_name == "boleto" && ($$.Metodo|trim|to_lower) == "boleto bancário")) }
            var $method_id { value = null }
            conditional {
              if (($matching|count) == 1) { var.update $method_id { value = ($matching|first).id } }
            }
            conditional {
              if ($current_status.Descricao_venda == "Reservado") {
                db.patch venda { field_name = "id" field_value = $venda.id data = {status_id: $paid_status.id, forma_pagamento_id: $method_id} } as $paid
              }
            }
          }
        }
      }
    }
  }
  response = {status: $external_status}
}
''')
    # The header is read from the request, never trusted from the JSON input.
    name = "api/asaas_webhooks/webhooks/asaas/pagamentos_POST.xs"
    original(name, '''
// Autentica eventos ASAAS, consulta o estado atual e persiste recebimento sem duplicacao.
query "webhooks/asaas/pagamentos" verb=POST {
  api_group = "asaas_webhooks"
  input { text id text event json payment }
  stack {
    var $headers { value = $env.$http_headers }
    var $token_header { value = "asaas-access-token: " ~ $env.ASAAS_WEBHOOK_TOKEN }
    var $header_token { value = ($headers|get:"asaas-access-token") ?? ($headers|get:"Asaas-Access-Token") ?? "" }
    precondition ($env.ASAAS_WEBHOOK_TOKEN != null && ($env.ASAAS_WEBHOOK_TOKEN|strlen) >= 32 && ($header_token == $env.ASAAS_WEBHOOK_TOKEN || ($headers|contains:$token_header))) {
      error_type = "unauthorized" error = "Webhook nao autorizado"
    }
    precondition ($input.id != "" && $input.payment.id != null) { error_type = "badrequest" error = "Evento invalido" }
    db.query asaas_evento { where = $db.asaas_evento.event_id == $input.id return = {type: "single"} } as $existing
    conditional {
      if ($existing == null) {
        db.transaction {
          stack {
            function.run "asaas/reconcile" { input = {payment_id: $input.payment.id} } as $state
            // Reconcile locks the sale. Duplicate insert rolls back all writes on contention.
            db.query asaas_evento { where = $db.asaas_evento.event_id == $input.id return = {type: "single"} } as $repeated
            conditional {
              if ($repeated == null) {
                db.add asaas_evento { data = {event_id: $input.id, payment_id: $input.payment.id, evento: $input.event, processado_em: now} } as $saved
              }
            }
          }
        }
      }
    }
  }
  response = {received: true}
}
''')
    # Payment GET only reads stored data. Reconciliation is performed by webhook.
    # Reconcile existing billing in cancellation before releasing any stock.
    name = "api/vendas/vendas/id/cancelar_POST.xs"
    text = read(name)
    pos = text.index("    conditional {\n      if ($status_atual.Descricao_venda")
    text = text[:pos] + '''
    conditional {
      if ($venda.payment_flow == "ASAAS") {
        db.query asaas_cobranca { where = $db.asaas_cobranca.venda_id == $venda.id return = {type: "single"} } as $billing
        conditional {
          if ($billing != null) {
            function.run "asaas/reconcile" { input = {payment_id: $billing.asaas_payment_id} } as $live_state
            precondition ($live_state.status == "PENDING" || $live_state.status == "OVERDUE" || $live_state.status == "DELETED") {
              error_type = "badrequest" error = "Cobranca recebida ou em processamento; nao liberar estoque"
            }
            conditional {
              if ($live_state.status != "DELETED") {
                function.run "asaas/request" { input = {method: "DELETE", path: "/payments/" ~ $billing.asaas_payment_id} } as $deleted
                precondition ($deleted.deleted == true) { error_type = "badrequest" error = "Cancelamento ASAAS nao confirmado; reserva preservada" }
              }
            }
            db.patch asaas_cobranca { field_name = "id" field_value = $billing.id data = {status: "DELETED"} } as $cancelled_billing
          }
          else {
            precondition ($venda.asaas_request_state == null || $venda.asaas_request_state == "") {
              error_type = "badrequest" error = "Tentativa de cobranca incerta; recuperar antes de cancelar"
            }
          }
        }
      }
    }
''' + text[pos:]
    # Serialize cancellation against creation/link and payment processing, recheck state.
    token = "        db.transaction {\n          stack {"
    text = text.replace(token, token + '''
            db.query venda { where = $db.venda.id == $venda.id lock = true return = {type: "single"} } as $locked_cancel
            precondition ($locked_cancel.status_id == $status_atual.id) { error_type = "badrequest" error = "Venda alterada; atualize antes de cancelar" }
            precondition ($locked_cancel.asaas_request_state != "SENDING" && $locked_cancel.asaas_request_state != "LOOKUP") { error_type = "badrequest" error = "Cobranca em andamento; reserva preservada" }
            conditional {
              if ($locked_cancel.payment_flow == "ASAAS") {
                db.query asaas_cobranca { where = $db.asaas_cobranca.venda_id == $venda.id return = {type: "single"} } as $billing_locked
                precondition (($billing_locked != null && $billing_locked.status == "DELETED") || ($billing_locked == null && ($locked_cancel.asaas_request_state == null || $locked_cancel.asaas_request_state == ""))) {
                  error_type = "badrequest" error = "Cobranca criada durante cancelamento; recuperar antes de liberar estoque"
                }
              }
            }
''', 1)
    text = text.replace('''                    db.get peca {
                      field_name = "id"
                      field_value = $item_canc.peca_id
                    } as $peca_item''', '''                    db.query peca {
                      where = $db.peca.id == $item_canc.peca_id
                      lock = true
                      return = {type: "single"}
                    } as $peca_item''')
    text = text.replace('''                  if ($item_canc.veiculo_id != null) {
                    db.patch veiculo''', '''                  if ($item_canc.veiculo_id != null) {
                    db.query veiculo {
                      where = $db.veiculo.id == $item_canc.veiculo_id
                      lock = true
                      return = {type: "single"}
                    } as $veiculo_cancelar
                    db.patch veiculo''')
    original(name, text)


    # Revenue is backed by actual receipt timestamps, independently of sale creation date.
    name = "api/gerenciamento/indicadores_GET.xs"
    text = read(name)
    query_start = text.index("    db.query venda {", text.index("    // 9."))
    query_end = text.index("} as $vendas_filtradas", query_start) + len("} as $vendas_filtradas")
    sale_filter = "$db.venda.vendedor_id ==? $vendedor_filtro && $db.venda.status_id ==? $parsed_status_id && $db.venda.forma_pagamento_id ==? $parsed_forma_pagamento_id"
    sale_queries = "    var $vendas_filtradas { value = [] }\n    conditional {\n"
    for condition, dates in (
        ("if ($parsed_data_inicio == null && $parsed_data_fim == null)", ""),
        ("elseif ($parsed_data_inicio != null && $parsed_data_fim == null)", " && $db.venda.data_venda >= $parsed_data_inicio"),
        ("elseif ($parsed_data_inicio == null && $parsed_data_fim != null)", " && $db.venda.data_venda <= $parsed_data_fim"),
        ("else", " && $db.venda.data_venda >= $parsed_data_inicio && $db.venda.data_venda <= $parsed_data_fim"),
    ):
        sale_queries += f'''      {condition} {{
        db.query venda {{
          where = {sale_filter}{dates}
          sort = {{id: "desc"}}
          return = {{type: "list"}}
        }} as $filtered_sales
        var.update $vendas_filtradas {{ value = $filtered_sales }}
      }}
'''
    text = text[:query_start] + sale_queries + "    }" + text[query_end:]
    item_start = text.index("    db.query venda_item {", text.index("    // 14."))
    item_end = text.index("} as $itens_das_vendas", item_start) + len("} as $itens_das_vendas")
    text = text[:item_start] + '''    var $itens_das_vendas { value = [] }
    conditional {
      if (($vendas_filtradas|count) > 0) {
        var $sale_ids { value = $vendas_filtradas|map:$$.id }
        db.query venda_item {
          where = $db.venda_item.venda_id in $sale_ids && ($parsed_tipo_item == null || $parsed_tipo_item == "todos" || ($parsed_tipo_item == "veiculo" && $db.venda_item.veiculo_id != null) || ($parsed_tipo_item == "peca" && $db.venda_item.peca_id != null))
          return = {type: "list"}
        } as $filtered_items
        var.update $itens_das_vendas { value = $filtered_items }
      }
    }''' + text[item_end:]
    start = text.index("    // 10. Processamento direto")
    end = text.index("    // 11. Agregacao vendas_por_periodo", start)
    finance = '''
    // Recebimentos ASAAS e historico manual sao fontes separadas, nunca somadas duas vezes.
    var $vendas_concluidas { value = 0 }
    foreach ($vendas_filtradas) {
      each as $sale {
        db.get status_venda { field_name = "id" field_value = $sale.status_id } as $sale_status
        conditional {
          if ($sale_status.Descricao_venda == "Concluída" || $sale_status.Descricao_venda == "Concluida") {
            var.update $vendas_concluidas { value = $vendas_concluidas + 1 }
          }
        }
      }
    }
'''
    for table, flow, alias, state, amount in (
        ("pagamento", '== "ASAAS"', "asaas_receipts", '($db.pagamento.status_asaas == "RECEIVED" || $db.pagamento.status_asaas == "CONFIRMED" || $db.pagamento.status_asaas == "RECEIVED_IN_CASH")', "valor"),
        ("venda_parcela", '!= "ASAAS"', "legacy_receipts", '$db.venda_parcela.status == "RECEBIDA"', "valor"),
    ):
        # A null legacy discriminator is the pre-migration value. COALESCE through a
        # DB field filter is avoided; added schema default handles existing records.
        flow_where = '$db.venda.payment_flow == "ASAAS"' if table == "pagamento" else '($db.venda.payment_flow == null || $db.venda.payment_flow != "ASAAS")'
        base = f'''{flow_where} && {state} && $db.{table}.recebido_em != null && $db.{table}.{amount} > 0 && $db.status_venda.Descricao_venda != "Cancelada" && $db.status_venda.Descricao_venda != "Expirada" && $db.venda.vendedor_id ==? $vendedor_filtro && $db.venda.status_id ==? $parsed_status_id && $db.venda.forma_pagamento_id ==? $parsed_forma_pagamento_id'''
        finance += f"    var ${alias} {{ value = [] }}\n    conditional {{\n"
        branches = (
            ("if ($parsed_data_inicio == null && $parsed_data_fim == null)", ""),
            ("elseif ($parsed_data_inicio != null && $parsed_data_fim == null)", f" && $db.{table}.recebido_em >= $parsed_data_inicio"),
            ("elseif ($parsed_data_inicio == null && $parsed_data_fim != null)", f" && $db.{table}.recebido_em <= $parsed_data_fim"),
            ("else", f" && $db.{table}.recebido_em >= $parsed_data_inicio && $db.{table}.recebido_em <= $parsed_data_fim"),
        )
        for condition, date_where in branches:
            finance += f'''
      {condition} {{
        db.query {table} {{
          join = {{
            venda: {{table: "venda", where: $db.{table}.venda_id == $db.venda.id}}
            status_venda: {{table: "status_venda", where: $db.venda.status_id == $db.status_venda.id}}
          }}
          where = {base}{date_where}
          return = {{type: "list"}}
        }} as $receipts
        var.update ${alias} {{ value = $receipts }}
      }}
'''
        finance += "    }\n"
    finance += '''
    var $vendas_pagas_ids { value = (($asaas_receipts|map:$$.venda_id)|merge:($legacy_receipts|map:$$.venda_id))|unique }
    var $vendas_pagas_count { value = $vendas_pagas_ids|count }
    var $soma_valor_final_vendas_pagas { value = (($asaas_receipts|map:$$.valor)|sum) + (($legacy_receipts|map:$$.valor)|sum) }
    var $valor_liquido_recebido_periodo { value = (($asaas_receipts|map:($$.valor_liquido ?? $$.valor))|sum) + (($legacy_receipts|map:$$.valor)|sum) }
    var $ticket_medio_vendas_pagas { value = 0 }
    conditional {
      if ($vendas_pagas_count > 0) { var.update $ticket_medio_vendas_pagas { value = $soma_valor_final_vendas_pagas / $vendas_pagas_count } }
    }
    var $diagnostico_parcelas { value = {fonte: "ASAAS e historico manual separado", vendas_pagas_distintas: $vendas_pagas_count} }
'''
    text = text[:start] + finance + text[end:]
    original(name, text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output)
