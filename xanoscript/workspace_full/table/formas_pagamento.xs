// Formas de pagamento disponíveis no MVP.
table formas_pagamento {
  schema {
    int id
    text nome filters=trim
    text slug filters=trim|lower
    bool ativo?=true
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]
  guid = "LlsaKVmtus2x7-19zkWB45z4h14"
}
