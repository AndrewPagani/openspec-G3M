// Indicadores gerenciais com agregacoes e restricoes de perfil
// Retorna metricas financeiras, de estoque e de vendas com suporte a datas ISO YYYY-MM-DD e parametros opcionais seguros
// Parametros opcionais de filtro com aceitacao total de ausencia e nulidade
query indicadores verb=GET {
  api_group = "gerenciamento"
  auth = "user"

  input {
    text? data_inicio? filters=trim
    text? data_fim? filters=trim
    text? status_id? filters=trim
    text? vendedor_id? filters=trim
    text? forma_pagamento_id? filters=trim
    text? tipo_item? filters=trim
    text? status_veiculo_id? filters=trim
  }

  stack {
    // 1. Obter usuario e perfil autenticado
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    // 2. Parsing e validacao segura de data_inicio (suporta YYYY-MM-DD e ISO)
    var $parsed_data_inicio {
      value = null
    }
  
    conditional {
      if ($input.data_inicio != null && $input.data_inicio != "") {
        var $di_str {
          value = $input.data_inicio|to_text
        }
      
        conditional {
          if (($di_str|strlen) == 10 && ($di_str|contains:"-")) {
            var.update $parsed_data_inicio {
              value = ($di_str ~ "T00:00:00Z")|to_timestamp
            }
          }
        
          else {
            var.update $parsed_data_inicio {
              value = $di_str|to_timestamp
            }
          }
        }
      
        precondition ($parsed_data_inicio != null) {
          error_type = "inputerror"
          error = "Parametro data_inicio invalido. Formato esperado: YYYY-MM-DD"
        }
      }
    }
  
    // 3. Parsing e validacao segura de data_fim (suporta YYYY-MM-DD e ISO)
    var $parsed_data_fim {
      value = null
    }
  
    conditional {
      if ($input.data_fim != null && $input.data_fim != "") {
        var $df_str {
          value = $input.data_fim|to_text
        }
      
        conditional {
          if (($df_str|strlen) == 10 && ($df_str|contains:"-")) {
            var.update $parsed_data_fim {
              value = ($df_str ~ "T23:59:59Z")|to_timestamp
            }
          }
        
          else {
            var.update $parsed_data_fim {
              value = $df_str|to_timestamp
            }
          }
        }
      
        precondition ($parsed_data_fim != null) {
          error_type = "inputerror"
          error = "Parametro data_fim invalido. Formato esperado: YYYY-MM-DD"
        }
      }
    }
  
    conditional {
      if ($parsed_data_inicio != null && $parsed_data_fim != null) {
        precondition ($parsed_data_inicio <= $parsed_data_fim) {
          error_type = "inputerror"
          error = "Parametro data_inicio nao pode ser posterior a data_fim"
        }
      }
    }
  
    // 4. Parsing e validacao de status_id
    var $parsed_status_id {
      value = null
    }
  
    conditional {
      if ($input.status_id != null && $input.status_id != "") {
        var $s_int {
          value = $input.status_id|to_int
        }
      
        precondition ($s_int > 0) {
          error_type = "inputerror"
          error = "Parametro status_id invalido. Deve ser um numero inteiro positivo"
        }
      
        var.update $parsed_status_id {
          value = $s_int
        }
      }
    }
  
    // 5. Parsing e validacao de forma_pagamento_id
    var $parsed_forma_pagamento_id {
      value = null
    }
  
    conditional {
      if ($input.forma_pagamento_id != null && $input.forma_pagamento_id != "") {
        var $f_int {
          value = $input.forma_pagamento_id|to_int
        }
      
        precondition ($f_int > 0) {
          error_type = "inputerror"
          error = "Parametro forma_pagamento_id invalido. Deve ser um numero inteiro positivo"
        }
      
        var.update $parsed_forma_pagamento_id {
          value = $f_int
        }
      }
    }
  
    // 7. Parsing e validacao de tipo_item
    var $parsed_tipo_item {
      value = null
    }
  
    conditional {
      if ($input.tipo_item != null && $input.tipo_item != "") {
        var $ti_str {
          value = ($input.tipo_item|to_text)|to_lower
        }
      
        precondition ($ti_str == "veiculo" || $ti_str == "peca" || $ti_str == "todos") {
          error_type = "inputerror"
          error = "Parametro tipo_item invalido. Valores permitidos: veiculo, peca"
        }
      
        var.update $parsed_tipo_item {
          value = $ti_str
        }
      }
    }
  
    // 8. Parsing e validacao de status_veiculo_id
    var $parsed_status_veiculo_id {
      value = null
    }
  
    conditional {
      if ($input.status_veiculo_id != null && $input.status_veiculo_id != "") {
        var $sv_int {
          value = $input.status_veiculo_id|to_int
        }
      
        precondition ($sv_int > 0) {
          error_type = "inputerror"
          error = "Parametro status_veiculo_id invalido. Deve ser um numero inteiro positivo"
        }
      
        var.update $parsed_status_veiculo_id {
          value = $sv_int
        }
      }
    }
  
    // 9. Determinar escopo de autorizacao (Vendedor restrito exclusivamente as suas vendas)
    var $is_gerencia {
      value = ($perfil != null && $perfil.Cargo == "Gerente")
    }
  
    var $vendedor_filtro {
      value = null
    }
  
    conditional {
      if ($is_gerencia == false) {
        var.update $vendedor_filtro {
          value = $auth.id
        }
      }
    
      else {
        conditional {
          if ($input.vendedor_id != null && $input.vendedor_id != "") {
            precondition (($input.vendedor_id|to_int) > 0) {
              error_type = "inputerror"
              error = "Parametro vendedor_id invalido. Deve ser um numero inteiro positivo"
            }

            var.update $vendedor_filtro {
              value = $input.vendedor_id|to_int
            }
          }
        
          else {
            var.update $vendedor_filtro {
              value = null
            }
          }
        }
      }
    }
  
    // 10. Consultar vendas aplicando filtros de periodo, vendedor, status e forma no banco
    db.query venda {
      where = ($vendedor_filtro == null || $db.venda.vendedor_id == $vendedor_filtro) && ($parsed_status_id == null || $db.venda.status_id == $parsed_status_id) && ($parsed_forma_pagamento_id == null || $db.venda.forma_pagamento_id == $parsed_forma_pagamento_id) && ($parsed_data_inicio == null || $db.venda.data_venda >= $parsed_data_inicio) && ($parsed_data_fim == null || $db.venda.data_venda <= $parsed_data_fim)
      sort = {id: "desc"}
      return = {type: "list"}
    } as $vendas_filtradas
  
    var $total_vendas_periodo {
      value = $vendas_filtradas|count
    }
  
    var $valor_bruto_vendido {
      value = (($vendas_filtradas|map:$$.Valor_bruto)|sum) ?? 0
    }
  
    var $descontos {
      value = (($vendas_filtradas|map:$$.Desconto)|sum) ?? 0
    }
  
    // Identificar vendas canceladas e percentual
    db.query status_venda {
      where = $db.status_venda.Descricao_venda == "Cancelada" || $db.status_venda.Descricao_venda == "CANCELADA" || $db.status_venda.Descricao_venda == "cancelada"
      return = {type: "single"}
    } as $status_canc_ref
  
    var $vendas_canceladas {
      value = ($vendas_filtradas|filter:$$.status_id == $status_canc_ref.id)|count
    }
  
    var $percentual_vendas_canceladas {
      value = 0
    }
  
    conditional {
      if ($total_vendas_periodo > 0) {
        var.update $percentual_vendas_canceladas {
          value = ($vendas_canceladas * 100) / $total_vendas_periodo
        }
      }
    }
  
    // 11. Auditoria e agregacao das parcelas recebidas
    // Carrega parcelas e vendas para diagnostico e calculo consistente de recebimentos
    db.query venda_parcela {
      return = {type: "list"}
    } as $todas_as_parcelas_banco
  
    var $parcelas_candidatas {
      value = 0
    }
  
    var $parcelas_recebidas_validas {
      value = []
    }
  
    var $parcelas_fora_periodo {
      value = 0
    }
  
    var $parcelas_com_valor_zero {
      value = 0
    }
  
    var $parcelas_sem_venda {
      value = 0
    }
  
    var $total_parcelas_banco {
      value = $todas_as_parcelas_banco|count
    }
  
    var $status_distintos_raw {
      value = ($todas_as_parcelas_banco|map:$$.status)|unique
    }
  
    var $com_valor_maior_zero {
      value = 0
    }
  
    var $com_recebido_em {
      value = 0
    }
  
    var $com_forma_recebida_id {
      value = 0
    }
  
    var $com_recebido_por {
      value = 0
    }
  
    var $com_venda_id {
      value = 0
    }
  
    var $com_venda_existente {
      value = 0
    }
  
    var $totais_por_status {
      value = ```
        {
          RECEBIDA       : 0
          PENDENTE       : 0
          CANCELADA      : 0
          OUTROS_OU_NULOS: 0
        }
        ```
    }
  
    var $exemplos_parcelas_recebidas {
      value = []
    }
  
    foreach ($todas_as_parcelas_banco) {
      each as $p {
        var $st_raw {
          value = $p.status
        }
      
        var $st_norm {
          value = ($st_raw != null) ? (($st_raw|trim)|to_upper) : ""
        }
      
        conditional {
          if ($st_norm == "RECEBIDA") {
            var.update $totais_por_status {
              value = $totais_por_status
                |set:"RECEBIDA":$totais_por_status.RECEBIDA + 1
            }
          }
        
          elseif ($st_norm == "PENDENTE") {
            var.update $totais_por_status {
              value = $totais_por_status
                |set:"PENDENTE":$totais_por_status.PENDENTE + 1
            }
          }
        
          elseif ($st_norm == "CANCELADA") {
            var.update $totais_por_status {
              value = $totais_por_status
                |set:"CANCELADA":$totais_por_status.CANCELADA + 1
            }
          }
        
          else {
            var.update $totais_por_status {
              value = $totais_por_status
                |set:"OUTROS_OU_NULOS":$totais_por_status.OUTROS_OU_NULOS + 1
            }
          }
        }
      
        conditional {
          if (($p.valor ?? 0) > 0) {
            var.update $com_valor_maior_zero {
              value = $com_valor_maior_zero + 1
            }
          }
        }
      
        conditional {
          if ($p.recebido_em != null) {
            var.update $com_recebido_em {
              value = $com_recebido_em + 1
            }
          }
        }
      
        conditional {
          if ($p.forma_recebida_id != null) {
            var.update $com_forma_recebida_id {
              value = $com_forma_recebida_id + 1
            }
          }
        }
      
        conditional {
          if ($p.recebido_por != null) {
            var.update $com_recebido_por {
              value = $com_recebido_por + 1
            }
          }
        }
      
        conditional {
          if ($p.venda_id != null) {
            var.update $com_venda_id {
              value = $com_venda_id + 1
            }
          }
        }
      
        var $venda_match {
          value = null
        }

        conditional {
          if ($p.venda_id != null) {
            db.get venda {
              field_name = "id"
              field_value = $p.venda_id
            } as $venda_encontrada

            var.update $venda_match {
              value = $venda_encontrada
            }
          }
        }
      
        conditional {
          if ($venda_match != null) {
            var.update $com_venda_existente {
              value = $com_venda_existente + 1
            }
          }
        }
      
        // Filtro de escopo de autorizacao e status da venda
        var $escopo_ok {
          value = ($venda_match != null) && ($vendedor_filtro == null || $venda_match.vendedor_id == $vendedor_filtro) && ($parsed_status_id == null || $venda_match.status_id == $parsed_status_id)
        }
      
        conditional {
          if ($escopo_ok) {
            var.update $parcelas_candidatas {
              value = $parcelas_candidatas + 1
            }
          
            // Regra oficial de parcela recebida:
            // 1. Status normalizado igual a RECEBIDA; OU
            // 2. Status nao e PENDENTE nem CANCELADA, e possui a triade recebido_em, forma_recebida_id e recebido_por.
            var $is_p_recebida {
              value = false
            }
          
            conditional {
              if ($st_norm != "PENDENTE" && $st_norm != "CANCELADA") {
                conditional {
                  if ($st_norm == "RECEBIDA" || ($p.recebido_em != null && $p.forma_recebida_id != null && $p.recebido_por != null)) {
                    var.update $is_p_recebida {
                      value = true
                    }
                  }
                }
              }
            }
          
            conditional {
              if ($is_p_recebida) {
                conditional {
                  if (($p.valor ?? 0) <= 0) {
                    var.update $parcelas_com_valor_zero {
                      value = $parcelas_com_valor_zero + 1
                    }
                  }
                
                  else {
                    // Periodo: utiliza preferencialmente recebido_em, com fallback em data_venda para dados legados
                    var $dt_ref {
                      value = $p.recebido_em ?? $venda_match.data_venda
                    }
                  
                    var $passou_periodo {
                      value = ($dt_ref != null) && ($parsed_data_inicio == null || $dt_ref >= $parsed_data_inicio) && ($parsed_data_fim == null || $dt_ref <= $parsed_data_fim)
                    }
                  
                    conditional {
                      if ($passou_periodo == false) {
                        var.update $parcelas_fora_periodo {
                          value = $parcelas_fora_periodo + 1
                        }
                      }
                    
                      else {
                        // Forma de pagamento recebida (com fallback para a forma da venda)
                        var $passou_forma {
                          value = ($parsed_forma_pagamento_id == null || $p.forma_recebida_id == $parsed_forma_pagamento_id || ($p.forma_recebida_id == null && $venda_match.forma_pagamento_id == $parsed_forma_pagamento_id))
                        }
                      
                        conditional {
                          if ($passou_forma) {
                            var $item_com_venda {
                              value = {
                                id                : $p.id
                                venda_id          : $p.venda_id
                                valor             : $p.valor
                                status_original   : $st_raw
                                status_normalizado: $st_norm
                                recebido_em       : $p.recebido_em
                                forma_recebida_id : $p.forma_recebida_id
                                recebido_por      : $p.recebido_por
                                data_venda        : $venda_match.data_venda
                                Valor_final       : $venda_match.Valor_final
                              }
                            }
                          
                            array.push $parcelas_recebidas_validas {
                              value = $item_com_venda
                            }
                          
                            conditional {
                              if (($exemplos_parcelas_recebidas|count) < 10) {
                                array.push $exemplos_parcelas_recebidas {
                                  value = $item_com_venda
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        
          else {
            conditional {
              if ($p.venda_id == null || $venda_match == null) {
                var.update $parcelas_sem_venda {
                  value = $parcelas_sem_venda + 1
                }
              }
            }
          }
        }
      }
    }
  
    var $valor_liquido_recebido_periodo {
      value = (($parcelas_recebidas_validas|map:$$.valor)|sum) ?? 0
    }
  
    // Contagem de vendas distintas que possuem pelo menos uma parcela recebida valida
    var $vendas_pagas_ids {
      value = ($parcelas_recebidas_validas|map:$$.venda_id)|unique
    }
  
    var $vendas_pagas_count {
      value = $vendas_pagas_ids|count
    }
  
    // Soma de Valor_final de cada venda distinta paga (sem duplicar se houver multiplas parcelas)
    var $soma_valor_final_vendas_pagas {
      value = 0
    }
  
    foreach ($vendas_pagas_ids) {
      each as $vid {
        var $p_venda {
          value = $parcelas_recebidas_validas|find:$$.venda_id == $vid
        }
      
        conditional {
          if ($p_venda != null) {
            var.update $soma_valor_final_vendas_pagas {
              value = $soma_valor_final_vendas_pagas + ($p_venda.Valor_final ?? 0)
            }
          }
        }
      }
    }
  
    var $ticket_medio_vendas_pagas {
      value = 0
    }
  
    conditional {
      if ($vendas_pagas_count > 0) {
        var.update $ticket_medio_vendas_pagas {
          value = $soma_valor_final_vendas_pagas / $vendas_pagas_count
        }
      }
    }
  
    var $mensagem_diagnostico {
      value = ($vendas_pagas_count > 0) ? "Parcelas recebidas processadas com sucesso." : "Nenhuma parcela qualificada foi encontrada na tabela venda_parcela."
    }
  
    var $diagnostico_parcelas {
      value = {
        mensagem                     : $mensagem_diagnostico
        parcelas_candidatas          : $parcelas_candidatas
        parcelas_recebidas_validas   : $parcelas_recebidas_validas|count
        parcelas_fora_periodo        : $parcelas_fora_periodo
        parcelas_com_valor_zero      : $parcelas_com_valor_zero
        parcelas_sem_venda           : $parcelas_sem_venda
        vendas_pagas_distintas       : $vendas_pagas_count
        soma_valores_recebidos       : $valor_liquido_recebido_periodo
        soma_valor_final_vendas_pagas: $soma_valor_final_vendas_pagas
        total_parcelas_banco         : $total_parcelas_banco
        status_distintos_encontrados : $status_distintos_raw
        total_por_status             : $totais_por_status
        com_recebido_em              : $com_recebido_em
        com_forma_recebida_id        : $com_forma_recebida_id
        com_recebido_por             : $com_recebido_por
        com_valor_maior_zero         : $com_valor_maior_zero
        com_venda_valida             : $com_venda_existente
        exemplos_parcelas_recebidas  : $exemplos_parcelas_recebidas
      }
    }
  
    // 12. Agregacao vendas_por_periodo (agrupamento por data)
    var $datas_unicas {
      value = ($vendas_filtradas|map:($$.data_venda|format_timestamp:"Y-m-d":"UTC"))|unique
    }
  
    var $vendas_por_periodo {
      value = []
    }
  
    foreach ($datas_unicas) {
      each as $dt {
        var $vendas_desta_data {
          value = $vendas_filtradas|filter:($$.data_venda|format_timestamp:"Y-m-d":"UTC") == $dt
        }
      
        var $total_valor_data {
          value = (($vendas_desta_data|map:$$.Valor_final)|sum) ?? 0
        }
      
        array.push $vendas_por_periodo {
          value = {
            periodo     : $dt
            total_vendas: $vendas_desta_data|count
            valor_total : $total_valor_data
          }
        }
      }
    }
  
    // Fonte da timeline: uma linha por venda, diretamente de data_venda.
    // A agregação final é feita no estado Reflex para preservar dia/semana/mês/ano.
    var $vendas_timeline {
      value = ```
          $vendas_filtradas|map:{
            periodo: $$.data_venda,
            total_vendas: 1,
            valor_total: $$.Valor_final
          }
        ```
    }
  
    // 13. Agregacao vendas_por_status_pagamento
    db.query status_venda {
      return = {type: "list"}
    } as $lista_status_venda
  
    var $vendas_por_status_pagamento {
      value = []
    }
  
    foreach ($lista_status_venda) {
      each as $sv {
        var $vendas_deste_status {
          value = $vendas_filtradas|filter:$$.status_id == $sv.id
        }
      
        array.push $vendas_por_status_pagamento {
          value = {
            status_id   : $sv.id
            descricao   : $sv.Descricao_venda
            total_vendas: $vendas_deste_status|count
          }
        }
      }
    }
  
    // 14. Agregacao vendas_por_forma_pagamento
    db.query forma_pagamento {
      return = {type: "list"}
    } as $lista_formas_pagamento
  
    var $vendas_por_forma_pagamento {
      value = []
    }
  
    foreach ($lista_formas_pagamento) {
      each as $fp {
        var $vendas_desta_forma {
          value = $vendas_filtradas|filter:$$.forma_pagamento_id == $fp.id
        }
      
        array.push $vendas_por_forma_pagamento {
          value = {
            forma_id    : $fp.id
            metodo      : $fp.Metodo
            total_vendas: $vendas_desta_forma|count
          }
        }
      }
    }
  
    // 15. Agregacao mix_itens (veiculos vs pecas vendidos no periodo)
    db.query venda_item {
      join = {
        venda: {
          table: "venda"
          where: $db.venda_item.venda_id == $db.venda.id
        }
      }
    
      where = ($vendedor_filtro == null || $db.venda.vendedor_id == $vendedor_filtro) && ($parsed_status_id == null || $db.venda.status_id == $parsed_status_id) && ($parsed_forma_pagamento_id == null || $db.venda.forma_pagamento_id == $parsed_forma_pagamento_id) && ($parsed_data_inicio == null || $db.venda.data_venda >= $parsed_data_inicio) && ($parsed_data_fim == null || $db.venda.data_venda <= $parsed_data_fim) && ($parsed_tipo_item == null || ($parsed_tipo_item == "todos") || ($parsed_tipo_item == "veiculo" && $db.venda_item.veiculo_id != null) || ($parsed_tipo_item == "peca" && $db.venda_item.peca_id != null))
      return = {type: "list"}
    } as $itens_das_vendas
  
    var $mix_itens {
      value = []
    }
  
    conditional {
      if (($itens_das_vendas|count) > 0) {
        var $qtd_itens_veic {
          value = ($itens_das_vendas|filter:$$.veiculo_id != null)|count
        }
      
        var $qtd_itens_pecas {
          value = ((($itens_das_vendas|filter:$$.peca_id != null)|map:$$.qtd)|sum) ?? 0
        }
      
        var.update $mix_itens {
          value = [
            {
              tipo      : "veiculo"
              quantidade: $qtd_itens_veic
            },
            {
              tipo      : "peca"
              quantidade: $qtd_itens_pecas
            }
          ]
        }
      }
    }
  
    // 16. Veiculos vendidos por marca
    var $veiculos_vendidos_por_marca {
      value = []
    }
  
    var $itens_veiculos {
      value = $itens_das_vendas|filter:$$.veiculo_id != null
    }
  
    conditional {
      if (($itens_veiculos|count) > 0) {
        var $veiculo_ids_vendidos {
          value = ($itens_veiculos|map:$$.veiculo_id)|unique
        }
      
        db.query veiculo {
          where = $db.veiculo.id in $veiculo_ids_vendidos
          return = {type: "list"}
        } as $veiculos_cadastrados
      
        var $veiculos_itens_formatados {
          value = []
        }
      
        var $valor_total_veiculos_vendidos {
          value = 0
        }
      
        foreach ($itens_veiculos) {
          each as $iv {
            var $veic_ref {
              value = $veiculos_cadastrados|find:$$.id == $iv.veiculo_id
            }
          
            var $marca_nome {
              value = "Sem marca"
            }
          
            conditional {
              if ($veic_ref != null && $veic_ref.Marca != null && (($veic_ref.Marca|trim) != "")) {
                var.update $marca_nome {
                  value = $veic_ref.Marca|trim
                }
              }
            }
          
            var $iv_qtd {
              value = $iv.qtd ?? 1
            }
          
            var $iv_val {
              value = $iv_qtd * ($iv.preco_unit ?? 0)
            }
          
            var.update $valor_total_veiculos_vendidos {
              value = $valor_total_veiculos_vendidos + $iv_val
            }
          
            array.push $veiculos_itens_formatados {
              value = {marca: $marca_nome, qtd: $iv_qtd, valor: $iv_val}
            }
          }
        }
      
        var $marcas_unicas {
          value = ($veiculos_itens_formatados|map:$$.marca)|unique
        }
      
        foreach ($marcas_unicas) {
          each as $m {
            var $itens_marca {
              value = $veiculos_itens_formatados|filter:$$.marca == $m
            }
          
            var $qtd_marca {
              value = (($itens_marca|map:$$.qtd)|sum) ?? 0
            }
          
            var $valor_marca {
              value = (($itens_marca|map:$$.valor)|sum) ?? 0
            }
          
            var $pct_marca {
              value = 0
            }
          
            conditional {
              if ($valor_total_veiculos_vendidos > 0) {
                var.update $pct_marca {
                  value = (($valor_marca * 100) / $valor_total_veiculos_vendidos)|round:2
                }
              }
            }
          
            array.push $veiculos_vendidos_por_marca {
              value = {
                marca      : $m
                quantidade : $qtd_marca
                valor_total: $valor_marca
                percentual : $pct_marca
              }
            }
          }
        }
      
        var.update $veiculos_vendidos_por_marca {
          value = $veiculos_vendidos_por_marca
            |sort:"valor_total":"number":false
        }
      }
    }
  
    // 17. Pecas vendidas por categoria
    var $pecas_vendidas_por_categoria {
      value = []
    }
  
    var $itens_pecas {
      value = $itens_das_vendas|filter:$$.peca_id != null
    }
  
    conditional {
      if (($itens_pecas|count) > 0) {
        var $peca_ids_vendidas {
          value = ($itens_pecas|map:$$.peca_id)|unique
        }
      
        db.query peca {
          where = $db.peca.id in $peca_ids_vendidas
          return = {type: "list"}
        } as $pecas_cadastradas
      
        var $area_ids {
          value = (($pecas_cadastradas|filter:$$.area_id != null)|map:$$.area_id)|unique
        }
      
        var $areas_cadastradas {
          value = []
        }
      
        conditional {
          if (($area_ids|count) > 0) {
            db.query veiculo_area {
              where = $db.veiculo_area.id in $area_ids
              return = {type: "list"}
            } as $areas_cadastradas_db
          
            var.update $areas_cadastradas {
              value = $areas_cadastradas_db
            }
          }
        }
      
        var $pecas_itens_formatados {
          value = []
        }
      
        var $valor_total_pecas_vendidas {
          value = 0
        }
      
        foreach ($itens_pecas) {
          each as $ip {
            var $peca_ref {
              value = $pecas_cadastradas|find:$$.id == $ip.peca_id
            }
          
            var $cat_nome {
              value = "Sem categoria"
            }
          
            conditional {
              if ($peca_ref != null && $peca_ref.area_id != null) {
                var $area_ref {
                  value = $areas_cadastradas|find:$$.id == $peca_ref.area_id
                }
              
                conditional {
                  if ($area_ref != null && $area_ref.Secao != null && (($area_ref.Secao|trim) != "")) {
                    var.update $cat_nome {
                      value = $area_ref.Secao|trim
                    }
                  }
                }
              }
            }
          
            var $ip_qtd {
              value = $ip.qtd ?? 1
            }
          
            var $ip_val {
              value = $ip_qtd * ($ip.preco_unit ?? 0)
            }
          
            var.update $valor_total_pecas_vendidas {
              value = $valor_total_pecas_vendidas + $ip_val
            }
          
            array.push $pecas_itens_formatados {
              value = {categoria: $cat_nome, qtd: $ip_qtd, valor: $ip_val}
            }
          }
        }
      
        var $categorias_unicas {
          value = ($pecas_itens_formatados|map:$$.categoria)|unique
        }
      
        foreach ($categorias_unicas) {
          each as $c {
            var $itens_cat {
              value = $pecas_itens_formatados|filter:$$.categoria == $c
            }
          
            var $qtd_cat {
              value = (($itens_cat|map:$$.qtd)|sum) ?? 0
            }
          
            var $valor_cat {
              value = (($itens_cat|map:$$.valor)|sum) ?? 0
            }
          
            var $pct_cat {
              value = 0
            }
          
            conditional {
              if ($valor_total_pecas_vendidas > 0) {
                var.update $pct_cat {
                  value = (($valor_cat * 100) / $valor_total_pecas_vendidas)|round:2
                }
              }
            }
          
            array.push $pecas_vendidas_por_categoria {
              value = {
                categoria  : $c
                quantidade : $qtd_cat
                valor_total: $valor_cat
                percentual : $pct_cat
              }
            }
          }
        }
      
        var.update $pecas_vendidas_por_categoria {
          value = $pecas_vendidas_por_categoria
            |sort:"valor_total":"number":false
        }
      }
    }
  
    // 18. Pecas vendidas por fabricante (indisponivel: nao ha campo fabricante na tabela peca)
    var $pecas_vendidas_por_fabricante {
      value = []
    }
  
    var $fabricante_disponivel {
      value = false
    }
  
    // 19. Conversao de estoque (indisponivel: nao ha estrutura de propostas/orcamentos no schema)
    var $conversao_estoque {
      value = ```
        {
          disponivel           : false
          propostas_total      : 0
          propostas_convertidas: 0
          taxa_conversao       : 0
        }
        ```
    }
  
    // 20. Giro de estoque (indisponivel: nao ha historico de movimentacoes de estoque no schema)
    var $giro_estoque {
      value = ```
        {
          disponivel         : false
          entradas_quantidade: 0
          saidas_quantidade  : 0
          estoque_medio      : 0
          giro               : 0
        }
        ```
    }
  
    // 21. Agregacoes gerenciais exclusivas (estoque global e vendas_por_vendedor)
    var $veiculos_disponiveis {
      value = 0
    }
  
    var $valor_veiculos_disponiveis {
      value = 0
    }
  
    var $pecas_qtd_disponivel {
      value = 0
    }
  
    var $valor_estoque_pecas {
      value = 0
    }
  
    var $pecas_sem_estoque {
      value = 0
    }
  
    var $pecas_baixo_estoque {
      value = []
    }
  
    var $veiculos_por_status {
      value = []
    }
  
    var $vendas_por_vendedor {
      value = []
    }
  
    conditional {
      if ($is_gerencia) {
        // Status veiculo disponivel
        db.query status_veiculo {
          where = $db.status_veiculo.Descricao == "Disponível" || $db.status_veiculo.Descricao == "Disponivel"
          return = {type: "single"}
        } as $status_disp
      
        var $status_veic_filtro {
          value = ($parsed_status_veiculo_id ?? $status_disp.id)
        }
      
        db.query veiculo {
          where = $status_veic_filtro == null || $db.veiculo.status_id == $status_veic_filtro
          return = {type: "list"}
        } as $veiculos_disp_list
      
        var.update $veiculos_disponiveis {
          value = $veiculos_disp_list|count
        }
      
        var.update $valor_veiculos_disponiveis {
          value = (($veiculos_disp_list|map:$$.Preco)|sum) ?? 0
        }
      
        // Metricas de pecas
        db.query peca {
          where = $db.peca.qtd_disp > 0
          return = {type: "list"}
        } as $pecas_em_estoque
      
        var.update $pecas_qtd_disponivel {
          value = (($pecas_em_estoque|map:$$.qtd_disp)|sum) ?? 0
        }
      
        var.update $valor_estoque_pecas {
          value = (($pecas_em_estoque|map:($$.PCvalor * $$.qtd_disp))|sum) ?? 0
        }
      
        // Consulta pecas com estoque baixo (qtd_disp <= 5 ou null)
        db.query peca {
          where = $db.peca.qtd_disp <= 5 || $db.peca.qtd_disp == null
          return = {type: "list"}
        } as $pecas_baixo_estoque_db
      
        // Mapeia pecas de baixo estoque com id, nome, quantidade e valor unitario
        var.update $pecas_baixo_estoque {
          value = ```
            $pecas_baixo_estoque_db|map:{
              id: $$.id,
              nome: $$.PCNome,
              quantidade: ($$.qtd_disp ?? 0),
              valor_unitario: ($$.PCvalor ?? 0)
            }
            ```
        }
      
        // Atualiza pecas_sem_estoque com a contagem da lista pecas_baixo_estoque
        var.update $pecas_sem_estoque {
          value = $pecas_baixo_estoque|count
        }
      
        // veiculos_por_status
        db.query status_veiculo {
          return = {type: "list"}
        } as $todos_status_veic
      
        db.query veiculo {
          return = {type: "list"}
        } as $todos_veiculos_base
      
        var.update $veiculos_por_status {
          value = []
        }
      
        foreach ($todos_status_veic) {
          each as $tsv {
            var $veic_deste_status {
              value = $todos_veiculos_base|filter:$$.status_id == $tsv.id
            }
          
            array.push $veiculos_por_status {
              value = {
                status_id : $tsv.id
                descricao : $tsv.Descricao
                quantidade: $veic_deste_status|count
              }
            }
          }
        }
      
        // vendas_por_vendedor
        db.query user {
          return = {type: "list"}
        } as $todos_usuarios
      
        var.update $vendas_por_vendedor {
          value = []
        }
      
        foreach ($todos_usuarios) {
          each as $tu {
            var $vendas_deste_vendedor {
              value = $vendas_filtradas|filter:$$.vendedor_id == $tu.id
            }
          
            var $valor_deste_vendedor {
              value = (($vendas_deste_vendedor|map:$$.Valor_final)|sum) ?? 0
            }
          
            array.push $vendas_por_vendedor {
              value = {
                vendedor_id : $tu.id
                nome        : $tu.UNome
                total_vendas: $vendas_deste_vendedor|count
                valor_total : $valor_deste_vendedor
              }
            }
          }
        }
      }
    }
  }

  response = {
    kpis                         : ```
      {
        total_vendas_periodo: $total_vendas_periodo,
        valor_bruto_vendido: $valor_bruto_vendido,
        valor_liquido_recebido_periodo: $valor_liquido_recebido_periodo,
        vendas_pagas: $vendas_pagas_count,
        ticket_medio_vendas_pagas: $ticket_medio_vendas_pagas,
        descontos: $descontos,
        vendas_canceladas: $vendas_canceladas,
        percentual_vendas_canceladas: $percentual_vendas_canceladas,
        veiculos_disponiveis: $veiculos_disponiveis,
        pecas_qtd_disponivel: $pecas_qtd_disponivel
      }
      ```
    vendas_por_periodo           : $vendas_por_periodo
    vendas_timeline              : $vendas_timeline
    vendas_por_status_pagamento  : $vendas_por_status_pagamento
    vendas_por_forma_pagamento   : $vendas_por_forma_pagamento
    vendas_por_vendedor          : $vendas_por_vendedor
    mix_itens                    : $mix_itens
    veiculos_por_status          : $veiculos_por_status
    valor_veiculos_disponiveis   : $valor_veiculos_disponiveis
    valor_estoque_pecas          : $valor_estoque_pecas
    pecas_sem_estoque            : $pecas_sem_estoque
    pecas_baixo_estoque          : $pecas_baixo_estoque
    veiculos_vendidos_por_marca  : $veiculos_vendidos_por_marca
    pecas_vendidas_por_categoria : $pecas_vendidas_por_categoria
    pecas_vendidas_por_fabricante: $pecas_vendidas_por_fabricante
    fabricante_disponivel        : $fabricante_disponivel
    conversao_estoque            : $conversao_estoque
    giro_estoque                 : $giro_estoque
    diagnostico_parcelas         : $diagnostico_parcelas
  }

  test "chamada sem nenhum filtro" {
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "chamada com filtros opcionais vazios" {
    input = {status_id: "", data_inicio: "", data_fim: null}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro data_inicio isolado formato YYYY-MM-DD" {
    input = {data_inicio: "2025-01-01"}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro data_fim isolado formato YYYY-MM-DD" {
    input = {data_fim: "2025-01-31"}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "datas formato YYYY-MM-DD juntas" {
    input = {data_inicio: "2025-01-01", data_fim: "2025-01-31"}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro status_id isolado" {
    input = {status_id: 1}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro vendedor_id isolado" {
    input = {vendedor_id: 1}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro forma_pagamento_id isolado" {
    input = {forma_pagamento_id: 1}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro tipo_item isolado" {
    input = {tipo_item: "veiculo"}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "filtro status_veiculo_id isolado" {
    input = {status_veiculo_id: 1}
  
    expect.to_be_defined ($response.kpis.total_vendas_periodo)
  }

  test "rejeita data_inicio com formato invalido" {
    input = {data_inicio: "data_invalida_nao_data"}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "rejeita status_id negativo" {
    input = {status_id: -5}
  
    expect.to_throw {
      exception = ""
    }
  }

  test "valida novas series de dashboard" {
    expect.to_be_defined ($response.veiculos_vendidos_por_marca)
    expect.to_be_defined ($response.pecas_vendidas_por_categoria)
    expect.to_be_defined ($response.pecas_vendidas_por_fabricante)
    expect.to_be_defined ($response.fabricante_disponivel)
    expect.to_be_defined ($response.conversao_estoque)
    expect.to_be_defined ($response.giro_estoque)
    expect.to_be_defined ($response.diagnostico_parcelas)
  }

  guid = "zilVzjhxE40-X8XJFz5HtV9lwdE"
}