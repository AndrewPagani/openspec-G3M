// Detalhes de um veiculo especifico com envelope de veiculo e veiculo_detalhe
// Retorna os detalhes de um veiculo e seus detalhes cadastrais
// Identificador do veiculo
query "veiculos/{id}" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "veiculo"
    }
  }

  stack {
    // Buscar veiculo pelo ID
    db.get veiculo {
      field_name = "id"
      field_value = $input.id
    } as $veiculo
  
    precondition ($veiculo != null) {
      error_type = "notfound"
      error = "Veiculo nao encontrado"
    }
  
    // Buscar descricao do status
    db.get status_veiculo {
      field_name = "id"
      field_value = $veiculo.status_id
    } as $status
  
    // Buscar registro correspondente em veiculo_detalhe usando veiculo_id
    db.query veiculo_detalhe {
      where = $db.veiculo_detalhe.veiculo_id == $input.id
      return = {type: "single"}
    } as $detalhes
  
    // Montar objeto de detalhes ou objeto vazio caso nao exista
    var $detalhes_envelope {
      value = {}
    }
  
    conditional {
      if ($detalhes != null) {
        var.update $detalhes_envelope {
          value = {
            id             : $detalhes.id
            veiculo_id     : $detalhes.veiculo_id
            uf_registro    : $detalhes.uf_registro
            cidade_registro: $detalhes.cidade_registro
            ano_fabricacao : $detalhes.ano_fabricacao
            motorizacao    : $detalhes.motorizacao
            combustivel    : $detalhes.combustivel
            cambio         : $detalhes.cambio
            quilometragem  : $detalhes.quilometragem
            numero_portas  : $detalhes.numero_portas
            numero_lugares : $detalhes.numero_lugares
            opcionais      : ($detalhes.opcionais ?? [])
            created_at     : $detalhes.created_at
          }
        }
      }
    }
  }

  response = {
    veiculo : ```
      {
        id              : $veiculo.id
        Marca           : $veiculo.Marca
        Modelo          : $veiculo.Modelo
        Cor             : $veiculo.Cor
        Ano             : $veiculo.Ano
        Placa           : $veiculo.Placa
        Chassi          : $veiculo.Chassi
        Quilometragem   : $veiculo.Quilometragem
        Preco           : $veiculo.Preco
        status_id       : $veiculo.status_id
        status_descricao: ($status.Descricao ?? "")
        created_at      : $veiculo.created_at
        imagem_url      : $veiculo.imagem_url
      }
      ```
    detalhes: $detalhes_envelope
  }

  guid = "c2cdn4hOtT2I4yvVfGEQ84oVa_I"
}