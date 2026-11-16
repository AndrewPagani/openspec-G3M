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
      if ($venda.payment_flow == "ASAAS") {
        db.query asaas_cobranca {
    where = $db.asaas_cobranca.venda_id == $venda.id
    return = {type: "single"} } as $billing
        conditional {
          if ($billing != null) {
            function.run "asaas/reconcile" { input = {payment_id: $billing.asaas_payment_id} } as $live_state
            precondition ($live_state.status == "PENDING" || $live_state.status == "OVERDUE" || $live_state.status == "DELETED") {

    error_type = "badrequest"
    error = "Cobranca recebida ou em processamento; nao liberar estoque"
            }
            conditional {
              if ($live_state.status != "DELETED") {
                function.run "asaas/request" { input = {method: "DELETE", path: "/payments/" ~ $billing.asaas_payment_id} } as $deleted
                precondition ($deleted.deleted == true) {
    error_type = "badrequest"
    error = "Cancelamento ASAAS nao confirmado; reserva preservada" }
              }
            }
            db.patch asaas_cobranca {
    field_name = "id"
    field_value = $billing.id
    data = {status: "DELETED"} } as $cancelled_billing
          }
          else {
            precondition ($venda.asaas_request_state == null || $venda.asaas_request_state == "") {

    error_type = "badrequest"
    error = "Tentativa de cobranca incerta; recuperar antes de cancelar"
            }
          }
        }
      }
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
            db.query venda {
    where = $db.venda.id == $venda.id
    lock = true
    return = {type: "single"} } as $locked_cancel
            precondition ($locked_cancel.status_id == $status_atual.id) {
    error_type = "badrequest"
    error = "Venda alterada; atualize antes de cancelar" }
            precondition ($locked_cancel.asaas_request_state != "SENDING" && $locked_cancel.asaas_request_state != "LOOKUP") {
    error_type = "badrequest"
    error = "Cobranca em andamento; reserva preservada" }
            conditional {
              if ($locked_cancel.payment_flow == "ASAAS") {
                db.query asaas_cobranca {
    where = $db.asaas_cobranca.venda_id == $venda.id
    return = {type: "single"} } as $billing_locked
                precondition (($billing_locked != null && $billing_locked.status == "DELETED") || ($billing_locked == null && ($locked_cancel.asaas_request_state == null || $locked_cancel.asaas_request_state == ""))) {

    error_type = "badrequest"
    error = "Cobranca criada durante cancelamento; recuperar antes de liberar estoque"
                }
              }
            }

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
                    db.query veiculo {

    where = $db.veiculo.id == $item_canc.veiculo_id

    lock = true

    return = {type: "single"}
                    } as $veiculo_cancelar
                    db.patch veiculo {

    field_name = "id"

    field_value = $item_canc.veiculo_id

    data = {status_id: $status_disp.id}
                    } as $veiculo_liberado
                  }

                  elseif ($item_canc.peca_id != null) {
                    db.query peca {

    where = $db.peca.id == $item_canc.peca_id

    lock = true

    return = {type: "single"}
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
