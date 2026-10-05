// Detalhes de um veiculo especifico
// Retorna os detalhes de um veiculo e a descricao do seu status
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
  }

  response = {
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
  }

  guid = "c2cdn4hOtT2I4yvVfGEQ84oVa_I"
}