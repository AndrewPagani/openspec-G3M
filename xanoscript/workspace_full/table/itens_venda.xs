// Itens de venda. A API deve exigir exatamente veiculo_id ou peca_id.
table itens_venda {
  schema {
    int id
    int venda_id { table = "vendas" }
    enum tipo_item {
      values = ["veiculo", "peca"]
    }
    int veiculo_id? { table = "veiculos" }
    int peca_id? { table = "pecas" }
    int quantidade filters=min:1
    decimal preco_unitario filters=min:0
    decimal subtotal filters=min:0
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}]}
    {type: "btree", field: [{name: "veiculo_id", op: "asc"}]}
    {type: "btree", field: [{name: "peca_id", op: "asc"}]}
  ]
  guid = "_yMoXgkQ8-11YF00fQlBoggpYzc"
}
