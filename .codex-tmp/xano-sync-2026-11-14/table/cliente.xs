// Migração ASAAS publicada no workspace 147643.
// Os campos ausentes em documentos antigos são preservados para atualização por GUID.
table cliente {
  auth = false

  schema {
    int id
    text CNome filters=trim
    text CPF filters=trim
    text Telefone filters=trim
    email Email? filters=trim|lower
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "CPF", op: "asc"}]}
    {type: "btree|unique", field: [{name: "Email", op: "asc"}]}
  ]

  guid = "0NP1T4qC0DYOFdsRZuVyEJt3BpE"
}