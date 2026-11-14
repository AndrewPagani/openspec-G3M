// Listagem de status de veiculos
// Retorna os possiveis status de veiculos
query "status-veiculos" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
  }

  stack {
    // Consultar todos os status de veiculos
    db.query status_veiculo {
      return = {type: "list"}
    } as $status_list
  }

  response = ```
    $status_list|map:{
        id: $$.id,
        Descricao: $$.Descricao
      }
    ```
  guid = "kBrXZSt26k_Pd5Cpk7TjGmyR1Zk"
}