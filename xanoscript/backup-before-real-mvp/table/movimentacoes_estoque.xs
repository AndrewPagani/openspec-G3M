// Livro de movimentações de estoque de peças.
table movimentacoes_estoque {
  auth = false

  schema {
    int id
    int part_id {
      table = "pecas"
    }
  
    int sale_id? {
      table = "vendas"
    }
  
    enum movement_type {
      values = ["entry", "reservation", "release", "sale", "return", "adjustment"]
    }
  
    int quantity filters=min:1
    int available_before filters=min:0
    int available_after filters=min:0
    int reserved_before filters=min:0
    int reserved_after filters=min:0
    int sold_before filters=min:0
    int sold_after filters=min:0
    text reason?
    int performed_by? {
      table = "usuarios"
    }
  
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree"
      field: [
        {name: "part_id", op: "asc"}
        {name: "created_at", op: "desc"}
      ]
    }
    {type: "btree", field: [{name: "sale_id", op: "asc"}]}
  ]

  guid = "mVY-EQopoQruySLgdUm-Fc0eXvI"
}