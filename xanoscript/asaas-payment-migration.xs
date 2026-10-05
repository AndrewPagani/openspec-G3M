// Migração ASAAS publicada no workspace 147643.
// Os campos ausentes em documentos antigos são preservados para atualização por GUID.

table cliente {
  auth = false

  schema {
    int id
    text CNome filters=trim
    text CPF filters=trim
    text Telefone filters=trim
    email Email? filters=trim|lower
    text asaas_customer_id?
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "CPF", op: "asc"}]}
    {type: "btree|unique", field: [{name: "Email", op: "asc"}]}
    {type: "btree|unique", field: [{name: "asaas_customer_id", op: "asc"}]}
  ]

  guid = "0NP1T4qC0DYOFdsRZuVyEJt3BpE"
}

---

table venda {
  auth = false

  schema {
    int id
    int cliente_id { table = "cliente" }
    int vendedor_id { table = "user" }
    int forma_pagamento_id { table = "forma_pagamento" }
    int status_id { table = "status_venda" }
    decimal Valor_bruto filters=min:0
    decimal Desconto?=0 filters=min:0
    decimal Valor_final filters=min:0
    timestamp data_venda?=now
    text asaas_payment_link_id?
    text asaas_payment_link_url?
    timestamp payment_link_expires_at?
    int payment_installment_limit?
    text cancel_reason?
    timestamp cancelled_at?
    text payment_email_status?
    timestamp payment_email_requested_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "asaas_payment_link_id", op: "asc"}]}
    {type: "btree", field: [{name: "data_venda", op: "desc"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
    {type: "btree", field: [{name: "vendedor_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]

  guid = "k9m1bxhQIWw6r3vqaOJc89be__M"
}

---

table pagamento {
  auth = false

  schema {
    int id
    int venda_id { table = "venda" }
    text asaas_payment_id
    text asaas_customer_id?
    text asaas_installment_id?
    text status_asaas
    text billing_type?
    decimal valor filters=min:0
    decimal valor_liquido? filters=min:0
    decimal taxa? filters=min:0
    int numero_parcela?
    int total_parcelas?
    timestamp vencimento?
    timestamp recebido_em?
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "asaas_payment_id", op: "asc"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_asaas", op: "asc"}]}
    {type: "btree", field: [{name: "recebido_em", op: "desc"}]}
  ]

  guid = "BUOGUNZjCVeYKnhpOSrxXJUHsl0"
}

---

table pagamento_evento {
  auth = false

  schema {
    int id
    text asaas_event_id
    text asaas_payment_id
    text evento
    timestamp recebido_em?=now
    timestamp processado_em?
    text status_processamento
    text erro_resumido?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "asaas_event_id", op: "asc"}]}
    {type: "btree", field: [{name: "asaas_payment_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_processamento", op: "asc"}]}
  ]

  guid = "3EbjyQ4krYOXyv8sD3L1_K6UGpI"
}
