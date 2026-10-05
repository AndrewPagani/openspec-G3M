// Permissões por recurso e ação.
table permissoes {
  auth = false

  schema {
    int id
    text resource filters=trim|lower
    text action filters=trim|lower
    text name filters=trim
    text slug filters=trim|lower
    bool is_active?=true
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
    {
      type : "btree"
      field: [{name: "resource", op: "asc"}, {name: "action", op: "asc"}]
    }
  ]

  guid = "Ccmpr-BhMEfFoConL2WItAoLJy0"
}