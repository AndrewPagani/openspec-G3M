table asaas_evento {
  auth = false
  schema {
    int id
    text event_id
    text payment_id
    text evento
    timestamp processado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "event_id", op: "asc"}]}
  ]

  guid = "e4zK7n-bFGnWYvZD805VCsyfxjs"
}
