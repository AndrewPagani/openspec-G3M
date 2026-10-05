// Alteracao de status do veiculo com validacao de perfil
// Permite a Gerente e Administrador alterar o status do veiculo respeitando regras de transicao
// Identificador do veiculo e novo status
query "veiculos/{id}/status" verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "veiculo"
    }
  
    int status_id {
      table = "status_veiculo"
    }
  }

  stack {
    // Validar permissao de perfil do usuario autenticado
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
      error = "Apenas Gerente ou Administrador podem alterar o status do veiculo"
    }
  
    // Buscar veiculo atual
    db.get veiculo {
      field_name = "id"
      field_value = $input.id
    } as $veiculo
  
    precondition ($veiculo != null) {
      error_type = "notfound"
      error = "Veiculo nao encontrado"
    }
  
    // Buscar status atual
    db.get status_veiculo {
      field_name = "id"
      field_value = $veiculo.status_id
    } as $status_atual
  
    // Impedir alteracao manual de veiculo ja vendido ou reservado
    precondition ($status_atual.Descricao != "Vendido" && $status_atual.Descricao != "Reservado") {
      error_type = "badrequest"
      error = "Nao e permitida a alteracao de status de veiculo vendido ou reservado"
    }
  
    // Verificar se esta associado a venda ativa
    db.query venda {
      join = {
        venda_item  : {
          table: "venda_item"
          where: $db.venda.id == $db.venda_item.venda_id
        }
        status_venda: {
          table: "status_venda"
          where: $db.venda.status_id == $db.status_venda.id
        }
      }
    
      where = $db.venda_item.veiculo_id == $input.id && ($db.status_venda.Descricao_venda == "Reservado" || $db.status_venda.Descricao_venda == "Paga")
      return = {type: "exists"}
    } as $em_venda_ativa
  
    precondition ($em_venda_ativa == false) {
      error_type = "badrequest"
      error = "Veiculo associado a uma venda ativa nao pode ter seu status alterado manualmente"
    }
  
    // Validar status de destino
    db.get status_veiculo {
      field_name = "id"
      field_value = $input.status_id
    } as $novo_status
  
    precondition ($novo_status != null) {
      error_type = "badrequest"
      error = "Status informado nao existe"
    }
  
    precondition ($novo_status.Descricao != "Vendido") {
      error_type = "badrequest"
      error = "Status Vendido so pode ser definido pela entrega da venda"
    }
  
    // Atualizar status no banco
    db.patch veiculo {
      field_name = "id"
      field_value = $input.id
      data = {status_id: $input.status_id}
    } as $veiculo_atualizado
  }

  response = {
    id              : $veiculo_atualizado.id
    Marca           : $veiculo_atualizado.Marca
    Modelo          : $veiculo_atualizado.Modelo
    Cor             : $veiculo_atualizado.Cor
    Ano             : $veiculo_atualizado.Ano
    Placa           : $veiculo_atualizado.Placa
    Chassi          : $veiculo_atualizado.Chassi
    Quilometragem   : $veiculo_atualizado.Quilometragem
    Preco           : $veiculo_atualizado.Preco
    status_id       : $veiculo_atualizado.status_id
    status_descricao: $novo_status.Descricao
    created_at      : $veiculo_atualizado.created_at
  }

  guid = "WLrIrajDXt_JNUfLVxX4P3q363k"
}