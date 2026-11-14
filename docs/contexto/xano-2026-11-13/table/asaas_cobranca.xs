// Tabela de integracao para cobrancas e links de pagamento ASAAS
table asaas_cobranca {
  auth = false

  schema {
    int id
    int venda_id {
      table = "venda"
    }
  
    text asaas_payment_id
    text invoice_url
    text status?=PENDING
    date due_date
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "venda_id", op: "asc"}]
    }
    {
      type : "btree|unique"
      field: [{name: "asaas_payment_id", op: "asc"}]
    }
    {type: "btree", field: [{name: "status", op: "asc"}]}
  ]

  guid = "jAobo1s0O80poH3GcHsbFTOtiic"
}