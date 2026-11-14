// Listagem de status de vendas
// Retorna os status de venda cadastrados
query "status-vendas" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
  }

  stack {
    // Consultar status de venda
    db.query status_venda {
      return = {type: "list"}
    } as $status_vendas
  }

  response = ```
    $status_vendas|map:{
        id: $$.id,
        Descricao_venda: $$.Descricao_venda
      }
    ```
  guid = "Czwd81CYlLpOtLtMFXN533IxlFM"
}