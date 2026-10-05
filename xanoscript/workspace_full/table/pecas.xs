// Peças e saldos materializados do estoque.
table pecas {
  schema {
    int id
    text codigo filters=trim|upper
    text nome filters=trim
    text descricao?
    int area_id { table = "areas_veiculo" }
    decimal preco filters=min:0
    int quantidade_total filters=min:0
    int quantidade_disponivel?=0 filters=min:0
    int quantidade_reservada?=0 filters=min:0
    int quantidade_vendida?=0 filters=min:0
    int estoque_minimo?=0 filters=min:0
    bool ativo?=true
    int created_by? { table = "usuarios" }
    int updated_by? { table = "usuarios" }
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "codigo", op: "asc"}]}
    {type: "btree", field: [{name: "nome", op: "asc"}]}
    {type: "btree", field: [{name: "area_id", op: "asc"}]}
  ]
  guid = "kkLdaKJ4Wpluzvm5YE38AlJZEX0"
}
