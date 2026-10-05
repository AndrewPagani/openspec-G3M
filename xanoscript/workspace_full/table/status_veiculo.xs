// Status operacionais de veículos.
table status_veiculo {
  schema {
    int id
    text nome filters=trim
    text slug filters=trim|lower
    bool disponivel?=false
    bool comercializavel?=false
    bool ativo?=true
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]
  guid = "8AiHm8MtXd9gI9AcrfHO6NQ5GzE"
}
