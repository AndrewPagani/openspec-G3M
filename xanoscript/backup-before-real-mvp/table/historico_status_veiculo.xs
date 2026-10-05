// Histórico de transições de veículo.
table historico_status_veiculo {
  auth = false

  schema {
    int id
    int vehicle_id {
      table = "veiculos"
    }
  
    int from_status_id? {
      table = "status_veiculo"
    }
  
    int to_status_id {
      table = "status_veiculo"
    }
  
    int sale_id? {
      table = "vendas"
    }
  
    int changed_by? {
      table = "usuarios"
    }
  
    text reason?
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree"
      field: [
        {name: "vehicle_id", op: "asc"}
        {name: "created_at", op: "desc"}
      ]
    }
  ]

  guid = "cTQBjZqeyVARdtMaowq0xkkdg08"
}