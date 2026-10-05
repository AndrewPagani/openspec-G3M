// Rota legada desativada; não consulta gateways nem altera parcelas
query "vendas/{id}/pagamento/atualizar" verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  }

  stack {
    precondition (false) {
      error_type = "badrequest"
      error = "Conciliacao externa desativada: consulte as baixas manuais no Xano"
    }
  }

  response = null
  guid = "dc7mNnThcMTatvcaUq0whonhpqk"
}
