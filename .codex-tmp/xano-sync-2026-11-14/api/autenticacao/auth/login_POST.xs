// Login de usuario com geracao de token de autenticacao
// Autentica o usuario e retorna o token Xano e dados do perfil
// Email e senha para login
query "auth/login" verb=POST {
  api_group = "autenticacao"

  input {
    email email filters=trim|lower
    text senha
  }

  stack {
    // Buscar usuario pelo email normalizado
    db.query user {
      where = $db.user.Email == $input.email
      return = {type: "single"}
    } as $user
  
    // Inicializar flag de validacao de senha
    var $is_valid {
      value = false
    }
  
    // Se o usuario existir, verificar a senha criptografada
    conditional {
      if ($user != null) {
        security.check_password {
          text_password = $input.senha
          hash_password = $user.Senha
        } as $checked
      
        var.update $is_valid {
          value = $checked
        }
      }
    }
  
    // Rejeitar com erro generico sem revelar existencia de usuario
    precondition ($user != null && $is_valid) {
      error_type = "unauthorized"
      error = "Credenciais invalidas"
    }
  
    // Buscar perfil vinculado
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    // Gerar token nativo Xano
    security.create_auth_token {
      table = "user"
      extras = {perfil_id: $user.perfil_id}
      expiration = 86400
      id = $user.id
    } as $auth_token
  }

  response = {
    authToken: $auth_token
    user     : ```
      {
        id: $user.id,
        UNome: $user.UNome,
        Email: $user.Email,
        perfil_id: $user.perfil_id,
        perfil: {
          id: $perfil.id,
          Cargo: $perfil.Cargo
        }
      }
      ```
  }

  guid = "OJmMByiHBiSq6RuuQJ_tZpv1m0Q"
}