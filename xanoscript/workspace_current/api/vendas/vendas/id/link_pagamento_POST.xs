// Mantém a rota antiga explícita para clientes legados; nenhum link externo é criado
query "vendas/{id}/link-pagamento" verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  
    int? max_parcelas filters=min:1|max:24
  }

  stack {
    precondition (false) {
      error_type = "badrequest"
      error = "Operacao desativada: pagamentos sao registrados manualmente no Xano"
    }
  }

  response = null
  guid = "DQL8iqkM9CRlIOHbmZPUgqCXJdI"
}
