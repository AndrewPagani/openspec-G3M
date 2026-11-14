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
  
    int forma_pagamento_id {
      table = "forma_pagamento"
    }
  
    int numero_parcelas filters=min:"1,max":24
    decimal Desconto? filters=min:0
    object[] itens {
      schema {
        int? veiculo_id
        int? peca_id
        int qtd filters=min:1
      }
    }
  }

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
  
    // 2. Validar forma de pagamento
    db.get forma_pagamento {
      field_name = "id"
      field_value = $input.forma_pagamento_id
    } as $forma_pagamento
  
    precondition ($forma_pagamento != null) {
      error_type = "badrequest"
      error = "Forma de pagamento informada e invalida"
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
      value = $input.Desconto ?? 0
    }
  
    conditional {
      if ($perfil_vendedor.Cargo == "Vendedor" && $desconto > 0) {
        precondition (false) {
          error_type = "accessdenied"
          error = "Vendedor nao possui permissao para conceder desconto"
        }
      }
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
  
    var $centavos_por_parcela {
      value = ($valor_total_centavos / $input.numero_parcelas)|floor
    }
  
    precondition ($valor_total_centavos >= $input.numero_parcelas) {
      error_type = "badrequest"
      error = "O valor da venda em centavos deve ser igual ou superior a quantidade de parcelas"
    }
  
    var $parcelas_criadas {
      value = []
    }
  
    // 8. Executar transacao atomica de gravacao da venda e reservas
    db.transaction {
      stack {
        db.add venda {
          data = {
            cliente_id        : $input.cliente_id
            vendedor_id       : $auth.id
            forma_pagamento_id: $input.forma_pagamento_id
            status_id         : $status_venda_reservado.id
            Valor_bruto       : $valor_bruto
            Desconto          : $desconto
            Valor_final       : $valor_final
            data_venda        : now
          }
        } as $nova_venda
      
        foreach ($itens_processados) {
          each as $proc_item {
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
                  value = $proc_item.qtd_anterior - $proc_item.qtd
                }
              
                db.patch peca {
                  field_name = "id"
                  field_value = $proc_item.peca_id
                  data = {qtd_disp: $nova_qtd}
                } as $peca_atualizada
              }
            }
          
            // Criar cronograma local; a última parcela absorve eventual resto de centavos
            var $numeros_parcela {
              value = [
                1
                2
                3
                4
                5
                6
                7
                8
                9
                10
                11
                12
                13
                14
                15
                16
                17
                18
                19
                20
                21
                22
                23
                24
              ]
            }
          
            foreach ($numeros_parcela|filter:$$ <= $input.numero_parcelas) {
              each as $numero_parcela {
                var $valor_parcela_centavos {
                  value = $centavos_por_parcela
                }
              
                conditional {
                  if ($numero_parcela == $input.numero_parcelas) {
                    var.update $valor_parcela_centavos {
                      value = $valor_total_centavos - ($centavos_por_parcela * ($input.numero_parcelas - 1))
                    }
                  }
                }
              
                // Calcular data de vencimento da parcela preservando o dia original e limitando ao ultimo dia do mes
                var $ano_base {
                  value = ($nova_venda.data_venda|format_timestamp:"Y":"America/Sao_Paulo")|to_int
                }
              
                var $mes_base_num {
                  value = ($nova_venda.data_venda|format_timestamp:"n":"America/Sao_Paulo")|to_int
                }
              
                var $dia_base_num {
                  value = ($nova_venda.data_venda|format_timestamp:"j":"America/Sao_Paulo")|to_int
                }
              
                var $mes_offset {
                  value = $numero_parcela - 1
                }
              
                var $total_meses {
                  value = ($ano_base * 12) + ($mes_base_num - 1) + $mes_offset
                }
              
                var $ano_alvo {
                  value = ($total_meses / 12)|floor
                }
              
                var $mes_alvo {
                  value = ($total_meses % 12) + 1
                }
              
                var $max_dias {
                  value = 31
                }
              
                conditional {
                  if ($mes_alvo == 4 || $mes_alvo == 6 || $mes_alvo == 9 || $mes_alvo == 11) {
                    var.update $max_dias {
                      value = 30
                    }
                  }
                
                  elseif ($mes_alvo == 2) {
                    conditional {
                      if (($ano_alvo % 4 == 0 && $ano_alvo % 100 != 0) || ($ano_alvo % 400 == 0)) {
                        var.update $max_dias {
                          value = 29
                        }
                      }
                    
                      else {
                        var.update $max_dias {
                          value = 28
                        }
                      }
                    }
                  }
                }
              
                var $dia_final {
                  value = $dia_base_num
                }
              
                conditional {
                  if ($dia_final > $max_dias) {
                    var.update $dia_final {
                      value = $max_dias
                    }
                  }
                }
              
                var $mes_str {
                  value = ($mes_alvo < 10) ? ("0" ~ ($mes_alvo|to_text)) : ($mes_alvo|to_text)
                }
              
                var $dia_str {
                  value = ($dia_final < 10) ? ("0" ~ ($dia_final|to_text)) : ($dia_final|to_text)
                }
              
                var $iso_vencimento {
                  value = ($ano_alvo|to_text) ~ "-" ~ $mes_str ~ "-" ~ $dia_str ~ "T12:00:00Z"
                }
              
                var $data_vencimento {
                  value = $iso_vencimento|to_timestamp
                }
              
                db.add venda_parcela {
                  data = {
                    venda_id      : $nova_venda.id
                    numero_parcela: $numero_parcela
                    total_parcelas: $input.numero_parcelas
                    valor         : $valor_parcela_centavos / 100
                    vencimento    : $data_vencimento
                    status        : "PENDENTE"
                  }
                } as $parcela_criada
              
                var.update $parcelas_criadas {
                  value = $parcelas_criadas
                    |push:```
                      {
                        id: $parcela_criada.id,
                        numero_parcela: $parcela_criada.numero_parcela,
                        total_parcelas: $parcela_criada.total_parcelas,
                        valor: $parcela_criada.valor,
                        vencimento: $parcela_criada.vencimento,
                        status: $parcela_criada.status,
                        forma_recebida: null,
                        recebido_em: null,
                        recebido_por: null
                      }
                      ```
                }
              }
            }
          }
        }
      }
    }
  }

  response = {
    id                : $nova_venda.id
    cliente_id        : $nova_venda.cliente_id
    vendedor_id       : $nova_venda.vendedor_id
    forma_pagamento_id: $nova_venda.forma_pagamento_id
    status_id         : $nova_venda.status_id
    status_descricao  : $status_venda_reservado.Descricao_venda
    Valor_bruto       : $nova_venda.Valor_bruto
    Desconto          : $nova_venda.Desconto
    Valor_final       : $nova_venda.Valor_final
    data_venda        : $nova_venda.data_venda
    numero_parcelas   : $input.numero_parcelas
    parcelas          : $parcelas_criadas
    itens             : $itens_processados
  }

  test "rejeita venda sem itens" {
    input = {
      cliente_id        : 1
      forma_pagamento_id: 1
      numero_parcelas   : 1
      Desconto          : 0
      itens             : []
    }
  
    expect.to_throw {
      exception = ""
    }
  }

  guid = "JsmBWI3-tQftZNHc7FitstctKYs"
}