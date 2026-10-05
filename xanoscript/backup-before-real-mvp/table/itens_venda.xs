// Itens de venda. A API deve exigir exatamente vehicle_id ou part_id.
table itens_venda {
  auth = false

  schema {
    int id
    int sale_id {
      table = "vendas"
    }
  
    enum item_type {
      values = ["vehicle", "part"]
    }
  
    int vehicle_id? {
      table = "veiculos"
    }
  
    int part_id? {
      table = "pecas"
    }
  
    int quantity filters=min:1
    decimal unit_price filters=min:0
    decimal subtotal filters=min:0
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "sale_id", op: "asc"}]}
    {type: "btree", field: [{name: "vehicle_id", op: "asc"}]}
    {type: "btree", field: [{name: "part_id", op: "asc"}]}
  ]

  guid = "_yMoXgkQ8-11YF00fQlBoggpYzc"
}