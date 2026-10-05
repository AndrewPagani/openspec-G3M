// Relação N:N entre perfis e permissões.
table perfil_permissoes {
  auth = false

  schema {
    int id
    int role_id {
      table = "perfis"
    }
  
    int permission_id {
      table = "permissoes"
    }
  
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [
        {name: "role_id", op: "asc"}
        {name: "permission_id", op: "asc"}
      ]
    }
  ]

  guid = "WWreJGuAbCTCAQ6mcpeFAEO3W-k"
}