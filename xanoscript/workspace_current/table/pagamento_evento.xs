table pagamento_evento {
  auth = false

  schema {
    int id
    text asaas_event_id
    text asaas_payment_id
    text evento
    timestamp recebido_em?=now
    timestamp processado_em?
    text status_processamento
    text erro_resumido?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "asaas_event_id", op: "asc"}]
    }
    {
      type : "btree"
      field: [{name: "asaas_payment_id", op: "asc"}]
    }
    {
      type : "btree"
      field: [{name: "status_processamento", op: "asc"}]
    }
  ]

  guid = "3EbjyQ4krYOXyv8sD3L1_K6UGpI"
}