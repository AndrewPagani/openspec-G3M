// Listagem de usuarios para administradores
// Lista usuarios do sistema com seus respectivos cargos (somente Administrador)
query usuarios verb=GET {
  api_group = "gerenciamento"
  auth = "user"

  input {
  }

  stack {
    // 1. Validar perfil do usuario autenticado (somente Administrador)
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $current_user
  
    db.get perfil {
      field_name = "id"
      field_value = $current_user.perfil_id
    } as $current_perfil
  
    precondition ($current_perfil != null && $current_perfil.Cargo == "Administrador") {
      error_type = "accessdenied"
      error = "Apenas Administradores possuem permissao para consultar usuarios"
    }
  
    // 2. Consultar perfis para enriquecimento
    db.query perfil {
      return = {type: "list"}
    } as $perfis
  
    // 3. Consultar usuarios
    db.query user {
      sort = {id: "asc"}
      return = {type: "list"}
    } as $usuarios
  
    // 4. Mapear sem expor Senha
    var $sanitized_users {
      value = ```
        $usuarios|map:{
                id: $$.id,
                UNome: $$.UNome,
                Email: $$.Email,
                perfil_id: $$.perfil_id,
                cargo: (($perfis|find:$item.id == $$.perfil_id).Cargo ?? ""),
                created_at: $$.created_at
              }
        ```
    }
  }

  response = $sanitized_users
  guid = "0wDD9iDE_fTxg3B8Z2pTu7le6Fo"
}