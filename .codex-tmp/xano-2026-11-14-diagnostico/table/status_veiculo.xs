table status_veiculo {
  auth = false

  schema {
    int id
    text Descricao filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "Descricao", op: "asc"}]
    }
  ]

  guid = "xY-ZfIGHc0JlsICQvl30B4xmERg"
}