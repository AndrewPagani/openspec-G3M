// Listagem de areas e secoes de veiculos e pecas
// Retorna as areas e secoes cadastradas
query "veiculo-areas" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
  }

  stack {
    // Consultar todas as secoes de veiculos e pecas
    db.query veiculo_area {
      return = {type: "list"}
    } as $areas
  }

  response = ```
    $areas|map:{
        id: $$.id,
        Secao: $$.Secao
      }
    ```
  guid = "LcviYv6Vpu3uK2fdzw3Y6lOVCY4"
}