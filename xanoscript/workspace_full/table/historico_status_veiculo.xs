// Histórico de transições de veículo.
table historico_status_veiculo {
  schema {
    int id
    int veiculo_id { table = "veiculos" }
    int status_anterior_id? { table = "status_veiculo" }
    int status_novo_id { table = "status_veiculo" }
    int venda_id? { table = "vendas" }
    int alterado_por? { table = "usuarios" }
    text motivo?
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "veiculo_id", op: "asc"}, {name: "created_at", op: "desc"}]}
  ]
  guid = "cTQBjZqeyVARdtMaowq0xkkdg08"
}
