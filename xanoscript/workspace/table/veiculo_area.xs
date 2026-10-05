table veiculo_area {
  schema {
    int id
    text Secao filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Secao", op: "asc"}]}
  ]
}
