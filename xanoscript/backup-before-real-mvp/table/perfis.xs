// Esquema relacional do MVP da concessionária.
// As regras transacionais de venda, estoque, cancelamento e autorização
// devem ser implementadas nas APIs/functions do Xano.
// Perfis de acesso.
table perfis {
  auth = false

  schema {
    int id
    text name filters=trim
    text slug filters=trim|lower
    text description?
    bool is_active?=true
    timestamp created_at?=now
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "slug", op: "asc"}]}
  ]

  guid = "1SRoXXSw-LAKgqo3O7mj0h2NbQg"
}