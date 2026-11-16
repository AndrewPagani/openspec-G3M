// Tabela de integracao entre clientes locais e clientes no gateway ASAAS
table asaas_cliente {
  auth = false

  schema {
    int id
    int cliente_id {
      table = "cliente"
    }

    text asaas_customer_id
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "cliente_id", op: "asc"}]
    }
    {
      type : "btree|unique"
      field: [{name: "asaas_customer_id", op: "asc"}]
    }
  ]

  guid = "ZlUGWoKeZ31OzHzO3mwbf8hEtkU"
}
