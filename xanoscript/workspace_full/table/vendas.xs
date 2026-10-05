// Cabeçalho da operação comercial.
table vendas {
  schema {
    int id
    int cliente_id { table = "clientes" }
    int vendedor_id { table = "usuarios" }
    int forma_pagamento_id? { table = "formas_pagamento" }
    int status_id { table = "status_venda" }
    decimal valor_bruto?=0 filters=min:0
    decimal desconto?=0 filters=min:0
    decimal valor_final?=0 filters=min:0
    text observacoes?
    timestamp vendido_em?
    timestamp cancelado_em?
    text motivo_cancelamento?
    int created_by? { table = "usuarios" }
    int updated_by? { table = "usuarios" }
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
    {type: "btree", field: [{name: "vendedor_id", op: "asc"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
  ]
  guid = "vFHRIGaWw4wmBkX0Atu80ZCus3k"
}
