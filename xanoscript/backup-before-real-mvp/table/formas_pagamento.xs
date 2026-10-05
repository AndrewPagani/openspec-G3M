// Formas de pagamento disponíveis no MVP.
table formas_pagamento {
  auth = false

  schema {
    int id
    text name filters=trim
    text slug filters=trim|lower
    bool is_active?=true
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]

  guid = "LlsaKVmtus2x7-19zkWB45z4h14"
}