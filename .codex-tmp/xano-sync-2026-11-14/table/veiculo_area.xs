table veiculo_area {
  auth = false

  schema {
    int id
    text Secao filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Secao", op: "asc"}]}
  ]

  guid = "SkDBFHkTClWSAOWB-tQEdgNCxwY"
}