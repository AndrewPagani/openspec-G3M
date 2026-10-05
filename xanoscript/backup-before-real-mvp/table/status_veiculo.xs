// Status operacionais de veículos.
table status_veiculo {
  auth = false

  schema {
    int id
    text name filters=trim
    text slug filters=trim|lower
    bool is_available?
    bool is_sellable?
    bool is_active?=true
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]

  guid = "8AiHm8MtXd9gI9AcrfHO6NQ5GzE"
}