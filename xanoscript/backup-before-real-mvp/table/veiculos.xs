// Veículos comercializados pela concessionária.
table veiculos {
  auth = false

  schema {
    int id
    text chassis_number filters=trim|upper
    text plate? filters=trim|upper
    text brand filters=trim
    text model filters=trim
    text color filters=trim
    int manufacture_year filters=min:1886
    int model_year? filters=min:1886
    int mileage filters=min:0
    decimal sale_price filters=min:0
    int vehicle_status_id {
      table = "status_veiculo"
    }
  
    timestamp available_at?
    timestamp sold_at?
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
    {
      type : "btree|unique"
      field: [{name: "chassis_number", op: "asc"}]
    }
    {type: "btree|unique", field: [{name: "plate", op: "asc"}]}
    {
      type : "btree"
      field: [{name: "brand", op: "asc"}, {name: "model", op: "asc"}]
    }
    {
      type : "btree"
      field: [{name: "vehicle_status_id", op: "asc"}]
    }
  ]

  guid = "6X-c8ACnvG-XbpLt2VeePMISu1s"
}