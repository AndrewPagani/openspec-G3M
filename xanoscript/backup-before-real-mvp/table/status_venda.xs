// Status operacionais de vendas.
table status_venda {
  auth = false

  schema {
    int id
    text name filters=trim
    text slug filters=trim|lower
    bool is_final?
    bool is_cancelled?
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]

  guid = "AJWCLTf8GmIl0gD7UO4frvqdIlE"
}