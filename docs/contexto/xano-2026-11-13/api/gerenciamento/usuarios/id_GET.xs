// Detalhe de usuario para administradores
// Retorna informacoes cadastrais de um usuario especifico (somente Administrador)
// Identificador do usuario
query "usuarios/{id}" verb=GET {
  api_group = "gerenciamento"
  auth = "user"

  input {
    int id {
      table = "user"
    }
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
  
    // 2. Buscar usuario solicitado
    db.get user {
      field_name = "id"
      field_value = $input.id
    } as $user_alvo
  
    precondition ($user_alvo != null) {
      error_type = "notfound"
      error = "Usuario nao encontrado"
    }
  
    // 3. Buscar perfil do usuario
    db.get perfil {
      field_name = "id"
      field_value = $user_alvo.perfil_id
    } as $perfil_alvo
  }

  response = {
    id        : $user_alvo.id
    UNome     : $user_alvo.UNome
    Email     : $user_alvo.Email
    perfil_id : $user_alvo.perfil_id
    cargo     : ($perfil_alvo.Cargo ?? "")
    created_at: $user_alvo.created_at
  }

  guid = "Ru9aA8-XjLwe47IkaC9cFQ0Uuzs"
}