// Áreas de aplicação das peças.
table areas_veiculo {
  auth = false

  schema {
    int id
    text name filters=trim
    text slug filters=trim|lower
    bool is_active?=true
    timestamp created_at?=now
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]

  guid = "XJwaXxvr7L9dVik2-wGiuwU78jc"
}