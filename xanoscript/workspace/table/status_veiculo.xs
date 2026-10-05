table status_veiculo {
  schema {
    int id
    text Descricao filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Descricao", op: "asc"}]}
  ]
}
