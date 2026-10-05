table forma_pagamento {
  schema {
    int id
    text Metodo filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Metodo", op: "asc"}]}
  ]
}
