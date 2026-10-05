// Preferências persistidas do dashboard por usuário.
table configuracoes_dashboard {
  auth = false

  schema {
    int id
    int user_id {
      table = "usuarios"
    }
  
    enum default_period {
      values = ["today", "week", "month", "quarter", "year"]
    }
  
    json filters?
    timestamp created_at?=now
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "GfQMiNHri1FhsyC_XWoLFn2OhU0"
}