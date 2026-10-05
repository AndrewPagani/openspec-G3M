table status_venda {
  schema {
    int id
    text Descricao_venda filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Descricao_venda", op: "asc"}]}
  ]
}
