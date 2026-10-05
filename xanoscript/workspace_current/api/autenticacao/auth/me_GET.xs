// Retorna dados do usuario autenticado e seu perfil
// Retorna informacoes do usuario atual autenticado sem expor a senha
query "auth/me" verb=GET {
  api_group = "autenticacao"
  auth = "user"

  input {
  }

  stack {
    // Buscar usuario correspondente ao token
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    // Garantir existencia do registro
    precondition ($user != null) {
      error_type = "notfound"
      error = "Usuario nao encontrado"
    }
  
    // Buscar perfil vinculado
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  }

  response = {
    id        : $user.id
    UNome     : $user.UNome
    Email     : $user.Email
    perfil_id : $user.perfil_id
    perfil    : ```
      {
        id: $perfil.id,
        Cargo: $perfil.Cargo
      }
      ```
    created_at: $user.created_at
  }

  guid = "Zx4kkzhJejrZJqn_IAicOSKNsgE"
}