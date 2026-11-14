// Cancela reserva local, encerra parcelas pendentes e devolve itens ao estoque
query "vendas/{id}/cancelar" verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  
    text motivo filters=trim
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    precondition ($perfil != null && ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador")) {
      error_type = "accessdenied"
      error = "Apenas Gerente ou Administrador podem cancelar vendas"
    }
  
    precondition (($input.motivo|strlen) > 0) {
      error_type = "inputerror"
      error = "Motivo do cancelamento e obrigatorio"
    }
  
    db.get venda {
      field_name = "id"
      field_value = $input.id
    } as $venda
  
    precondition ($venda != null) {
      error_type = "notfound"
      error = "Venda nao encontrada"
    }
  
    db.get status_venda {
      field_name = "id"
      field_value = $venda.status_id
    } as $status_atual
  
    db.query status_venda {
      where = $db.status_venda.Descricao_venda == "Cancelada"
      return = {type: "single"}
    } as $status_cancelada
  
    precondition ($status_cancelada != null) {
      error = "Status Cancelada nao configurado no sistema"
    }
  
    db.query status_veiculo {
      where = $db.status_veiculo.Descricao == "Disponível" || $db.status_veiculo.Descricao == "Disponivel"
      return = {type: "single"}
    } as $status_disp
  
    precondition ($status_disp != null) {
      error = "Status Disponivel nao configurado no sistema"
    }
  
    conditional {
      if ($status_atual.Descricao_venda == "Cancelada") {
        var $venda_final {
          value = $venda
        }
      }
    
      else {
        precondition ($status_atual.Descricao_venda == "Reservado") {
          error_type = "badrequest"
          error = "Apenas vendas com status Reservado podem ser canceladas"
        }
      
        db.query venda_parcela {
          where = $db.venda_parcela.venda_id == $venda.id && $db.venda_parcela.status == "RECEBIDA"
          return = {type: "exists"}
        } as $tem_parcela_recebida
      
        precondition ($tem_parcela_recebida == false) {
          error_type = "badrequest"
          error = "Nao e permitido cancelar venda com parcelas recebidas"
        }
      
        db.transaction {
          stack {
            db.query venda_parcela {
              where = $db.venda_parcela.venda_id == $venda.id && $db.venda_parcela.status == "RECEBIDA"
              return = {type: "exists"}
            } as $tem_parcela_recebida_transacao
          
            precondition ($tem_parcela_recebida_transacao == false) {
              error_type = "badrequest"
              error = "Nao e permitido cancelar venda com parcelas recebidas"
            }
          
            db.patch venda {
              field_name = "id"
              field_value = $venda.id
              data = {
                status_id    : $status_cancelada.id
                cancel_reason: $input.motivo
                cancelled_at : now
              }
            } as $venda_cancelada
          
            db.query venda_parcela {
              where = $db.venda_parcela.venda_id == $venda.id && $db.venda_parcela.status == "PENDENTE"
              return = {type: "list"}
            } as $parcelas_pendentes
          
            foreach ($parcelas_pendentes) {
              each as $parcela_pendente {
                db.patch venda_parcela {
                  field_name = "id"
                  field_value = $parcela_pendente.id
                  data = {
                    status      : "CANCELADA"
                    cancelada_em: now
                    updated_at  : now
                  }
                } as $parcela_cancelada
              }
            }
          
            db.query venda_item {
              where = $db.venda_item.venda_id == $venda.id
              return = {type: "list"}
            } as $itens_cancelar
          
            foreach ($itens_cancelar) {
              each as $item_canc {
                conditional {
                  if ($item_canc.veiculo_id != null) {
                    db.patch veiculo {
                      field_name = "id"
                      field_value = $item_canc.veiculo_id
                      data = {status_id: $status_disp.id}
                    } as $veiculo_liberado
                  }
                
                  elseif ($item_canc.peca_id != null) {
                    db.get peca {
                      field_name = "id"
                      field_value = $item_canc.peca_id
                    } as $peca_item
                  
                    conditional {
                      if ($peca_item != null) {
                        var $qtd_devolvida {
                          value = ($peca_item.qtd_disp ?? 0) + $item_canc.qtd
                        }
                      
                        db.patch peca {
                          field_name = "id"
                          field_value = $peca_item.id
                          data = {qtd_disp: $qtd_devolvida}
                        } as $peca_devolvida
                      }
                    }
                  }
                }
              }
            }
          }
        }
      
        var $venda_final {
          value = $venda_cancelada
        }
      }
    }
  }

  response = {
    id              : $venda_final.id
    status_id       : $status_cancelada.id
    status_descricao: $status_cancelada.Descricao_venda
    cancel_reason   : $venda_final.cancel_reason
    cancelled_at    : $venda_final.cancelled_at
    mensagem        : "Venda cancelada e parcelas locais encerradas"
  }

  test "rejeita cancelamento de venda inexistente" {
    input = {id: 999999, motivo: "Venda inexistente"}
  
    expect.to_throw {
      exception = ""
    }
  }

  guid = "q7BLpojytalgAEozirGnnSZwVwI"
}