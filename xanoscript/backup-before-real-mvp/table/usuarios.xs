// Usuários internos do sistema e autenticação do Xano.
table usuarios {
  auth = true

  schema {
    int id
    text name filters=trim
    email email filters=trim|lower
    password password {
      sensitive = true
    }
  
    int role_id {
      table = "perfis"
    }
  
    bool is_active?=true
    timestamp last_login_at?
    timestamp created_at?=now
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
    {type: "btree", field: [{name: "role_id", op: "asc"}]}
  ]

  guid = "GOZfy8p5CTgWHY648evRSSZhS7M"
}