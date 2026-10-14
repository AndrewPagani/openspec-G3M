// Cadastro de veiculo com status inicial Disponivel
// Cadastra um novo veiculo definindo o status inicial Disponivel e validando placa e chassi
// Dados cadastrais do veiculo
query veiculos verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    text Marca filters=trim
    text Modelo filters=trim
    text Cor filters=trim
    int Ano filters=min:1900|max:2100
    text Placa? filters=trim
    text Chassi? filters=trim
    decimal Quilometragem? filters=min:0
    decimal Preco filters=min:0
    text Imagem_url? filters=trim
    int status_id?
  }

  stack {
    // Validar preenchimento dos campos de texto obrigatorios
    precondition (($input.Marca|strlen) > 0 && ($input.Modelo|strlen) > 0 && ($input.Cor|strlen) > 0) {
      error_type = "inputerror"
      error = "Marca, Modelo e Cor sao obrigatorios"
    }
  
    // Verificar unicidade de Placa quando informada
    conditional {
      if ($input.Placa != null && ($input.Placa|strlen) > 0) {
        db.query veiculo {
          where = $db.veiculo.Placa == $input.Placa
          return = {type: "single"}
        } as $placa_existente
      
        precondition ($placa_existente == null) {
          error_type = "badrequest"
          error = "Placa ja cadastrada em outro veiculo"
        }
      }
    }
  
    // Verificar unicidade de Chassi quando informado
    conditional {
      if ($input.Chassi != null && ($input.Chassi|strlen) > 0) {
        db.query veiculo {
          where = $db.veiculo.Chassi == $input.Chassi
          return = {type: "single"}
        } as $chassi_existente
      
        precondition ($chassi_existente == null) {
          error_type = "badrequest"
          error = "Chassi ja cadastrado em outro veiculo"
        }
      }
    }
  
    // Aceitar status escolhido no cadastro e preservar Disponivel como padrao legado
    var $status_inicial {
      value = null
    }

    conditional {
      if ($input.status_id != null) {
        db.get user {
          field_name = "id"
          field_value = $auth.id
        } as $usuario

        db.get perfil {
          field_name = "id"
          field_value = $usuario.perfil_id
        } as $perfil_usuario

        precondition ($perfil_usuario.Cargo == "Gerente" || $perfil_usuario.Cargo == "Administrador") {
          error_type = "accessdenied"
          error = "Somente gerente ou administrador pode escolher o status inicial"
        }

        db.get status_veiculo {
          field_name = "id"
          field_value = $input.status_id
        } as $status_selecionado

        precondition ($status_selecionado != null) {
          error_type = "badrequest"
          error = "Status de veiculo informado nao existe"
        }

        var.update $status_inicial {
          value = $status_selecionado
        }
      }

      else {
        db.query status_veiculo {
          where = $db.status_veiculo.Descricao == "Disponível" || $db.status_veiculo.Descricao == "Disponivel"
          return = {type: "single"}
        } as $status_disp

        precondition ($status_disp != null) {
          error = "Configuracao de status Disponivel nao encontrada"
        }

        var.update $status_inicial {
          value = $status_disp
        }
      }
    }
  
    // Inserir registro do veiculo
    db.add veiculo {
      data = {
        Marca        : $input.Marca
        Modelo       : $input.Modelo
        Cor          : $input.Cor
        Ano          : $input.Ano
        Placa        : $input.Placa
        Chassi       : $input.Chassi
        Quilometragem: $input.Quilometragem
        Preco        : $input.Preco
        status_id    : $status_inicial.id
        Imagem_url   : $input.Imagem_url
        created_at   : now
      }
    } as $novo_veiculo
  }

  response = {
    id              : $novo_veiculo.id
    Marca           : $novo_veiculo.Marca
    Modelo          : $novo_veiculo.Modelo
    Cor             : $novo_veiculo.Cor
    Ano             : $novo_veiculo.Ano
    Placa           : $novo_veiculo.Placa
    Chassi          : $novo_veiculo.Chassi
    Quilometragem   : $novo_veiculo.Quilometragem
    Preco           : $novo_veiculo.Preco
    Imagem_url      : $novo_veiculo.Imagem_url
    status_id       : $novo_veiculo.status_id
    status_descricao: $status_inicial.Descricao
    created_at      : $novo_veiculo.created_at
  }

  guid = "zBsu_R6R3FhUoEKzNOWE2eVvfjU"
}