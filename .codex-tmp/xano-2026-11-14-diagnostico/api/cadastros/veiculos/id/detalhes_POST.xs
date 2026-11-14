// Cadastro de detalhes do veiculo
// Cadastra as informacoes complementares do veiculo em relacao 1:1
// Identificador do veiculo e detalhes tecnicos
query "veiculos/{id}/detalhes" verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "veiculo"
    }
  
    text uf_registro? filters=trim|upper
    text cidade_registro? filters=trim
    int ano_fabricacao? filters=min:1900|max:2100
    text motorizacao? filters=trim
    text combustivel? filters=trim
    text cambio? filters=trim
    decimal quilometragem? filters=min:0
    int numero_portas? filters=min:1|max:20
    int numero_lugares? filters=min:1|max:100
    json opcionais?
  }

  stack {
    // Validar permissao de perfil do usuario autenticado (Gerente ou Administrador)
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
      error = "Apenas Gerente ou Administrador podem cadastrar detalhes do veiculo"
    }
  
    // Validar se o veiculo existe
    db.get veiculo {
      field_name = "id"
      field_value = $input.id
    } as $veiculo
  
    precondition ($veiculo != null) {
      error_type = "notfound"
      error = "Veiculo nao encontrado"
    }
  
    // Impedir segundo registro para o mesmo veiculo_id (retornar 409 Conflict)
    db.query veiculo_detalhe {
      where = $db.veiculo_detalhe.veiculo_id == $input.id
      return = {type: "single"}
    } as $detalhe_existente
  
    conditional {
      if ($detalhe_existente != null) {
        throw {
          name = "Conflict"
          value = "Veiculo ja possui detalhes cadastrados"
          status = 409
        }
      }
    }
  
    // Validar limites e valores
    conditional {
      if ($input.ano_fabricacao != null) {
        precondition ($input.ano_fabricacao >= 1900 && $input.ano_fabricacao <= 2100) {
          error_type = "badrequest"
          error = "Ano de fabricacao deve estar entre 1900 e 2100"
        }
      }
    }
  
    conditional {
      if ($input.quilometragem != null) {
        precondition ($input.quilometragem >= 0) {
          error_type = "badrequest"
          error = "Quilometragem deve ser maior ou igual a 0"
        }
      }
    }
  
    conditional {
      if ($input.numero_portas != null) {
        precondition ($input.numero_portas >= 1 && $input.numero_portas <= 20) {
          error_type = "badrequest"
          error = "Numero de portas deve estar entre 1 e 20"
        }
      }
    }
  
    conditional {
      if ($input.numero_lugares != null) {
        precondition ($input.numero_lugares >= 1 && $input.numero_lugares <= 100) {
          error_type = "badrequest"
          error = "Numero de lugares deve estar entre 1 e 100"
        }
      }
    }
  
    conditional {
      if ($input.combustivel != null && ($input.combustivel|strlen) > 0) {
        precondition ($input.combustivel == "Flex" || $input.combustivel == "Gasolina" || $input.combustivel == "Diesel" || $input.combustivel == "Elétrico" || $input.combustivel == "Híbrido") {
          error_type = "badrequest"
          error = "Combustivel invalido. Valores aceitos: Flex, Gasolina, Diesel, Elétrico, Híbrido"
        }
      }
    }
  
    conditional {
      if ($input.cambio != null && ($input.cambio|strlen) > 0) {
        precondition ($input.cambio == "Automático" || $input.cambio == "Manual" || $input.cambio == "CVT") {
          error_type = "badrequest"
          error = "Cambio invalido. Valores aceitos: Automático, Manual, CVT"
        }
      }
    }
  
    conditional {
      if ($input.opcionais != null) {
        precondition ($input.opcionais|is_array) {
          error_type = "badrequest"
          error = "O campo opcionais deve ser uma lista"
        }
      
        foreach ($input.opcionais) {
          each as $item {
            precondition ($item|is_text) {
              error_type = "badrequest"
              error = "Todos os itens de opcionais devem ser textos"
            }
          }
        }
      }
    }
  
    // Inserir registro com operacao atomica
    var $novo_detalhe {
      value = null
    }
  
    db.transaction {
      stack {
        db.add veiculo_detalhe {
          data = {
            veiculo_id     : $input.id
            uf_registro    : (($input.uf_registro != null) ? ($input.uf_registro|trim|to_upper) : null)
            cidade_registro: (($input.cidade_registro != null) ? ($input.cidade_registro|trim) : null)
            ano_fabricacao : $input.ano_fabricacao
            motorizacao    : (($input.motorizacao != null) ? ($input.motorizacao|trim) : null)
            combustivel    : (($input.combustivel != null) ? ($input.combustivel|trim) : null)
            cambio         : (($input.cambio != null) ? ($input.cambio|trim) : null)
            quilometragem  : $input.quilometragem
            numero_portas  : $input.numero_portas
            numero_lugares : $input.numero_lugares
            opcionais      : ($input.opcionais ?? [])
            created_at     : now
          }
        } as $detalhe_criado
      
        var.update $novo_detalhe {
          value = $detalhe_criado
        }
      }
    }
  }

  response = {
    id             : $novo_detalhe.id
    veiculo_id     : $novo_detalhe.veiculo_id
    uf_registro    : $novo_detalhe.uf_registro
    cidade_registro: $novo_detalhe.cidade_registro
    ano_fabricacao : $novo_detalhe.ano_fabricacao
    motorizacao    : $novo_detalhe.motorizacao
    combustivel    : $novo_detalhe.combustivel
    cambio         : $novo_detalhe.cambio
    quilometragem  : $novo_detalhe.quilometragem
    numero_portas  : $novo_detalhe.numero_portas
    numero_lugares : $novo_detalhe.numero_lugares
    opcionais      : ($novo_detalhe.opcionais ?? [])
    created_at     : $novo_detalhe.created_at
  }

  guid = "7pdzawC47DcpPHeE8hgtx_mvK3I"
}