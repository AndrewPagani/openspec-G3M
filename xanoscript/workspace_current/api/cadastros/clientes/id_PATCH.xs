// Atualizacao parcial de dados cadastrais do cliente
// Atualiza campos cadastrais do cliente validando unicidade de CPF e email
// Identificador e campos permitidos para atualizacao
query "clientes/{id}" verb=PATCH {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "cliente"
    }
  
    text CNome? filters=trim
    text CPF? filters=trim
    text Telefone? filters=trim
    email Email? filters=trim|lower
  }

  stack {
    // Buscar cliente existente
    db.get cliente {
      field_name = "id"
      field_value = $input.id
    } as $cliente
  
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente nao encontrado"
    }
  
    // Inicializar mapa de atualizacoes
    var $updates {
      value = {}
    }
  
    // Processar atualizacao de nome
    conditional {
      if ($input.CNome != null) {
        precondition (($input.CNome|strlen) >= 2) {
          error_type = "inputerror"
          error = "Nome deve conter ao menos 2 caracteres"
        }
      
        var.update $updates {
          value = $updates|set:"CNome":$input.CNome
        }
      }
    }
  
    // Processar atualizacao de CPF
    conditional {
      if ($input.CPF != null) {
        var $cpf_clean {
          value = "/[^0-9]/"|regex_replace:"":$input.CPF
        }
      
        precondition (($cpf_clean|strlen) == 11) {
          error_type = "inputerror"
          error = "CPF deve conter exatamente 11 digitos numericos"
        }
      
        db.query cliente {
          where = $db.cliente.CPF == $cpf_clean && $db.cliente.id != $input.id
          return = {type: "single"}
        } as $cpf_check
      
        precondition ($cpf_check == null) {
          error_type = "badrequest"
          error = "CPF ja cadastrado para outro cliente"
        }
      
        var.update $updates {
          value = $updates|set:"CPF":$cpf_clean
        }
      }
    }
  
    // Processar atualizacao de telefone
    conditional {
      if ($input.Telefone != null) {
        precondition (($input.Telefone|strlen) >= 8) {
          error_type = "inputerror"
          error = "Telefone invalido"
        }
      
        var.update $updates {
          value = $updates|set:"Telefone":$input.Telefone
        }
      }
    }
  
    // Processar atualizacao de email
    conditional {
      if ($input.Email != null) {
        var $email_norm {
          value = $input.Email|to_lower
        }
      
        db.query cliente {
          where = $db.cliente.Email == $email_norm && $db.cliente.id != $input.id
          return = {type: "single"}
        } as $email_check
      
        precondition ($email_check == null) {
          error_type = "badrequest"
          error = "Email ja cadastrado para outro cliente"
        }
      
        var.update $updates {
          value = $updates|set:"Email":$email_norm
        }
      }
    }
  
    // Atualizar no banco apenas se houver campos alterados
    conditional {
      if (($updates|is_empty) == false) {
        db.patch cliente {
          field_name = "id"
          field_value = $input.id
          data = $updates
        } as $cliente_atualizado
      }
    
      else {
        var $cliente_atualizado {
          value = $cliente
        }
      }
    }
  }

  response = {
    id        : $cliente_atualizado.id
    CNome     : $cliente_atualizado.CNome
    CPF       : $cliente_atualizado.CPF
    Telefone  : $cliente_atualizado.Telefone
    Email     : $cliente_atualizado.Email
    created_at: $cliente_atualizado.created_at
  }

  guid = "6rAuj7Tam-X3HOlF-du8a_sW3LU"
}