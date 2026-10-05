table venda {
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
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "data_venda", op: "desc"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
    {type: "btree", field: [{name: "vendedor_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]
}
