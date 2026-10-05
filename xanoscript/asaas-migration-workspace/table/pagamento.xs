table pagamento {
  auth = false

  schema {
    int id
    int venda_id { table = "venda" }
    text asaas_payment_id
    text asaas_customer_id?
    text asaas_installment_id?
    text status_asaas
    text billing_type?
    decimal valor filters=min:0
    decimal valor_liquido? filters=min:0
    decimal taxa? filters=min:0
    int numero_parcela?
    int total_parcelas?
    timestamp vencimento?
    timestamp recebido_em?
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "asaas_payment_id", op: "asc"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_asaas", op: "asc"}]}
    {type: "btree", field: [{name: "recebido_em", op: "desc"}]}
  ]
  guid = "BUOGUNZjCVeYKnhpOSrxXJUHsl0"
}
