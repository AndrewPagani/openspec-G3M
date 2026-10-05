// Peças e saldos materializados do estoque.
table pecas {
  auth = false

  schema {
    int id
    text sku filters=trim|upper
    text name filters=trim
    text description?
    int vehicle_area_id {
      table = "areas_veiculo"
    }
  
    decimal sale_price filters=min:0
    int total_quantity filters=min:0
    int available_quantity? filters=min:0
    int reserved_quantity? filters=min:0
    int sold_quantity? filters=min:0
    int minimum_stock? filters=min:0
    bool is_active?=true
    int created_by? {
      table = "usuarios"
    }
  
    int updated_by? {
      table = "usuarios"
    }
  
    timestamp created_at?=now
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "sku", op: "asc"}]}
    {type: "btree", field: [{name: "name", op: "asc"}]}
    {
      type : "btree"
      field: [{name: "vehicle_area_id", op: "asc"}]
    }
  ]

  guid = "kkLdaKJ4Wpluzvm5YE38AlJZEX0"
}