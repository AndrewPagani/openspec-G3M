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
  
    // Buscar ID do status Disponivel na tabela de referencia
    db.query status_veiculo {
      where = $db.status_veiculo.Descricao == "Disponível" || $db.status_veiculo.Descricao == "Disponivel"
      return = {type: "single"}
    } as $status_disp
  
    precondition ($status_disp != null) {
      error = "Configuracao de status Disponivel nao encontrada"
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
        status_id    : $status_disp.id
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
    status_id       : $novo_veiculo.status_id
    status_descricao: $status_disp.Descricao
    created_at      : $novo_veiculo.created_at
  }

  guid = "zBsu_R6R3FhUoEKzNOWE2eVvfjU"
}