table venda {
  auth = false

  schema {
    int id
    int cliente_id {
      table = "cliente"
    }
  
    int vendedor_id {
      table = "user"
    }
  
    int forma_pagamento_id {
      table = "forma_pagamento"
    }
  
    int status_id {
      table = "status_venda"
    }
  
    decimal Valor_bruto filters=min:0
    decimal Desconto? filters=min:0
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
    {
      type : "btree|unique"
      field: [{name: "asaas_payment_link_id", op: "asc"}]
    }
    {type: "btree", field: [{name: "data_venda", op: "desc"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
    {type: "btree", field: [{name: "vendedor_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]

  guid = "k9m1bxhQIWw6r3vqaOJc89be__M"
}