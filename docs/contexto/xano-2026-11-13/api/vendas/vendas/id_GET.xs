// Detalhes completos da venda com itens, parcelas locais e histórico legado
// Identificador da venda
query "vendas/{id}" verb=GET {
  api_group = "vendas"
  auth = "user"

  input {
    int id {
      table = "venda"
    }
  }

  stack {
    // Buscar venda no banco
    db.get venda {
      field_name = "id"
      field_value = $input.id
    } as $venda
  
    precondition ($venda != null) {
      error_type = "notfound"
      error = "Venda nao encontrada"
    }
  
    // Validar permissao de acesso (Vendedor so acessa suas proprias vendas)
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    conditional {
      if ($perfil.Cargo == "Vendedor") {
        precondition ($venda.vendedor_id == $auth.id) {
          error_type = "notfound"
          error = "Venda nao encontrada"
        }
      }
    }
  
    // Buscar dados do cliente
    db.get cliente {
      field_name = "id"
      field_value = $venda.cliente_id
    } as $cliente
  
    // Buscar dados do vendedor
    db.get user {
      field_name = "id"
      field_value = $venda.vendedor_id
    } as $vendedor
  
    // Buscar forma de pagamento
    db.get forma_pagamento {
      field_name = "id"
      field_value = $venda.forma_pagamento_id
    } as $forma_pagamento
  
    // Buscar status da venda
    db.get status_venda {
      field_name = "id"
      field_value = $venda.status_id
    } as $status_venda
  
    // Buscar itens da venda
    db.query venda_item {
      where = $db.venda_item.venda_id == $input.id
      return = {type: "list"}
    } as $itens_brutos
  
    // Buscar veiculos e pecas para enriquecer itens
    db.query veiculo {
      return = {type: "list"}
    } as $todos_veiculos
  
    db.query peca {
      return = {type: "list"}
    } as $todas_pecas
  
    var $itens_detalhados {
      value = ```
        $itens_brutos|map:{
                id: $$.id,
                veiculo_id: $$.veiculo_id,
                veiculo_marca: (($todos_veiculos|find:$item.id == $$.veiculo_id).Marca ?? null),
                veiculo_modelo: (($todos_veiculos|find:$item.id == $$.veiculo_id).Modelo ?? null),
                veiculo_placa: (($todos_veiculos|find:$item.id == $$.veiculo_id).Placa ?? null),
                peca_id: $$.peca_id,
                peca_nome: (($todas_pecas|find:$item.id == $$.peca_id).PCNome ?? null),
                qtd: $$.qtd,
                preco_unit: $$.preco_unit,
                subtotal: ($$.preco_unit * $$.qtd)
              }
        ```
    }
  
    // O histórico antigo permanece apenas para leitura e não participa dos totais locais
    db.query pagamento {
      where = $db.pagamento.venda_id == $input.id
      sort = {numero_parcela: "asc"}
      return = {type: "list"}
    } as $pagamentos_legados_db
  
    db.query venda_parcela {
      where = $db.venda_parcela.venda_id == $input.id
      sort = {numero_parcela: "asc"}
      return = {type: "list"}
    } as $parcelas_db
  
    db.query forma_pagamento {
      return = {type: "list"}
    } as $formas_pagamento
  
    var $pagamentos_sanitizados {
      value = ```
        $pagamentos_legados_db|map:{
                valor: $$.valor,
                numero_parcela: $$.numero_parcela,
                total_parcelas: $$.total_parcelas,
                vencimento: $$.vencimento,
                recebido_em: $$.recebido_em
              }
        ```
    }
  
    var $parcelas_sanitizadas {
      value = []
    }
  
    foreach ($parcelas_db) {
      each as $p_item {
        var $venc_val {
          value = $p_item.vencimento
        }
      
        conditional {
          if ($venc_val == null || (($venc_val|to_int) <= 0)) {
            var $p_ano {
              value = ($venda.data_venda|format_timestamp:"Y":"America/Sao_Paulo")|to_int
            }
          
            var $p_mes {
              value = ($venda.data_venda|format_timestamp:"n":"America/Sao_Paulo")|to_int
            }
          
            var $p_dia {
              value = ($venda.data_venda|format_timestamp:"j":"America/Sao_Paulo")|to_int
            }
          
            var $p_total_meses {
              value = ($p_ano * 12) + ($p_mes - 1) + ($p_item.numero_parcela - 1)
            }
          
            var $p_ano_alvo {
              value = ($p_total_meses / 12)|floor
            }
          
            var $p_mes_alvo {
              value = ($p_total_meses % 12) + 1
            }
          
            var $p_max_dias {
              value = 31
            }
          
            conditional {
              if ($p_mes_alvo == 4 || $p_mes_alvo == 6 || $p_mes_alvo == 9 || $p_mes_alvo == 11) {
                var.update $p_max_dias {
                  value = 30
                }
              }
            
              elseif ($p_mes_alvo == 2) {
                conditional {
                  if (($p_ano_alvo % 4 == 0 && $p_ano_alvo % 100 != 0) || ($p_ano_alvo % 400 == 0)) {
                    var.update $p_max_dias {
                      value = 29
                    }
                  }
                
                  else {
                    var.update $p_max_dias {
                      value = 28
                    }
                  }
                }
              }
            }
          
            var $p_dia_final {
              value = ($p_dia > $p_max_dias) ? $p_max_dias : $p_dia
            }
          
            var $p_mes_str {
              value = ($p_mes_alvo < 10) ? ("0" ~ ($p_mes_alvo|to_text)) : ($p_mes_alvo|to_text)
            }
          
            var $p_dia_str {
              value = ($p_dia_final < 10) ? ("0" ~ ($p_dia_final|to_text)) : ($p_dia_final|to_text)
            }
          
            var.update $venc_val {
              value = (($p_ano_alvo|to_text) ~ "-" ~ $p_mes_str ~ "-" ~ $p_dia_str ~ "T12:00:00Z")|to_timestamp
            }
          
            db.patch venda_parcela {
              field_name = "id"
              field_value = $p_item.id
              data = {vencimento: $venc_val}
            } as $parcela_corrigida
          }
        }
      
        var.update $parcelas_sanitizadas {
          value = $parcelas_sanitizadas
            |push:```
                {
                  id: $p_item.id,
                  numero_parcela: $p_item.numero_parcela,
                  total_parcelas: $p_item.total_parcelas,
                  valor: $p_item.valor,
                  vencimento: $venc_val,
                  status: $p_item.status,
                  forma_recebida: (($formas_pagamento|find:$item.id == $p_item.forma_recebida_id).Metodo ?? null),
                  recebido_em: $p_item.recebido_em,
                  recebido_por: $p_item.recebido_por,
                  cancelada_em: $p_item.cancelada_em
                }
              ```
        }
      }
    }
  }

  response = {
    id                : $venda.id
    cliente           : ```
      $cliente != null ? {
        id: $cliente.id,
        CNome: $cliente.CNome,
        CPF: $cliente.CPF,
        Telefone: $cliente.Telefone,
        Email: $cliente.Email
      } : null
      ```
    vendedor          : ```
      {
        id: $vendedor.id,
        UNome: $vendedor.UNome,
        Email: $vendedor.Email
      }
      ```
    forma_pagamento   : ```
      {
        id: $forma_pagamento.id,
        Metodo: $forma_pagamento.Metodo
      }
      ```
    status            : ```
      {
        id: $status_venda.id,
        Descricao_venda: $status_venda.Descricao_venda
      }
      ```
    Valor_bruto       : $venda.Valor_bruto
    Desconto          : ($venda.Desconto ?? 0)
    Valor_final       : $venda.Valor_final
    data_venda        : $venda.data_venda
    itens             : $itens_detalhados
    parcelas          : $parcelas_sanitizadas
    pagamentos_legados: $pagamentos_sanitizados
    cancel_reason     : $venda.cancel_reason
    cancelled_at      : $venda.cancelled_at
  }

  guid = "PNIu0yQ-bkmpLexRBXrZHAF6EcA"
}