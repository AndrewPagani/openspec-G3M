// Detalhes de veiculos relacionados 1:1 com a tabela veiculo
table veiculo_detalhe {
  auth = false

  schema {
    int id
    int veiculo_id {
      table = "veiculo"
    }
  
    text uf_registro? filters=trim|upper
    text cidade_registro? filters=trim
    int ano_fabricacao? filters=min:1900|max:2100
    text motorizacao? filters=trim
    text combustivel? filters=trim
    text cambio? filters=trim
    decimal quilometragem? filters=min:0
    int numero_portas? filters=min:1|max:20
    int numero_lugares? filters=min:1|max:100
    json opcionais?
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "veiculo_id", op: "asc"}]
    }
    {type: "btree", field: [{name: "uf_registro", op: "asc"}]}
  ]

  guid = "qKBxcjSlEt5E6CYFrFP2IndPEzI"
}