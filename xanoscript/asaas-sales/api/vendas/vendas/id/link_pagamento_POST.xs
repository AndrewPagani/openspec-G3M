// Gera ou recupera fatura ASAAS persistida, com escopo por perfil e protecao de tentativas ambiguas.
query "vendas/{id}/link-pagamento" verb=POST {
  api_group = "vendas"
  auth = "user"
  input { int id }
  stack {

    db.get venda {
    field_name = "id"
    field_value = $input.id } as $venda
    precondition ($venda != null) {
    error_type = "notfound"
    error = "Venda nao encontrada" }
    db.get user {
    field_name = "id"
    field_value = $auth.id } as $user
    db.get perfil {
    field_name = "id"
    field_value = $user.perfil_id } as $perfil
    precondition ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador" || ($perfil.Cargo == "Vendedor" && $venda.vendedor_id == $auth.id)) {

    error_type = "accessdenied"
    error = "Sem permissao para esta venda"
    }

    precondition ($venda.payment_flow == "ASAAS") {
    error_type = "badrequest"
    error = "Venda legada usa seu historico original" }
    db.get status_venda {
    field_name = "id"
    field_value = $venda.status_id } as $status
    precondition ($status.Descricao_venda == "Reservado" || $status.Descricao_venda == "Paga" || $status.Descricao_venda == "Concluída") {

    error_type = "badrequest"
    error = "Venda nao permite gerar cobranca"
    }
    db.query asaas_cobranca {
    where = $db.asaas_cobranca.venda_id == $venda.id
    return = {type: "single"} } as $cobranca
    conditional {
      if ($cobranca == null) {
        precondition ($status.Descricao_venda == "Reservado") {
    error_type = "badrequest"
    error = "Venda nao permite nova cobranca" }
        var $due { value = now|transform_timestamp:"+30 days":"America/Sao_Paulo"|format_timestamp:"Y-m-d":"America/Sao_Paulo" }
        // Claim the lookup phase before any external request. Cancellation cannot
        // release stock while customer/charge lookup or creation is in progress.
        db.transaction {
          stack {
            db.query venda {
    where = $db.venda.id == $venda.id
    lock = true
    return = {type: "single"} } as $lookup_sale
            precondition ($lookup_sale.status_id == $venda.status_id && $lookup_sale.payment_flow == "ASAAS") {

    error_type = "badrequest"
    error = "Venda alterada; atualize antes de gerar o link"
            }
            conditional {
              if ($lookup_sale.asaas_request_state == null || $lookup_sale.asaas_request_state == "") {
                db.patch venda {
    field_name = "id"
    field_value = $venda.id
    data = {asaas_request_state: "LOOKUP"} } as $lookup_started
              }
            }
          }
        }
        function.run "asaas/customer" { input = {cliente_id: $venda.cliente_id} } as $customer
        var $reference { value = "venda-" ~ $venda.id }
        function.run "asaas/request" {
          input = {method: "GET", path: "/payments", body: {externalReference: $reference, customer: $customer.id, limit: 100}}
        } as $found
        precondition (($found.data|count) <= 1 && $found.hasMore != true) {
    error_type = "badrequest"
    error = "Cobrancas divergentes; reconciliar antes de continuar" }
        conditional {
          if (($found.data|count) == 1) {
            var $payment { value = $found.data|first }
          }
          else {
            db.transaction {
              stack {
                db.query venda {
    where = $db.venda.id == $venda.id
    lock = true
    return = {type: "single"} } as $locked
                precondition ($locked.status_id == $venda.status_id && $locked.asaas_request_state == "LOOKUP") {

    error_type = "badrequest"
    error = "Tentativa anterior em andamento ou com resultado incerto; reconciliar no ASAAS"
                }
                db.patch venda {
    field_name = "id"
    field_value = $venda.id
    data = {asaas_request_state: "SENDING"} } as $marked
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

    error_type = "badrequest"
    error = "Cobranca ASAAS invalida; reconciliar a tentativa preservada"
        }
        db.transaction {
          stack {
            db.query venda {
    where = $db.venda.id == $venda.id
    lock = true
    return = {type: "single"} } as $locked_save
            precondition ($locked_save.status_id == $venda.status_id && $locked_save.payment_flow == "ASAAS") {

    error_type = "badrequest"
    error = "Venda alterada durante geracao; reconciliar cobranca sem criar outra"
            }
            db.query asaas_cobranca {
    where = $db.asaas_cobranca.venda_id == $venda.id
    return = {type: "single"} } as $existing
            conditional {
              if ($existing == null) {
                db.add asaas_cobranca {
    data = {
                  venda_id: $venda.id, asaas_payment_id: $payment.id, invoice_url: $payment.invoiceUrl,
                  status: $payment.status, due_date: $payment.dueDate
                }} as $cobranca
              }
              else {
                precondition ($existing.asaas_payment_id == $payment.id) {
    error_type = "badrequest"
    error = "Cobranca divergente" }
                var $cobranca { value = $existing }
              }
            }
            db.patch venda {
    field_name = "id"
    field_value = $venda.id
    data = {asaas_request_state: "LINKED"} } as $linked
          }
        }
      }
    }
  }
  response = {venda_id: $venda.id, invoice_url: $cobranca.invoice_url, status: $cobranca.status, due_date: $cobranca.due_date}

  guid = "DQL8iqkM9CRlIOHbmZPUgqCXJdI"
}
