// Entrega e conclusao de venda paga
// Registra a conclusao de uma venda Paga marcando os veiculos como Vendidos de forma atomica e idempotente
// Identificador da venda a ser entregue
query "vendas/{id}/entregar" verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  }

  stack {
    // Buscar venda no banco
    db.get venda {
      field_name = "id"
      field_value = $input.id
    } as $venda
  
    precondition ($venda != null) {
      error_type = "notfound"
      error = "Venda nao encontrada"
    }
  
    // Validar permissao de perfil (vendedor so entrega suas proprias vendas)
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    conditional {
      if ($perfil.Cargo == "Vendedor") {
        precondition ($venda.vendedor_id == $auth.id) {
          error_type = "notfound"
          error = "Venda nao encontrada"
        }
      }
    }
  
    // Buscar status atual da venda
    db.get status_venda {
      field_name = "id"
      field_value = $venda.status_id
    } as $status_atual
  
    // Resolver status Concluida e Vendido
    db.query status_venda {
      where = $db.status_venda.Descricao_venda == "Concluída" || $db.status_venda.Descricao_venda == "Concluida"
      return = {type: "single"}
    } as $status_concluida
  
    precondition ($status_concluida != null) {
      error = "Status Concluida nao configurado no sistema"
    }
  
    db.query status_veiculo {
      where = $db.status_veiculo.Descricao == "Vendido"
      return = {type: "single"}
    } as $status_vendido
  
    precondition ($status_vendido != null) {
      error = "Status de veiculo Vendido nao configurado no sistema"
    }
  
    // Idempotencia: se ja estiver concluida, retornar imediatamente
    conditional {
      if ($status_atual.Descricao_venda == "Concluída" || $status_atual.Descricao_venda == "Concluida") {
        var $venda_final {
          value = $venda
        }
      }
    
      else {
        // Exigir status Paga
        precondition ($status_atual.Descricao_venda == "Paga") {
          error_type = "badrequest"
          error = "Apenas vendas com status Paga podem ser entregues"
        }
      
        // Executar transacao atomica: concluir venda e marcar veiculo como Vendido
        db.transaction {
          stack {
            db.patch venda {
              field_name = "id"
              field_value = $venda.id
              data = {status_id: $status_concluida.id}
            } as $venda_atualizada
          
            db.query venda_item {
              where = $db.venda_item.venda_id == $venda.id
              return = {type: "list"}
            } as $itens_venda
          
            foreach ($itens_venda) {
              each as $item_entregar {
                conditional {
                  if ($item_entregar.veiculo_id != null) {
                    db.patch veiculo {
                      field_name = "id"
                      field_value = $item_entregar.veiculo_id
                      data = {status_id: $status_vendido.id}
                    } as $veiculo_atualizado
                  }
                }
              }
            }
          }
        }
      
        var $venda_final {
          value = $venda_atualizada
        }
      }
    }
  }

  response = {
    id              : $venda_final.id
    status_id       : $status_concluida.id
    status_descricao: $status_concluida.Descricao_venda
    cliente_id      : $venda_final.cliente_id
    vendedor_id     : $venda_final.vendedor_id
    Valor_final     : $venda_final.Valor_final
    mensagem        : "Venda concluida e itens entregues com sucesso"
  }

  guid = "uaZMBgybh5Cy1OAMy1CLbN4dQ1g"
}