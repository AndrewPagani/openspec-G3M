// Esquema mínimo do MVP real da concessionária.
// Valores monetários usam decimal e datas usam timestamp no Xano.
// Regras de transição, estoque e validação de item devem ficar nas APIs.

table perfil {
  schema {
    int id
    text Cargo filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Cargo", op: "asc"}]}
  ]
}
