table venda_item {
  auth = false

  schema {
    int id
    int venda_id {
      table = "venda"
    }
  
    int veiculo_id? {
      table = "veiculo"
    }
  
    int peca_id? {
      table = "peca"
    }
  
    int qtd?=1 filters=min:1
    decimal preco_unit filters=min:0
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}]}
    {type: "btree", field: [{name: "veiculo_id", op: "asc"}]}
    {type: "btree", field: [{name: "peca_id", op: "asc"}]}
  ]

  guid = "lPD0Nc9lDGTCgM6P3u2yy0-s6ac"
}