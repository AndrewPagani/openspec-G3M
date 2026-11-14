table venda_parcela {
  auth = false

  schema {
    int id
    int venda_id {
      table = "venda"
    }
  
    int numero_parcela filters=min:"1,max":24
    int total_parcelas filters=min:"1,max":24
    decimal valor filters=min:0.01
    timestamp vencimento
    text status?=PENDENTE
    int forma_recebida_id? {
      table = "forma_pagamento"
    }
  
    timestamp recebido_em?
    int recebido_por? {
      table = "user"
    }
  
    timestamp cancelada_em?
    timestamp updated_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [
        {name: "venda_id", op: "asc"}
        {name: "numero_parcela", op: "asc"}
      ]
    }
    {
      type : "btree"
      field: [{name: "status", op: "asc"}, {name: "vencimento", op: "asc"}]
    }
    {type: "btree", field: [{name: "status", op: "asc"}]}
    {type: "btree", field: [{name: "vencimento", op: "asc"}]}
    {type: "btree", field: [{name: "recebido_em", op: "desc"}]}
    {
      type : "btree"
      field: [{name: "forma_recebida_id", op: "asc"}]
    }
  ]

  guid = "BfbjLgk7XQvy8aoiXcfBgWM2pXM"
}