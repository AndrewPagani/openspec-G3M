// Clientes compradores.
table clientes {
  schema {
    int id
    text nome filters=trim
    text cpf filters=trim
    text telefone filters=trim
    email email? filters=trim|lower
    bool ativo?=true
    int created_by? { table = "usuarios" }
    int updated_by? { table = "usuarios" }
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "cpf", op: "asc"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
    {type: "btree", field: [{name: "email", op: "asc"}]}
  ]
  guid = "Jt5Tt-aAQilsr5_xBS6zuEa7ZAg"
}
