// Cadastro de novo cliente
// Cadastra um novo cliente com validacao de CPF e email unicos
// Dados do cliente a ser cadastrado
query clientes verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    text CNome filters=trim
    text CPF filters=trim
    text Telefone filters=trim
    email Email filters=trim|lower
  }

  stack {
    // Normalizar CPF removendo caracteres nao numericos
    var $cpf_clean {
      value = "/[^0-9]/"|regex_replace:"":$input.CPF
    }
  
    // Normalizar email
    var $email_norm {
      value = $input.Email|to_lower
    }
  
    // Validar formato basico do CPF
    precondition (($cpf_clean|strlen) == 11) {
      error_type = "inputerror"
      error = "CPF deve conter exatamente 11 digitos numericos"
    }
  
    // Validar nome e telefone
    precondition (($input.CNome|strlen) >= 2) {
      error_type = "inputerror"
      error = "Nome do cliente deve conter ao menos 2 caracteres"
    }
  
    precondition (($input.Telefone|strlen) >= 8) {
      error_type = "inputerror"
      error = "Telefone invalido"
    }
  
    // Verificar unicidade de CPF
    db.query cliente {
      where = $db.cliente.CPF == $cpf_clean
      return = {type: "single"}
    } as $cpf_existente
  
    precondition ($cpf_existente == null) {
      error_type = "badrequest"
      error = "CPF ja cadastrado para outro cliente"
    }
  
    // Verificar unicidade de Email
    db.query cliente {
      where = $db.cliente.Email == $email_norm
      return = {type: "single"}
    } as $email_existente
  
    precondition ($email_existente == null) {
      error_type = "badrequest"
      error = "Email ja cadastrado para outro cliente"
    }
  
    // Inserir novo cliente no banco
    db.add cliente {
      data = {
        CNome     : $input.CNome
        CPF       : $cpf_clean
        Telefone  : $input.Telefone
        Email     : $email_norm
        created_at: now
      }
    } as $novo_cliente
  
    // Criar o cliente correspondente no ASAAS Sandbox antes de confirmar o cadastro
    api.request {
      url = "https://api-sandbox.asaas.com/v3/customers"
      method = "POST"
      params = {
        name                : $novo_cliente.CNome
        cpfCnpj             : $novo_cliente.CPF
        email               : $novo_cliente.Email
        mobilePhone         : $novo_cliente.Telefone
        notificationDisabled: true
      }
    
      headers = []
        |push:"access_token: " ~ $env.ASAAS
        |push:"Content-Type: application/json"
        |push:"User-Agent: AutoGestao/1.0"
    } as $cliente_asaas_response
  
    conditional {
      if ($cliente_asaas_response.status < 200 || $cliente_asaas_response.status >= 300 || $cliente_asaas_response.body.id == null) {
        db.del cliente {
          field_name = "id"
          field_value = $novo_cliente.id
        }
      
        precondition (false) {
          error_type = "badrequest"
          error = "Cliente nao foi criado no ASAAS; o cadastro local foi desfeito"
        }
      }
    }
  
    db.add asaas_cliente {
      data = {
        cliente_id       : $novo_cliente.id
        asaas_customer_id: $cliente_asaas_response.body.id
      }
    } as $cliente_asaas
  }

  response = {
    id        : $novo_cliente.id
    CNome     : $novo_cliente.CNome
    CPF       : $novo_cliente.CPF
    Telefone  : $novo_cliente.Telefone
    Email     : $novo_cliente.Email
    created_at: $novo_cliente.created_at
  }

  guid = "5ar3o6onB4Q7FGjX3G6rNh_anZo"
}