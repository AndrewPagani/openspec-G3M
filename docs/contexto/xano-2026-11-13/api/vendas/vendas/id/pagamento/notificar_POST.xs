// Rota legada desativada; o fluxo manual não envia cobranças ou notificações
query "vendas/{id}/pagamento/notificar" verb=POST {
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
      error = "Notificacoes de pagamento nao estao disponiveis neste fluxo"
    }
  }

  response = null
  guid = "fe-VjkQ-kM6BesoEgPgiQU6Y-iI"
}