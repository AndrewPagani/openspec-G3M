table forma_pagamento {
  auth = false

  schema {
    int id
    text Metodo filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Metodo", op: "asc"}]}
  ]

  guid = "qpFKrOFczIlbHc4OD4nGNAeR_kM"
}