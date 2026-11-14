table peca {
  auth = false

  schema {
    int id
    text PCNome filters=trim
    decimal PCvalor filters=min:0
    int qtd_disp? filters=min:0
    int area_id? {
      table = "veiculo_area"
    }
  
    text imagem_url? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "PCNome", op: "asc"}]}
    {type: "btree", field: [{name: "area_id", op: "asc"}]}
    {type: "btree", field: [{name: "imagem_url", op: "asc"}]}
  ]

  guid = "8FpCnm1UPOvY5VsL25D5oVKRE_E"
}