table veiculo {
  auth = false

  schema {
    int id
    text Marca filters=trim
    text Modelo filters=trim
    text Cor filters=trim
    int Ano
    text Placa? filters=trim|upper
    text Chassi? filters=trim|upper
    decimal Quilometragem? filters=min:0
    decimal Preco filters=min:0
    text Imagem_url? filters=trim
    int status_id {
      table = "status_veiculo"
    }
  
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Placa", op: "asc"}]}
    {type: "btree|unique", field: [{name: "Chassi", op: "asc"}]}
    {
      type : "btree"
      field: [{name: "Marca", op: "asc"}, {name: "Modelo", op: "asc"}]
    }
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]

  guid = "IrvCzPzPd1dfxxrkHxmKAeYH7Hw"
}