// Status operacionais de vendas.
table status_venda {
  schema {
    int id
    text nome filters=trim
    text slug filters=trim|lower
    bool finalizado?=false
    bool cancelado?=false
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]
  guid = "AJWCLTf8GmIl0gD7UO4frvqdIlE"
}
