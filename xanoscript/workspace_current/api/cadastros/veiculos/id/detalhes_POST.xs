// Cria os detalhes complementares de um veículo
query "veiculos/{id}/detalhes" verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    int id { table = "veiculo" }
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
    db.get veiculo {
      field_name = "id"
      field_value = $input.id
    } as $veiculo

    precondition ($veiculo != null) {
      error_type = "notfound"
      error = "Veiculo nao encontrado"
    }

    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $usuario
    db.get perfil {
      field_name = "id"
      field_value = $usuario.perfil_id
    } as $perfil
    precondition ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador") {
      error_type = "accessdenied"
      error = "Somente gerente ou administrador pode alterar detalhes do veiculo"
    }

    db.query veiculo_detalhe {
      where = $db.veiculo_detalhe.veiculo_id == $input.id
      return = {type: "single"}
    } as $existente
    precondition ($existente == null) {
      error_type = "badrequest"
      error = "Detalhes deste veiculo ja existem"
    }

    precondition ($input.combustivel == null || $input.combustivel == "Flex" || $input.combustivel == "Gasolina" || $input.combustivel == "Diesel" || $input.combustivel == "Elétrico" || $input.combustivel == "Híbrido") {
      error_type = "inputerror"
      error = "Tipo de combustivel invalido"
    }
    precondition ($input.cambio == null || $input.cambio == "Automático" || $input.cambio == "Manual" || $input.cambio == "CVT") {
      error_type = "inputerror"
      error = "Tipo de cambio invalido"
    }
    precondition ($input.opcionais == null || ($input.opcionais|count) >= 0) {
      error_type = "inputerror"
      error = "Opcionais devem ser uma lista"
    }

    db.add veiculo_detalhe {
      data = {
        veiculo_id       : $input.id
        uf_registro      : $input.uf_registro
        cidade_registro: $input.cidade_registro
        ano_fabricacao : $input.ano_fabricacao
        motorizacao    : $input.motorizacao
        combustivel    : $input.combustivel
        cambio          : $input.cambio
        quilometragem  : $input.quilometragem
        numero_portas  : $input.numero_portas
        numero_lugares : $input.numero_lugares
        opcionais      : $input.opcionais
        created_at     : now
      }
    } as $detalhes
  }

  response = $detalhes
  guid = "7pdzawC47DcpPHeE8hgtx_mvK3I"
}
