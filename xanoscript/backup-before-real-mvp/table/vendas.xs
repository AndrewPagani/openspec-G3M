// Cabeçalho da operação comercial.
table vendas {
  auth = false

  schema {
    int id
    int customer_id {
      table = "clientes"
    }
  
    int seller_id {
      table = "usuarios"
    }
  
    int payment_method_id? {
      table = "formas_pagamento"
    }
  
    int sale_status_id {
      table = "status_venda"
    }
  
    decimal gross_amount? filters=min:0
    decimal discount_amount? filters=min:0
    decimal final_amount? filters=min:0
    text notes?
    timestamp sold_at?
    timestamp cancelled_at?
    text cancellation_reason?
    int created_by? {
      table = "usuarios"
    }
  
    int updated_by? {
      table = "usuarios"
    }
  
    timestamp created_at?=now
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "sale_status_id", op: "asc"}]}
    {type: "btree", field: [{name: "seller_id", op: "asc"}]}
    {type: "btree", field: [{name: "customer_id", op: "asc"}]}
  ]

  guid = "vFHRIGaWw4wmBkX0Atu80ZCus3k"
}