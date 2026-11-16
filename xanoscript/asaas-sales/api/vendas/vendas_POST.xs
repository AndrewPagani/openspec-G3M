// Criacao de venda com reserva atomica de veiculos e pecas
// Cria uma nova venda calculando precos por catalogo, validando descontos por perfil e reservando itens no banco de forma atomica contra concorrencia
// Parametros de entrada da venda
query vendas verb=POST {
  api_group = "vendas"
  auth = "user"

  input {
    int cliente_id {
      table = "cliente"
    }

    object[] itens {
      schema {
        int? veiculo_id?
        int? peca_id?
        int qtd filters=min:1
      }
    }
  }

  stack {
    db.transaction {
      stack {

    // 1. Validar cliente e dados obrigatorios de contato
    db.get cliente {

    field_name = "id"

    field_value = $input.cliente_id
    } as $cliente

    precondition ($cliente != null) {

    error_type = "notfound"

    error = "Cliente nao encontrado"
    }

    precondition (($cliente.CPF != null && ($cliente.CPF|strlen) > 0) && ($cliente.Email != null && ($cliente.Email|strlen) > 0) && ($cliente.Telefone != null && ($cliente.Telefone|strlen) > 0)) {

    error_type = "badrequest"

    error = "Cliente deve possuir CPF, Email e Telefone cadastrados para realizar venda"
    }

    // 3. Validar perfil do usuario para aplicacao de desconto
    db.get user {

    field_name = "id"

    field_value = $auth.id
    } as $usuario_vendedor

    db.get perfil {

    field_name = "id"

    field_value = $usuario_vendedor.perfil_id
    } as $perfil_vendedor

    var $desconto {
      value = 0
    }

    conditional {
      if ($perfil_vendedor.Cargo == "Vendedor" && $desconto > 0) {
        precondition (false) {

    error_type = "accessdenied"

    error = "Vendedor nao possui permissao para conceder desconto"
        }
      }
    }


    precondition ($perfil_vendedor.Cargo == "Vendedor" || $perfil_vendedor.Cargo == "Gerente" || $perfil_vendedor.Cargo == "Administrador") {

    error_type = "accessdenied"
    error = "Perfil sem permissao para criar venda"
    }
    // 4. Validar presenca de itens
    precondition (($input.itens|count) > 0) {

    error_type = "badrequest"

    error = "A venda deve conter ao menos um item"
    }

    // 5. Buscar status de venda Reservado e status de veiculo Reservado e Disponivel
    db.query status_venda {

    where = $db.status_venda.Descricao_venda == "Reservado"

    return = {type: "single"}
    } as $status_venda_reservado

    precondition ($status_venda_reservado != null) {

    error = "Status de venda Reservado nao encontrado"
    }

    db.query status_veiculo {

    where = $db.status_veiculo.Descricao == "Disponível" || $db.status_veiculo.Descricao == "Disponivel"

    return = {type: "single"}
    } as $status_veiculo_disp

    db.query status_veiculo {

    where = $db.status_veiculo.Descricao == "Reservado"

    return = {type: "single"}
    } as $status_veiculo_res

    precondition ($status_veiculo_disp != null && $status_veiculo_res != null) {

    error = "Status de veiculo Disponivel/Reservado nao encontrados"
    }

    // 6. Validar itens, verificar estoque/disponibilidade e congelar precos
    var $itens_processados {
      value = []
    }

    var $veiculos_vistos {
      value = []
    }

    var $pecas_vistas {
      value = []
    }

    var $valor_bruto {
      value = 0
    }

    foreach ($input.itens) {
      each as $item {
        var $tem_veiculo {
          value = ($item.veiculo_id != null && $item.veiculo_id > 0)
        }

        var $tem_peca {
          value = ($item.peca_id != null && $item.peca_id > 0)
        }

        precondition (($tem_veiculo && $tem_peca == false) || ($tem_veiculo == false && $tem_peca)) {

    error_type = "badrequest"

    error = "Cada item deve conter exclusivamente veiculo_id ou peca_id"
        }

        conditional {
          if ($tem_veiculo) {
            precondition ($item.qtd == 1) {

    error_type = "badrequest"

    error = "Quantidade para veiculo deve ser exatamente 1"
            }

            precondition (($veiculos_vistos|some:$$ == $item.veiculo_id) == false) {

    error_type = "badrequest"

    error = "O mesmo veiculo nao pode ser adicionado mais de uma vez"
            }

            var.update $veiculos_vistos {
              value = $veiculos_vistos|push:$item.veiculo_id
            }

            db.get veiculo {

    field_name = "id"

    field_value = $item.veiculo_id
            } as $veiculo_db

            precondition ($veiculo_db != null) {

    error_type = "notfound"

    error = "Veiculo nao encontrado"
            }

            precondition ($veiculo_db.status_id == $status_veiculo_disp.id) {

    error_type = "badrequest"

    error = "409 Conflito: Veiculo selecionado nao esta disponivel para reserva"
            }

            var $subtotal_item {
              value = $veiculo_db.Preco * 1
            }

            var.update $valor_bruto {
              value = $valor_bruto + $subtotal_item
            }

            var.update $itens_processados {
              value = $itens_processados
                |push:```
                  {
                    veiculo_id: $item.veiculo_id,
                    peca_id: null,
                    qtd: 1,
                    preco_unit: $veiculo_db.Preco,
                    subtotal: $subtotal_item
                  }
                  ```
            }
          }

          else {
            precondition ($item.qtd >= 1) {

    error_type = "badrequest"

    error = "Quantidade de pecas deve ser no minimo 1"
            }

            precondition (($pecas_vistas|some:$$ == $item.peca_id) == false) {

    error_type = "badrequest"

    error = "Peca duplicada no pedido. Consolide a quantidade em um unico item"
            }

            var.update $pecas_vistas {
              value = $pecas_vistas|push:$item.peca_id
            }

            db.get peca {

    field_name = "id"

    field_value = $item.peca_id
            } as $peca_db

            precondition ($peca_db != null) {

    error_type = "notfound"

    error = "Peca nao encontrada"
            }

            precondition (($peca_db.qtd_disp ?? 0) >= $item.qtd) {

    error_type = "badrequest"

    error = "409 Conflito: Estoque insuficiente para a peca selecionada"
            }

            var $subtotal_item_peca {
              value = $peca_db.PCvalor * $item.qtd
            }

            var.update $valor_bruto {
              value = $valor_bruto + $subtotal_item_peca
            }

            var.update $itens_processados {
              value = $itens_processados
                |push:```
                  {
                    veiculo_id: null,
                    peca_id: $item.peca_id,
                    qtd: $item.qtd,
                    preco_unit: $peca_db.PCvalor,
                    subtotal: $subtotal_item_peca,
                    qtd_anterior: ($peca_db.qtd_disp ?? 0)
                  }
                  ```
            }
          }
        }
      }
    }

    // 7. Validar valor final e desconto
    precondition ($desconto <= $valor_bruto) {

    error_type = "badrequest"

    error = "Desconto nao pode ser superior ao valor bruto da venda"
    }

    var $valor_final {
      value = $valor_bruto - $desconto
    }

    var $valor_total_centavos {
      value = ($valor_final * 100)|round:0
    }

    precondition ($valor_final == ($valor_total_centavos / 100)) {

    error_type = "badrequest"

    error = "O valor final da venda deve ter no maximo duas casas decimais"
    }


        precondition ($valor_final > 0) {
    error_type = "badrequest"
    error = "Valor da venda deve ser positivo" }
        db.add venda {

    data = {
            cliente_id        : $input.cliente_id
            vendedor_id       : $auth.id
            forma_pagamento_id: null
            payment_flow      : "ASAAS"
            status_id         : $status_venda_reservado.id
            Valor_bruto       : $valor_bruto
            Desconto          : $desconto
            Valor_final       : $valor_final
            data_venda        : now
          }
        } as $nova_venda

        foreach ($itens_processados) {
          each as $proc_item {

            conditional {
              if ($proc_item.veiculo_id != null) {
                db.query veiculo {
    where = $db.veiculo.id == $proc_item.veiculo_id
    lock = true
    return = {type: "single"} } as $current_vehicle
                precondition ($current_vehicle.status_id == $status_veiculo_disp.id && $current_vehicle.Preco == $proc_item.preco_unit) {

    error_type = "badrequest"
    error = "Veiculo alterado ou reservado por outra venda; atualize a selecao"
                }
              }
              else {
                db.query peca {
    where = $db.peca.id == $proc_item.peca_id
    lock = true
    return = {type: "single"} } as $current_part
                precondition ($current_part != null && $current_part.qtd_disp >= $proc_item.qtd && $current_part.PCvalor == $proc_item.preco_unit) {

    error_type = "badrequest"
    error = "Estoque ou preco alterado; atualize a selecao"
                }
              }
            }
            db.add venda_item {

    data = {
                venda_id  : $nova_venda.id
                veiculo_id: $proc_item.veiculo_id
                peca_id   : $proc_item.peca_id
                qtd       : $proc_item.qtd
                preco_unit: $proc_item.preco_unit
              }
            } as $venda_item_salvo

            conditional {
              if ($proc_item.veiculo_id != null) {
                db.patch veiculo {

    field_name = "id"

    field_value = $proc_item.veiculo_id

    data = {status_id: $status_veiculo_res.id}
                } as $veiculo_atualizado
              }

              else {
                var $nova_qtd {
                  value = $current_part.qtd_disp - $proc_item.qtd
                }

                db.patch peca {

    field_name = "id"

    field_value = $proc_item.peca_id

    data = {qtd_disp: $nova_qtd}
                } as $peca_atualizada
              }
            }

          }
        }

      }
    }
  }

  response = {id: $nova_venda.id, cliente_id: $nova_venda.cliente_id, vendedor_id: $nova_venda.vendedor_id,
              status_id: $nova_venda.status_id, status_descricao: $status_venda_reservado.Descricao_venda,
              Valor_bruto: $valor_bruto, Desconto: 0, Valor_final: $valor_final,
              data_venda: $nova_venda.data_venda, payment_flow: "ASAAS", itens: $itens_processados}

  guid = "JsmBWI3-tQftZNHc7FitstctKYs"
}
