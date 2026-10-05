// Usuários internos do sistema e autenticação do Xano.
table usuarios {
  auth = true
  schema {
    int id
    text nome filters=trim
    email email filters=trim|lower
    password senha {
      sensitive = true
    }
    int perfil_id { table = "perfis" }
    bool ativo?=true
    timestamp ultimo_login_em?
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
    {type: "btree", field: [{name: "perfil_id", op: "asc"}]}
  ]
  guid = "GOZfy8p5CTgWHY648evRSSZhS7M"
}
