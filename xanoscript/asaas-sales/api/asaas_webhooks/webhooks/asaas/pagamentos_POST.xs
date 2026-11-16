// Autentica eventos ASAAS, consulta o estado atual e persiste recebimento sem duplicacao.
query "webhooks/asaas/pagamentos" verb=POST {
  api_group = "asaas_webhooks"
  input {
    text id
    text event
    json payment
  }
  stack {
    var $headers { value = $env.$http_headers }
    var $token_header { value = "asaas-access-token: " ~ $env.ASAAS_WEBHOOK_TOKEN }
    var $header_token { value = ($headers|get:"asaas-access-token") ?? ($headers|get:"Asaas-Access-Token") ?? "" }
    precondition ($env.ASAAS_WEBHOOK_TOKEN != null && ($env.ASAAS_WEBHOOK_TOKEN|strlen) >= 32 && ($header_token == $env.ASAAS_WEBHOOK_TOKEN || ($headers|contains:$token_header))) {

    error_type = "unauthorized"
    error = "Webhook nao autorizado"
    }
    precondition ($input.id != "" && $input.payment.id != null) {
    error_type = "badrequest"
    error = "Evento invalido" }
    db.query asaas_evento {
    where = $db.asaas_evento.event_id == $input.id
    return = {type: "single"} } as $existing
    conditional {
      if ($existing == null) {
        db.transaction {
          stack {
            function.run "asaas/reconcile" { input = {payment_id: $input.payment.id} } as $state
            // Reconcile locks the sale. Duplicate insert rolls back all writes on contention.
            db.query asaas_evento {
    where = $db.asaas_evento.event_id == $input.id
    return = {type: "single"} } as $repeated
            conditional {
              if ($repeated == null) {
                db.add asaas_evento {
    data = {event_id: $input.id, payment_id: $input.payment.id, evento: $input.event, processado_em: now} } as $saved
              }
            }
          }
        }
      }
    }
  }
  response = {received: true}

  guid = "Kjx_lWW-gc7VSfhS1ocjRG1Cmc8"
}
