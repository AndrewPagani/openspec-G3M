// Áreas de aplicação das peças.
table areas_veiculo {
  schema {
    int id
    text nome filters=trim
    text slug filters=trim|lower
    bool ativo?=true
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]
  guid = "XJwaXxvr7L9dVik2-wGiuwU78jc"
}
