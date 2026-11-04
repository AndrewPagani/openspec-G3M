// Atualiza parcialmente os detalhes complementares de um veículo
query "veiculos/{id}/detalhes" verb=PATCH {
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
    } as $detalhes
    precondition ($detalhes != null) {
      error_type = "notfound"
      error = "Detalhes do veiculo nao encontrados"
    }
    precondition ($input.combustivel == null || $input.combustivel == "Flex" || $input.combustivel == "Gasolina" || $input.combustivel == "Diesel" || $input.combustivel == "Elétrico" || $input.combustivel == "Híbrido") {
      error_type = "inputerror"
      error = "Tipo de combustivel invalido"
    }
    precondition ($input.cambio == null || $input.cambio == "Automático" || $input.cambio == "Manual" || $input.cambio == "CVT") {
      error_type = "inputerror"
      error = "Tipo de cambio invalido"
    }

    var $updates { value = {} }
    conditional { if ($input.uf_registro != null) { var.update $updates { value = $updates|set:"uf_registro":$input.uf_registro } } }
    conditional { if ($input.cidade_registro != null) { var.update $updates { value = $updates|set:"cidade_registro":$input.cidade_registro } } }
    conditional { if ($input.ano_fabricacao != null) { var.update $updates { value = $updates|set:"ano_fabricacao":$input.ano_fabricacao } } }
    conditional { if ($input.motorizacao != null) { var.update $updates { value = $updates|set:"motorizacao":$input.motorizacao } } }
    conditional { if ($input.combustivel != null) { var.update $updates { value = $updates|set:"combustivel":$input.combustivel } } }
    conditional { if ($input.cambio != null) { var.update $updates { value = $updates|set:"cambio":$input.cambio } } }
    conditional { if ($input.quilometragem != null) { var.update $updates { value = $updates|set:"quilometragem":$input.quilometragem } } }
    conditional { if ($input.numero_portas != null) { var.update $updates { value = $updates|set:"numero_portas":$input.numero_portas } } }
    conditional { if ($input.numero_lugares != null) { var.update $updates { value = $updates|set:"numero_lugares":$input.numero_lugares } } }
    conditional { if ($input.opcionais != null) { var.update $updates { value = $updates|set:"opcionais":$input.opcionais } } }
    db.patch veiculo_detalhe {
      field_name = "id"
      field_value = $detalhes.id
      data = $updates
    } as $atualizado
  }

  response = $atualizado
  guid = "SbzsB31TG8V0Myx4wG2WrvtZbNU"
}
