// Ajuste absoluto de estoque com validacao de reservas ativas
// Ajusta a quantidade disponivel de uma peca impedindo reducao abaixo das reservas em vendas ativas
// Identificador da peca e nova quantidade absoluta
query "pecas/{id}/ajuste-estoque" verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "peca"
    }
  
    int qtd_disp filters=min:0
  }

  stack {
    // Validar permissao de perfil (Gerente ou Administrador)
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
      error = "Apenas Gerente ou Administrador podem ajustar o estoque"
    }
  
    // Buscar peca no banco
    db.get peca {
      field_name = "id"
      field_value = $input.id
    } as $peca
  
    precondition ($peca != null) {
      error_type = "notfound"
      error = "Peca nao encontrada"
    }
  
    // Consultar quantidade total reservada em vendas ativas (Reservado ou Paga)
    db.query venda_item {
      join = {
        venda       : {
          table: "venda"
          where: $db.venda_item.venda_id == $db.venda.id
        }
        status_venda: {
          table: "status_venda"
          where: $db.venda.status_id == $db.status_venda.id
        }
      }
    
      where = $db.venda_item.peca_id == $input.id && ($db.status_venda.Descricao_venda == "Reservado" || $db.status_venda.Descricao_venda == "Paga")
      return = {type: "list"}
    } as $itens_reservados
  
    // Somar as quantidades reservadas
    var $qtd_reservada {
      value = (($itens_reservados|map:$$.qtd)|sum) ?? 0
    }
  
    // Validar se o novo estoque respeita as reservas ativas
    precondition ($input.qtd_disp >= $qtd_reservada) {
      error_type = "badrequest"
      error = "A quantidade nao pode ser menor que a soma reservada em vendas ativas"
    }
  
    // Atualizar estoque no banco
    db.patch peca {
      field_name = "id"
      field_value = $input.id
      data = {qtd_disp: $input.qtd_disp}
    } as $peca_atualizada
  
    // Buscar secao/area vinculada
    var $area_secao {
      value = null
    }
  
    conditional {
      if ($peca_atualizada.area_id != null) {
        db.get veiculo_area {
          field_name = "id"
          field_value = $peca_atualizada.area_id
        } as $area
      
        conditional {
          if ($area != null) {
            var.update $area_secao {
              value = $area.Secao
            }
          }
        }
      }
    }
  }

  response = {
    id                 : $peca_atualizada.id
    PCNome             : $peca_atualizada.PCNome
    PCvalor            : $peca_atualizada.PCvalor
    qtd_disp           : $peca_atualizada.qtd_disp
    qtd_reservada_ativa: $qtd_reservada
    area_id            : $peca_atualizada.area_id
    area_secao         : $area_secao
    imagem_url         : $peca_atualizada.imagem_url
  }

  guid = "w7B3O-a4kkWtZceTE38K-It5iCw"
}