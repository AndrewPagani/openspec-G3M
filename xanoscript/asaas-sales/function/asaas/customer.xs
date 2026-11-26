// Recupera vinculo e confirma notificacoes desabilitadas antes de qualquer cobranca.
function "asaas/customer" {
  input { int cliente_id }
  stack {
    db.get cliente {
    field_name = "id"
    field_value = $input.cliente_id } as $cliente
    precondition ($cliente != null) {
    error_type = "notfound"
    error = "Cliente nao encontrado" }
    db.query asaas_cliente {

    where = $db.asaas_cliente.cliente_id == $cliente.id

    return = {type: "single"}
    } as $link
    var $customer_id { value = $link.asaas_customer_id ?? "" }
    var $reference { value = "cliente-" ~ $cliente.id }
    var $cpf { value = "/[^0-9]/"|regex_replace:"":$cliente.CPF }
    conditional {
      if ($customer_id == "") {
        function.run "asaas/request" {
          input = {method: "GET", path: "/customers", body: {cpfCnpj: $cpf, limit: 100}}
        } as $found
        precondition (($found.totalCount ?? 0) <= 1 && ($found.data|count) <= 1 && $found.hasMore != true) {

    error_type = "badrequest"
    error = "Mais de um cliente ASAAS para este CPF; reconciliar antes de continuar"
        }
        conditional {
          if (($found.data|count) == 1) {
            var $matched { value = $found.data|first }
            precondition ($matched.id != null && $matched.cpfCnpj == $cpf) {
              error_type = "badrequest"
              error = "O CPF retornado pelo ASAAS diverge do cadastro local"
            }
            var.update $customer_id { value = $matched.id }
          }
          else {
            // A marca fica persistida se o POST sofrer timeout. Nunca reenviar cegamente.
            db.transaction {
              stack {
                db.query cliente {

    where = $db.cliente.id == $cliente.id

    lock = true

    return = {type: "single"}
                } as $locked
                precondition ($locked.asaas_sync_state == null || $locked.asaas_sync_state == "") {

    error_type = "badrequest"
    error = "Cadastro ASAAS com resultado incerto; reconciliar antes de nova criacao"
                }
                db.patch cliente {

    field_name = "id"
    field_value = $cliente.id
    data = {asaas_sync_state: "SENDING"}
                } as $marked
              }
            }
            function.run "asaas/request" {
              input = {method: "POST", path: "/customers", body: {
                name: $cliente.CNome, cpfCnpj: $cpf, email: $cliente.Email,
                mobilePhone: $cliente.Telefone, externalReference: $reference, notificationDisabled: true
              }}
            } as $created
            precondition ($created.id != null) {
    error_type = "badrequest"
    error = "ASAAS nao retornou cliente; reconciliar tentativa" }
            var.update $customer_id { value = $created.id }
          }
        }
        db.transaction {
          stack {
            db.query cliente {
    where = $db.cliente.id == $cliente.id
    lock = true
    return = {type: "single"} } as $locked_link
            precondition ($locked_link != null && $locked_link.CPF == $cliente.CPF) {
              error_type = "badrequest"
              error = "Cadastro do cliente alterado; tente novamente"
            }
            db.query asaas_cliente {
    where = $db.asaas_cliente.cliente_id == $cliente.id
    return = {type: "single"} } as $existing
            conditional {
              if ($existing == null) {
                db.query asaas_cliente {
                  where = $db.asaas_cliente.asaas_customer_id == $customer_id
                  lock = true
                  return = {type: "single"}
                } as $previous_link
                conditional {
                  if ($previous_link == null) {
                    db.add asaas_cliente {
                      data = {cliente_id: $cliente.id, asaas_customer_id: $customer_id}
                    } as $saved
                  }
                  else {
                    db.get cliente {
                      field_name = "id"
                      field_value = $previous_link.cliente_id
                    } as $previous_customer
                    precondition ($previous_customer == null) {
                      error_type = "badrequest"
                      error = "ID ASAAS pertence a outro cliente ativo; revise o cadastro"
                    }
                    db.patch asaas_cliente {
                      field_name = "id"
                      field_value = $previous_link.id
                      data = {cliente_id: $cliente.id}
                    } as $relinked
                  }
                }
              }
              else {
                precondition ($existing.asaas_customer_id == $customer_id) {
    error_type = "badrequest"
    error = "Vinculo ASAAS divergente" }
              }
            }
          }
        }
      }
    }
    function.run "asaas/request" {
      input = {method: "PUT", path: "/customers/" ~ $customer_id, body: {notificationDisabled: true}}
    } as $muted
    function.run "asaas/request" {
      input = {method: "GET", path: "/customers/" ~ $customer_id ~ "/notifications", body: {limit: 100}}
    } as $notifications
    precondition ($notifications.hasMore != true) {
    error_type = "badrequest"
    error = "Revisar todas as notificacoes ASAAS antes de cobrar" }
    foreach ($notifications.data) {
      each as $notification {
        function.run "asaas/request" {
          input = {method: "PUT", path: "/notifications/" ~ $notification.id, body: {
            enabled: false, emailEnabledForProvider: false, emailEnabledForCustomer: false,
            smsEnabledForProvider: false, smsEnabledForCustomer: false,
            phoneCallEnabledForCustomer: false, whatsappEnabledForCustomer: false
          }}
        } as $disabled
        precondition ($disabled.enabled == false) {
    error_type = "badrequest"
    error = "Nao foi possivel desativar notificacoes ASAAS" }
      }
    }
    function.run "asaas/request" {
      input = {method: "GET", path: "/customers/" ~ $customer_id ~ "/notifications", body: {limit: 100}}
    } as $verified
    precondition ($verified.hasMore != true && (($verified.data|filter:$$.enabled == true)|count) == 0) {

    error_type = "badrequest"
    error = "Notificacoes ASAAS ainda habilitadas"
    }
    db.patch cliente {
    field_name = "id"
    field_value = $cliente.id
    data = {asaas_sync_state: "SYNCED"} } as $synced
  }
  response = {id: $customer_id}

  guid = "GHxjS_JaKmJpUWdNjeHK1B7GtBk"
}
