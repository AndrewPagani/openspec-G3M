// Webhook legado desativado; eventos externos não alteram vendas nem parcelas
query "webhooks/asaas/pagamentos" verb=POST {
  api_group = "asaas_webhooks"

  input {
    text id filters=trim
    text event filters=trim
    json payment
  }

  stack {
    precondition (false) {
      error_type = "badrequest"
      error = "Webhook de pagamentos desativado; registre recebimentos manualmente no Xano"
    }
  }

  response = null
  guid = "Kjx_lWW-gc7VSfhS1ocjRG1Cmc8"
}