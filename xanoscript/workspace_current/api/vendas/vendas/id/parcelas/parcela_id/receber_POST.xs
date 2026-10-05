// Registra manualmente o recebimento integral de uma parcela local
query "vendas/{id}/parcelas/{parcela_id}/receber" verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  
    int parcela_id {
      table = "venda_parcela"
    }
  
    int forma_pagamento_id {
      table = "forma_pagamento"
    }
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $usuario
  
    db.get perfil {
      field_name = "id"
      field_value = $usuario.perfil_id
    } as $perfil
  
    precondition ($perfil != null && ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador")) {
      error_type = "accessdenied"
      error = "Apenas Gerente ou Administrador podem confirmar recebimentos"
    }
  
    db.get venda {
      field_name = "id"
      field_value = $input.id
    } as $venda
  
    precondition ($venda != null) {
      error_type = "notfound"
      error = "Venda nao encontrada"
    }
  
    db.get venda_parcela {
      field_name = "id"
      field_value = $input.parcela_id
    } as $parcela
  
    precondition ($parcela != null && $parcela.venda_id == $venda.id) {
      error_type = "notfound"
      error = "Parcela nao encontrada para esta venda"
    }
  
    db.get status_venda {
      field_name = "id"
      field_value = $venda.status_id
    } as $status_venda
  
    conditional {
      if ($parcela.status == "RECEBIDA") {
        var $parcela_final {
          value = $parcela
        }
      
        var $status_venda_final {
          value = $status_venda
        }
      }
    
      else {
        precondition ($parcela.status == "PENDENTE") {
          error_type = "badrequest"
          error = "Somente parcelas pendentes podem ser recebidas"
        }
      
        precondition ($status_venda.Descricao_venda == "Reservado" || $status_venda.Descricao_venda == "Paga") {
          error_type = "badrequest"
          error = "A venda nao permite novos recebimentos"
        }
      
        db.get forma_pagamento {
          field_name = "id"
          field_value = $input.forma_pagamento_id
        } as $forma_recebida
      
        precondition ($forma_recebida != null) {
          error_type = "badrequest"
          error = "Forma de pagamento recebida invalida"
        }
      
        db.transaction {
          stack {
            db.get venda {
              field_name = "id"
              field_value = $venda.id
            } as $venda_transacao
          
            db.get status_venda {
              field_name = "id"
              field_value = $venda_transacao.status_id
            } as $status_venda_transacao
          
            db.get venda_parcela {
              field_name = "id"
              field_value = $parcela.id
            } as $parcela_transacao
          
            conditional {
              if ($parcela_transacao.status == "RECEBIDA") {
                var $parcela_final {
                  value = $parcela_transacao
                }
              
                var $status_venda_final {
                  value = $status_venda_transacao
                }
              }
            
              else {
                precondition ($parcela_transacao.status == "PENDENTE") {
                  error_type = "badrequest"
                  error = "Somente parcelas pendentes podem ser recebidas"
                }
              
                precondition ($status_venda_transacao.Descricao_venda == "Reservado" || $status_venda_transacao.Descricao_venda == "Paga") {
                  error_type = "badrequest"
                  error = "A venda nao permite novos recebimentos"
                }
              
                db.patch venda_parcela {
                  field_name = "id"
                  field_value = $parcela_transacao.id
                  data = {
                    status             : "RECEBIDA"
                    forma_recebida_id  : $forma_recebida.id
                    recebido_em        : now
                    recebido_por       : $auth.id
                    updated_at         : now
                  }
                } as $parcela_recebida
              
                var $parcela_final {
                  value = $parcela_recebida
                }
              
                var $status_venda_final {
                  value = $status_venda_transacao
                }
              
                conditional {
                  if ($parcela_transacao.numero_parcela == 1 && $status_venda_transacao.Descricao_venda == "Reservado") {
                    db.query status_venda {
                      where = $db.status_venda.Descricao_venda == "Paga"
                      return = {type: "single"}
                    } as $status_pago
                  
                    precondition ($status_pago != null) {
                      error = "Status Paga nao configurado no sistema"
                    }
                  
                    db.patch venda {
                      field_name = "id"
                      field_value = $venda_transacao.id
                      data = {status_id: $status_pago.id}
                    } as $venda_paga
                  
                    var.update $status_venda_final {
                      value = $status_pago
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  
    db.get forma_pagamento {
      field_name = "id"
      field_value = $parcela_final.forma_recebida_id
    } as $forma_final
  }

  response = {
    venda_id          : $input.id
    id                : $parcela_final.id
    numero_parcela    : $parcela_final.numero_parcela
    total_parcelas    : $parcela_final.total_parcelas
    valor             : $parcela_final.valor
    vencimento        : $parcela_final.vencimento
    status            : $parcela_final.status
    forma_recebida    : ($forma_final.Metodo ?? null)
    recebido_em       : $parcela_final.recebido_em
    recebido_por      : $parcela_final.recebido_por
    status_venda      : ($status_venda_final.Descricao_venda ?? "")
  }

  guid = "7I6SdNjYCv-HXWOsgkmDr2E6G5c"
}
