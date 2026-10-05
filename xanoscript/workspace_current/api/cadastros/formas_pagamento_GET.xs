// Listagem de formas de pagamento
// Retorna as formas de pagamento suportadas
query "formas-pagamento" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
  }

  stack {
    // Consultar formas de pagamento
    db.query forma_pagamento {
      return = {type: "list"}
    } as $formas
  }

  response = ```
    $formas|map:{
        id: $$.id,
        Metodo: $$.Metodo
      }
    ```
  guid = "-I8fNuXM69yosE_hRF3hZjAoNOQ"
}