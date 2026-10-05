// Atualizacao de dados cadastrais do veiculo
// Atualiza atributos cadastrais do veiculo impedindo alteracao se vinculado a venda ativa
// Identificador do veiculo e atributos editaveis
query "veiculos/{id}" verb=PATCH {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "veiculo"
    }
  
    text Marca? filters=trim
    text Modelo? filters=trim
    text Cor? filters=trim
    int Ano? filters=min:1900|max:2100
    text Placa? filters=trim
    text Chassi? filters=trim
    decimal Quilometragem? filters=min:0
    decimal Preco? filters=min:0
  }

  stack {
    // Buscar veiculo atual
    db.get veiculo {
      field_name = "id"
      field_value = $input.id
    } as $veiculo
  
    precondition ($veiculo != null) {
      error_type = "notfound"
      error = "Veiculo nao encontrado"
    }
  
    // Verificar se o veiculo esta vinculado a venda ativa (Reservado ou Paga)
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
      error = "Veiculo associado a uma venda ativa nao pode ser alterado"
    }
  
    // Inicializar mapa de atualizacoes
    var $updates {
      value = {}
    }
  
    conditional {
      if ($input.Marca != null && ($input.Marca|strlen) > 0) {
        var.update $updates {
          value = $updates|set:"Marca":$input.Marca
        }
      }
    }
  
    conditional {
      if ($input.Modelo != null && ($input.Modelo|strlen) > 0) {
        var.update $updates {
          value = $updates|set:"Modelo":$input.Modelo
        }
      }
    }
  
    conditional {
      if ($input.Cor != null && ($input.Cor|strlen) > 0) {
        var.update $updates {
          value = $updates|set:"Cor":$input.Cor
        }
      }
    }
  
    conditional {
      if ($input.Ano != null) {
        var.update $updates {
          value = $updates|set:"Ano":$input.Ano
        }
      }
    }
  
    conditional {
      if ($input.Placa != null && ($input.Placa|strlen) > 0) {
        db.query veiculo {
          where = $db.veiculo.Placa == $input.Placa && $db.veiculo.id != $input.id
          return = {type: "single"}
        } as $placa_check
      
        precondition ($placa_check == null) {
          error_type = "badrequest"
          error = "Placa ja cadastrada em outro veiculo"
        }
      
        var.update $updates {
          value = $updates|set:"Placa":$input.Placa
        }
      }
    }
  
    conditional {
      if ($input.Chassi != null && ($input.Chassi|strlen) > 0) {
        db.query veiculo {
          where = $db.veiculo.Chassi == $input.Chassi && $db.veiculo.id != $input.id
          return = {type: "single"}
        } as $chassi_check
      
        precondition ($chassi_check == null) {
          error_type = "badrequest"
          error = "Chassi ja cadastrado em outro veiculo"
        }
      
        var.update $updates {
          value = $updates|set:"Chassi":$input.Chassi
        }
      }
    }
  
    conditional {
      if ($input.Quilometragem != null) {
        var.update $updates {
          value = $updates
            |set:"Quilometragem":$input.Quilometragem
        }
      }
    }
  
    conditional {
      if ($input.Preco != null) {
        var.update $updates {
          value = $updates|set:"Preco":$input.Preco
        }
      }
    }
  
    // Gravar alteracoes
    conditional {
      if (($updates|is_empty) == false) {
        db.patch veiculo {
          field_name = "id"
          field_value = $input.id
          data = $updates
        } as $veiculo_atualizado
      }
    
      else {
        var $veiculo_atualizado {
          value = $veiculo
        }
      }
    }
  
    // Buscar descricao do status
    db.get status_veiculo {
      field_name = "id"
      field_value = $veiculo_atualizado.status_id
    } as $status
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
    status_descricao: ($status.Descricao ?? "")
    created_at      : $veiculo_atualizado.created_at
  }

  guid = "Kt5-0xB-Jalp_6FmeyB_XM_k_QM"
}