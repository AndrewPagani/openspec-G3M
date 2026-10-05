// Preferências persistidas do dashboard por usuário.
table configuracoes_dashboard {
  schema {
    int id
    int usuario_id { table = "usuarios" }
    enum periodo_padrao {
      values = ["dia", "semana", "mes", "trimestre", "ano"]
    }
    json filtros?
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "usuario_id", op: "asc"}]}
  ]
  guid = "GfQMiNHri1FhsyC_XWoLFn2OhU0"
}
