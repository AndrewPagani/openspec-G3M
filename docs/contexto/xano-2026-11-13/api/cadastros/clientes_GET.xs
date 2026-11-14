// Listagem paginada de clientes com busca textual
// Lista clientes com suporte a paginacao e busca por nome, CPF, telefone ou email
// Parametros de consulta e paginacao
query clientes verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
    int page?=1 filters=min:1
    int per_page?=20 filters=min:1|max:100
    text busca? filters=trim
  }

  stack {
    // Buscar clientes filtrando pelo termo de busca se informado
    db.query cliente {
      where = ($input.busca == null || $input.busca == "") || ($db.cliente.CNome includes $input.busca || $db.cliente.CPF includes $input.busca || $db.cliente.Telefone includes $input.busca || $db.cliente.Email includes $input.busca)
      sort = {CNome: "asc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }
    } as $result
  
    // Mapear registros para remover campos internos como asaas_customer_id
    var $sanitized_items {
      value = ```
        $result.items|map:{
                id: $$.id,
                CNome: $$.CNome,
                CPF: $$.CPF,
                Telefone: $$.Telefone,
                Email: $$.Email,
                created_at: $$.created_at
              }
        ```
    }
  }

  response = {
    items     : $sanitized_items
    pagination: ```
      {
        page: $result.curPage,
        per_page: $result.perPage,
        total: $result.total ?? ($result.items|count),
        total_pages: $result.pageTotal ?? 1
      }
      ```
  }

  guid = "k_5ISualOUfQUKsvUx-98nlM3RM"
}