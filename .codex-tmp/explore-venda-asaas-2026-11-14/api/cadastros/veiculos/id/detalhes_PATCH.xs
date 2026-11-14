// Atualizacao parcial de detalhes do veiculo
// Atualiza somente os campos informados de veiculo_detalhe com validacao de perfil
// Identificador do veiculo e campos a serem atualizados
query "veiculos/{id}/detalhes" verb=PATCH {
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
      error = "Apenas Gerente ou Administrador podem atualizar detalhes do veiculo"
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
  
    // Buscar detalhes existentes do veiculo (404 se nao existirem)
    db.query veiculo_detalhe {
      where = $db.veiculo_detalhe.veiculo_id == $input.id
      return = {type: "single"}
    } as $detalhes
  
    precondition ($detalhes != null) {
      error_type = "notfound"
      error = "Detalhes do veiculo nao encontrados"
    }
  
    // Inicializar mapa de atualizacoes
    var $updates {
      value = {}
    }
  
    // Validar e registrar atualizacoes parciais
    conditional {
      if ($input.uf_registro != null && ($input.uf_registro|strlen) > 0) {
        var.update $updates {
          value = $updates
            |set:"uf_registro":($input.uf_registro|trim|to_upper)
        }
      }
    }
  
    conditional {
      if ($input.cidade_registro != null && ($input.cidade_registro|strlen) > 0) {
        var.update $updates {
          value = $updates
            |set:"cidade_registro":($input.cidade_registro|trim)
        }
      }
    }
  
    conditional {
      if ($input.ano_fabricacao != null) {
        precondition ($input.ano_fabricacao >= 1900 && $input.ano_fabricacao <= 2100) {
          error_type = "badrequest"
          error = "Ano de fabricacao deve estar entre 1900 e 2100"
        }
      
        var.update $updates {
          value = $updates
            |set:"ano_fabricacao":$input.ano_fabricacao
        }
      }
    }
  
    conditional {
      if ($input.motorizacao != null && ($input.motorizacao|strlen) > 0) {
        var.update $updates {
          value = $updates
            |set:"motorizacao":($input.motorizacao|trim)
        }
      }
    }
  
    conditional {
      if ($input.combustivel != null && ($input.combustivel|strlen) > 0) {
        precondition ($input.combustivel == "Flex" || $input.combustivel == "Gasolina" || $input.combustivel == "Diesel" || $input.combustivel == "Elétrico" || $input.combustivel == "Híbrido") {
          error_type = "badrequest"
          error = "Combustivel invalido. Valores aceitos: Flex, Gasolina, Diesel, Elétrico, Híbrido"
        }
      
        var.update $updates {
          value = $updates
            |set:"combustivel":($input.combustivel|trim)
        }
      }
    }
  
    conditional {
      if ($input.cambio != null && ($input.cambio|strlen) > 0) {
        precondition ($input.cambio == "Automático" || $input.cambio == "Manual" || $input.cambio == "CVT") {
          error_type = "badrequest"
          error = "Cambio invalido. Valores aceitos: Automático, Manual, CVT"
        }
      
        var.update $updates {
          value = $updates
            |set:"cambio":($input.cambio|trim)
        }
      }
    }
  
    conditional {
      if ($input.quilometragem != null) {
        precondition ($input.quilometragem >= 0) {
          error_type = "badrequest"
          error = "Quilometragem deve ser maior ou igual a 0"
        }
      
        var.update $updates {
          value = $updates
            |set:"quilometragem":$input.quilometragem
        }
      }
    }
  
    conditional {
      if ($input.numero_portas != null) {
        precondition ($input.numero_portas >= 1 && $input.numero_portas <= 20) {
          error_type = "badrequest"
          error = "Numero de portas deve estar entre 1 e 20"
        }
      
        var.update $updates {
          value = $updates
            |set:"numero_portas":$input.numero_portas
        }
      }
    }
  
    conditional {
      if ($input.numero_lugares != null) {
        precondition ($input.numero_lugares >= 1 && $input.numero_lugares <= 100) {
          error_type = "badrequest"
          error = "Numero de lugares deve estar entre 1 e 100"
        }
      
        var.update $updates {
          value = $updates
            |set:"numero_lugares":$input.numero_lugares
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
      
        var.update $updates {
          value = $updates|set:"opcionais":$input.opcionais
        }
      }
    }
  
    // Gravar alteracoes com operacao atomica
    var $detalhes_atualizado {
      value = $detalhes
    }
  
    conditional {
      if (($updates|is_empty) == false) {
        db.transaction {
          stack {
            db.patch veiculo_detalhe {
              field_name = "id"
              field_value = $detalhes.id
              data = $updates
            } as $detalhe_gravado
          
            var.update $detalhes_atualizado {
              value = $detalhe_gravado
            }
          }
        }
      }
    }
  }

  response = {
    id             : $detalhes_atualizado.id
    veiculo_id     : $detalhes_atualizado.veiculo_id
    uf_registro    : $detalhes_atualizado.uf_registro
    cidade_registro: $detalhes_atualizado.cidade_registro
    ano_fabricacao : $detalhes_atualizado.ano_fabricacao
    motorizacao    : $detalhes_atualizado.motorizacao
    combustivel    : $detalhes_atualizado.combustivel
    cambio         : $detalhes_atualizado.cambio
    quilometragem  : $detalhes_atualizado.quilometragem
    numero_portas  : $detalhes_atualizado.numero_portas
    numero_lugares : $detalhes_atualizado.numero_lugares
    opcionais      : ($detalhes_atualizado.opcionais ?? [])
    created_at     : $detalhes_atualizado.created_at
  }

  guid = "SbzsB31TG8V0Myx4wG2WrvtZbNU"
}