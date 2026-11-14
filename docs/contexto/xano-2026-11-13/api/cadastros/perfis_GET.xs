// Listagem de perfis de usuario
// Retorna os perfis de acesso cadastrados
query perfis verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
  }

  stack {
    // Consultar todos os perfis
    db.query perfil {
      return = {type: "list"}
    } as $perfis
  }

  response = ```
    $perfis|map:{
        id: $$.id,
        Cargo: $$.Cargo
      }
    ```
  guid = "aoacYug1d-7DZUqf54VaC6TprcQ"
}