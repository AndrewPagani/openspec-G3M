// Livro de movimentações de estoque de peças.
table movimentacoes_estoque {
  schema {
    int id
    int peca_id { table = "pecas" }
    int venda_id? { table = "vendas" }
    enum tipo_movimentacao {
      values = ["entrada", "reserva", "liberacao", "venda", "devolucao", "ajuste"]
    }
    int quantidade filters=min:1
    int disponivel_antes filters=min:0
    int disponivel_depois filters=min:0
    int reservado_antes filters=min:0
    int reservado_depois filters=min:0
    int vendido_antes filters=min:0
    int vendido_depois filters=min:0
    text motivo?
    int realizado_por? { table = "usuarios" }
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "peca_id", op: "asc"}, {name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}]}
  ]
  guid = "mVY-EQopoQruySLgdUm-Fc0eXvI"
}
