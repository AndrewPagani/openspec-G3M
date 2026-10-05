// Histórico de transições de venda.
table historico_status_venda {
  auth = false

  schema {
    int id
    int sale_id {
      table = "vendas"
    }
  
    int from_status_id? {
      table = "status_venda"
    }
  
    int to_status_id {
      table = "status_venda"
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
        {name: "sale_id", op: "asc"}
        {name: "created_at", op: "desc"}
      ]
    }
  ]

  guid = "3-8GoMt2IUUhAYqA_9ceN74Adjg"
}