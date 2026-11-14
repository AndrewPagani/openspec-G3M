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
  
    precondition ($perfil != null && $perfil.Cargo == "Gerente") {
      error_type = "accessdenied"
      error = "Apenas Gerente pode confirmar recebimentos"
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
                    status           : "RECEBIDA"
                    forma_recebida_id: $forma_recebida.id
                    recebido_em      : now
                    recebido_por     : $auth.id
                    updated_at       : now
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
  
    // Garantir vencimento valido no retorno mesmo se a parcela original possuia data corrompida
    var $vencimento_final {
      value = $parcela_final.vencimento
    }
  
    conditional {
      if ($vencimento_final == null || (($vencimento_final|to_int) <= 0)) {
        var $p_ano {
          value = ($venda.data_venda|format_timestamp:"Y":"America/Sao_Paulo")|to_int
        }
      
        var $p_mes {
          value = ($venda.data_venda|format_timestamp:"n":"America/Sao_Paulo")|to_int
        }
      
        var $p_dia {
          value = ($venda.data_venda|format_timestamp:"j":"America/Sao_Paulo")|to_int
        }
      
        var $p_total_meses {
          value = ($p_ano * 12) + ($p_mes - 1) + ($parcela_final.numero_parcela - 1)
        }
      
        var $p_ano_alvo {
          value = ($p_total_meses / 12)|floor
        }
      
        var $p_mes_alvo {
          value = ($p_total_meses % 12) + 1
        }
      
        var $p_max_dias {
          value = 31
        }
      
        conditional {
          if ($p_mes_alvo == 4 || $p_mes_alvo == 6 || $p_mes_alvo == 9 || $p_mes_alvo == 11) {
            var.update $p_max_dias {
              value = 30
            }
          }
        
          elseif ($p_mes_alvo == 2) {
            conditional {
              if (($p_ano_alvo % 4 == 0 && $p_ano_alvo % 100 != 0) || ($p_ano_alvo % 400 == 0)) {
                var.update $p_max_dias {
                  value = 29
                }
              }
            
              else {
                var.update $p_max_dias {
                  value = 28
                }
              }
            }
          }
        }
      
        var $p_dia_final {
          value = ($p_dia > $p_max_dias) ? $p_max_dias : $p_dia
        }
      
        var $p_mes_str {
          value = ($p_mes_alvo < 10) ? ("0" ~ ($p_mes_alvo|to_text)) : ($p_mes_alvo|to_text)
        }
      
        var $p_dia_str {
          value = ($p_dia_final < 10) ? ("0" ~ ($p_dia_final|to_text)) : ($p_dia_final|to_text)
        }
      
        var.update $vencimento_final {
          value = (($p_ano_alvo|to_text) ~ "-" ~ $p_mes_str ~ "-" ~ $p_dia_str ~ "T12:00:00Z")|to_timestamp
        }
      }
    }
  }

  response = {
    venda_id      : $input.id
    id            : $parcela_final.id
    numero_parcela: $parcela_final.numero_parcela
    total_parcelas: $parcela_final.total_parcelas
    valor         : $parcela_final.valor
    vencimento    : $vencimento_final
    status        : $parcela_final.status
    forma_recebida: ($forma_final.Metodo ?? null)
    recebido_em   : $parcela_final.recebido_em
    recebido_por  : $parcela_final.recebido_por
    status_venda  : ($status_venda_final.Descricao_venda ?? "")
  }

  guid = "7I6SdNjYCv-HXWOsgkmDr2E6G5c"
}