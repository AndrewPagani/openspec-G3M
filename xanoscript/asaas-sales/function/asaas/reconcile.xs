function "asaas/reconcile" {
  input { text payment_id }
  stack {
    db.query asaas_cobranca {
    where = $db.asaas_cobranca.asaas_payment_id == $input.payment_id
    return = {type: "single"} } as $cobranca
    precondition ($cobranca != null) {
    error_type = "badrequest"
    error = "Cobranca ainda nao vinculada; tentar evento novamente" }
    db.transaction {
      stack {
        db.query venda {
    where = $db.venda.id == $cobranca.venda_id
    lock = true
    return = {type: "single"} } as $venda
        precondition ($venda.payment_flow == "ASAAS") {
    error_type = "badrequest"
    error = "Cobranca fora do fluxo ASAAS" }
        function.run "asaas/request" { input = {method: "GET", path: "/payments/" ~ $input.payment_id} } as $payment
        db.query asaas_cliente {
    where = $db.asaas_cliente.cliente_id == $venda.cliente_id
    return = {type: "single"} } as $customer
        precondition ($payment.id == $input.payment_id && $payment.customer == $customer.asaas_customer_id && $payment.value == $venda.Valor_final) {

    error_type = "badrequest"
    error = "Cobranca divergente da venda"
        }
        var $external_status { value = ($payment.deleted == true ? "DELETED" : $payment.status) }
        var $received { value = $external_status == "RECEIVED" || $external_status == "CONFIRMED" || $external_status == "RECEIVED_IN_CASH" }
        var $received_at { value = null }
        conditional {
          if ($received) {
            precondition ($payment.paymentDate != null || $payment.clientPaymentDate != null || $payment.confirmedDate != null) {

    error_type = "badrequest"
    error = "Pagamento sem data autoritativa; reconciliar no ASAAS"
            }
            var.update $received_at { value = ($payment.paymentDate ?? $payment.clientPaymentDate ?? $payment.confirmedDate)|to_timestamp }
          }
        }
        db.patch asaas_cobranca {
    field_name = "id"
    field_value = $cobranca.id
    data = {
          status: $external_status, billing_type: $payment.billingType, recebido_em: $received_at,
          valor_recebido: ($received ? $payment.value : 0)
        }} as $updated
        db.query pagamento {
    where = $db.pagamento.asaas_payment_id == $payment.id
    return = {type: "single"} } as $ledger
        conditional {
          if ($ledger == null) {
            db.add pagamento {
    data = {
              venda_id: $venda.id, asaas_payment_id: $payment.id, status_asaas: $external_status,
              billing_type: $payment.billingType, valor: $payment.value, valor_liquido: $payment.netValue,
              recebido_em: $received_at, updated_at: now
            }} as $saved_ledger
          }
          else {
            db.patch pagamento {
    field_name = "id"
    field_value = $ledger.id
    data = {
              status_asaas: $external_status, billing_type: $payment.billingType, valor: $payment.value,
              valor_liquido: $payment.netValue, recebido_em: $received_at, updated_at: now
            }} as $saved_ledger
          }
        }
        conditional {
          if ($received) {
            db.get status_venda {
    field_name = "id"
    field_value = $venda.status_id } as $current_status
            precondition ($current_status.Descricao_venda != "Cancelada") {
    error_type = "badrequest"
    error = "Pagamento de venda cancelada exige reconciliacao" }
            db.query status_venda {
    where = $db.status_venda.Descricao_venda == "Paga"
    return = {type: "single"} } as $paid_status
            precondition ($paid_status != null) {
    error_type = "badrequest"
    error = "Status Paga nao configurado" }
            var $method_name { value = "" }
            conditional {
              if ($payment.billingType == "PIX") { var.update $method_name { value = "pix" } }
              elseif ($payment.billingType == "BOLETO") { var.update $method_name { value = "boleto" } }
              elseif ($payment.billingType == "CREDIT_CARD") { var.update $method_name { value = "cartão de crédito" } }
            }
            db.query forma_pagamento {
    return = {type: "list"} } as $methods
            var $matching { value = $methods|filter:(($$.Metodo|trim|to_lower) == $method_name || ($method_name == "boleto" && ($$.Metodo|trim|to_lower) == "boleto bancário")) }
            var $method_id { value = null }
            conditional {
              if (($matching|count) == 1) { var.update $method_id { value = ($matching|first).id } }
            }
            conditional {
              if ($current_status.Descricao_venda == "Reservado") {
                db.patch venda {
    field_name = "id"
    field_value = $venda.id
    data = {status_id: $paid_status.id, forma_pagamento_id: $method_id} } as $paid
              }
            }
          }
        }
      }
    }
  }
  response = {status: $external_status}

  guid = "0SXCWXSCp0ZMGTEHyA9nsKPaizo"
}
