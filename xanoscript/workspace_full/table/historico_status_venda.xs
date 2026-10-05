// Histórico de transições de venda.
table historico_status_venda {
  schema {
    int id
    int venda_id { table = "vendas" }
    int status_anterior_id? { table = "status_venda" }
    int status_novo_id { table = "status_venda" }
    int alterado_por? { table = "usuarios" }
    text motivo?
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}, {name: "created_at", op: "desc"}]}
  ]
  guid = "3-8GoMt2IUUhAYqA_9ceN74Adjg"
}
