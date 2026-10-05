table user {
  auth = true
  schema {
    int id
    text UNome filters=trim
    email Email filters=trim|lower
    int perfil_id { table = "perfil" }
    password Senha {
      sensitive = true
    }
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Email", op: "asc"}]}
    {type: "btree", field: [{name: "perfil_id", op: "asc"}]}
  ]
}
