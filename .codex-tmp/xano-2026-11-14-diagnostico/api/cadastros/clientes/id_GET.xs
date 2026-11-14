// Detalhes de um cliente especifico
// Retorna os dados cadastrais do cliente sem expor identificadores externos
// Identificador do cliente
query "clientes/{id}" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "cliente"
    }
  }

  stack {
    // Buscar registro do cliente pelo ID
    db.get cliente {
      field_name = "id"
      field_value = $input.id
    } as $cliente
  
    // Validar se o cliente existe
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente nao encontrado"
    }
  }

  response = {
    id        : $cliente.id
    CNome     : $cliente.CNome
    CPF       : $cliente.CPF
    Telefone  : $cliente.Telefone
    Email     : $cliente.Email
    created_at: $cliente.created_at
  }

  guid = "td6FQ28vboMlbUg0-lotVP8ydq4"
}