// Gera uma cobrança única no ASAAS Sandbox e persiste somente o vínculo externo.
query "vendas/{id}/link-pagamento" verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  }

  stack {
    db.get venda {
      field_name = "id"
      field_value = $input.id
    } as $venda
  
    precondition ($venda != null) {
      error_type = "notfound"
      error = "Venda nao encontrada"
    }
  
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $usuario
  
    db.get perfil {
      field_name = "id"
      field_value = $usuario.perfil_id
    } as $perfil
  
    precondition ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador") {
      error_type = "accessdenied"
      error = "Somente gerentes e administradores podem gerar links de pagamento"
    }
  
    db.get status_venda {
      field_name = "id"
      field_value = $venda.status_id
    } as $status_venda
  
    precondition ($status_venda.Descricao_venda == "Pendente") {
      error_type = "badrequest"
      error = "Somente vendas pendentes podem gerar link de pagamento"
    }
  
    db.query asaas_cobranca {
      where = $db.asaas_cobranca.venda_id == $venda.id
      return = {type: "single"}
    } as $cobranca_existente
  
    conditional {
      if ($cobranca_existente == null) {
        db.get cliente {
          field_name = "id"
          field_value = $venda.cliente_id
        } as $cliente
      
        precondition ($cliente != null && $cliente.CNome != null && $cliente.CPF != null && $cliente.Email != null) {
          error_type = "badrequest"
          error = "Cliente deve possuir nome, CPF e email para gerar a cobranca"
        }
      
        db.query asaas_cliente {
          where = $db.asaas_cliente.cliente_id == $cliente.id
          return = {type: "single"}
        } as $cliente_asaas
      
        conditional {
          if ($cliente_asaas == null) {
            api.request {
              url = "https://api-sandbox.asaas.com/v3/customers"
              method = "POST"
              params = {
                name                : $cliente.CNome
                cpfCnpj             : $cliente.CPF
                email               : $cliente.Email
                mobilePhone         : $cliente.Telefone
                notificationDisabled: true
              }
            
              headers = []
                |push:"access_token: " ~ $env.ASAAS
                |push:"Content-Type: application/json"
                |push:"User-Agent: AutoGestao/1.0"
            } as $cliente_asaas_response
          
            precondition ($cliente_asaas_response.status >= 200 && $cliente_asaas_response.status < 300 && $cliente_asaas_response.body.id != null) {
              error_type = "badrequest"
              error = "Nao foi possivel criar o cliente no ASAAS"
            }
          
            db.add asaas_cliente {
              data = {
                cliente_id       : $cliente.id
                asaas_customer_id: $cliente_asaas_response.body.id
              }
            } as $cliente_asaas
          }
        }
      
        var $due_date {
          value = now
            |epoch_ms_add_days:30
            |format_timestamp:"Y-m-d":"UTC"
        }
      
        api.request {
          url = "https://api-sandbox.asaas.com/v3/payments"
          method = "POST"
          params = {
            customer   : $cliente_asaas.asaas_customer_id
            billingType: "UNDEFINED"
            value      : $venda.Valor_final
            dueDate    : $due_date
            description: ("Venda #" ~ $venda.id)
          }
        
          headers = []
            |push:"access_token: " ~ $env.ASAAS
            |push:"Content-Type: application/json"
            |push:"User-Agent: AutoGestao/1.0"
        } as $cobranca_asaas_response
      
        precondition ($cobranca_asaas_response.status >= 200 && $cobranca_asaas_response.status < 300 && $cobranca_asaas_response.body.id != null && $cobranca_asaas_response.body.invoiceUrl != null) {
          error_type = "badrequest"
          error = "Nao foi possivel criar a cobranca no ASAAS"
        }
      
        db.add asaas_cobranca {
          data = {
            venda_id        : $venda.id
            asaas_payment_id: $cobranca_asaas_response.body.id
            invoice_url     : $cobranca_asaas_response.body.invoiceUrl
            status          : ($cobranca_asaas_response.body.status ?? "PENDING")
            due_date        : $due_date
          }
        } as $cobranca_existente
      }
    }
  }

  response = {
    venda_id        : $venda.id
    asaas_payment_id: $cobranca_existente.asaas_payment_id
    invoice_url     : $cobranca_existente.invoice_url
    status          : $cobranca_existente.status
    due_date        : $cobranca_existente.due_date
  }

  guid = "DQL8iqkM9CRlIOHbmZPUgqCXJdI"
}