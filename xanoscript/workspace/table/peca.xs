table peca {
  schema {
    int id
    text PCNome filters=trim
    decimal PCvalor filters=min:0
    int qtd_disp?=0 filters=min:0
    int area_id? { table = "veiculo_area" }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "PCNome", op: "asc"}]}
    {type: "btree", field: [{name: "area_id", op: "asc"}]}
  ]
}
