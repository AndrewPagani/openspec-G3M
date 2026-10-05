// Clientes compradores.
table clientes {
  auth = false

  schema {
    int id
    text name filters=trim
    text cpf filters=trim
    text phone filters=trim
    email email? filters=trim|lower
    bool is_active?=true
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
    {type: "btree|unique", field: [{name: "cpf", op: "asc"}]}
    {type: "btree", field: [{name: "name", op: "asc"}]}
    {type: "btree", field: [{name: "email", op: "asc"}]}
  ]

  guid = "Jt5Tt-aAQilsr5_xBS6zuEa7ZAg"
}