// Auditoria de alterações críticas.
table logs_auditoria {
  schema {
    int id
    text tipo_entidade filters=trim|lower
    int entidade_id
    text acao filters=trim|lower
    int usuario_id? { table = "usuarios" }
    json dados_anteriores?
    json dados_posteriores?
    json metadados?
    text endereco_ip?
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "tipo_entidade", op: "asc"}, {name: "entidade_id", op: "asc"}]}
    {type: "btree", field: [{name: "usuario_id", op: "asc"}, {name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
  guid = "BNgcr3iWatNMcCkCPuQOpm44gxQ"
}
