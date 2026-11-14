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
    // 1. Obter usuario e perfil autenticado (Gerente e Vendedor permitidos; Cliente negado)
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    precondition ($perfil != null && ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Vendedor")) {
      error_type = "accessdenied"
      error = "Acesso nao autorizado ao dashboard gerencial"
    }
  
    var $is_gerente {
      value = ($perfil.Cargo == "Gerente")
    }
  
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
  
    // 5. Parsing e validacao de vendedor_id
    var $parsed_vendedor_id {
      value = null
    }
  
    conditional {
      if ($input.vendedor_id != null && $input.vendedor_id != "") {
        var $v_int {
          value = $input.vendedor_id|to_int
        }
      
        precondition ($v_int > 0) {
          error_type = "inputerror"
          error = "Parametro vendedor_id invalido. Deve ser um numero inteiro positivo"
        }
      
        var.update $parsed_vendedor_id {
          value = $v_int
        }
      }
    }
  
    // 6. Parsing e validacao de forma_pagamento_id
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
  
    // Determinar escopo de autorizacao (Vendedor restrito exclusivamente as suas vendas)
    var $vendedor_filtro {
      value = null
    }
  
    conditional {
      if ($is_gerente == false) {
        var.update $vendedor_filtro {
          value = $auth.id
        }
      }
    
      else {
        var.update $vendedor_filtro {
          value = $parsed_vendedor_id
        }
      }
    }
  
    // 9. Consultar vendas aplicando filtros de periodo, vendedor, status e forma no banco
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
  
    // 10. Processamento direto da tabela venda para vendas concluidas, vendas pagas e faturamento recebido
    var $vendas_concluidas {
      value = 0
    }
  
    var $vendas_pagas_ids {
      value = []
    }
  
    var $soma_valor_final_vendas_pagas {
      value = 0
    }
  
    var $valor_liquido_recebido_periodo {
      value = 0
    }
  
    var $exemplos_parcelas_recebidas {
      value = []
    }
  
    foreach ($vendas_filtradas) {
      each as $vf_item {
        var $status_venda_item {
          value = null
        }
      
        conditional {
          if ($vf_item.status_id != null) {
            db.get status_venda {
              field_name = "id"
              field_value = $vf_item.status_id
            } as $db_status_venda_item
          
            var.update $status_venda_item {
              value = $db_status_venda_item
            }
          }
        }
      
        var $desc_st_lower {
          value = ($status_venda_item != null && $status_venda_item.Descricao_venda != null) ? (($status_venda_item.Descricao_venda|trim)|to_lower) : ""
        }
      
        var $is_concluida {
          value = ($desc_st_lower == "concluída" || $desc_st_lower == "concluida")
        }
      
        conditional {
          if ($is_concluida) {
            var.update $vendas_concluidas {
              value = $vendas_concluidas + 1
            }
          }
        }
      
        var $is_paga_status {
          value = ($desc_st_lower == "paga" || $desc_st_lower == "concluída" || $desc_st_lower == "concluida")
        }
      
        db.query venda_parcela {
          where = $db.venda_parcela.venda_id == $vf_item.id
          return = {type: "list"}
        } as $parcs_venda
      
        var $tem_parc_recebida {
          value = false
        }
      
        var $soma_parcs_recebidas {
          value = 0
        }
      
        foreach ($parcs_venda) {
          each as $pv {
            var $pv_st {
              value = ($pv.status != null) ? (($pv.status|trim)|to_upper) : ""
            }
          
            conditional {
              if ($pv_st != "CANCELADA") {
                conditional {
                  if ($pv_st == "RECEBIDA" || ($pv.recebido_em != null && $pv.forma_recebida_id != null && $pv.recebido_por != null) || $is_paga_status) {
                    var.update $tem_parc_recebida {
                      value = true
                    }
                  
                    var.update $soma_parcs_recebidas {
                      value = $soma_parcs_recebidas + ($pv.valor ?? 0)
                    }
                  
                    conditional {
                      if (($exemplos_parcelas_recebidas|count) < 10) {
                        array.push $exemplos_parcelas_recebidas {
                          value = {
                            id                : $pv.id
                            venda_id          : $vf_item.id
                            valor             : $pv.valor
                            status_original   : $pv.status
                            status_normalizado: ($is_paga_status && $pv_st == "PENDENTE" ? "RECEBIDA (VENDA " ~ ($desc_st_lower|to_upper) ~ ")" : $pv_st)
                            recebido_em       : ($pv.recebido_em ?? $vf_item.data_venda)
                            forma_recebida_id : ($pv.forma_recebida_id ?? $vf_item.forma_pagamento_id)
                            recebido_por      : $pv.recebido_por
                            data_venda        : $vf_item.data_venda
                            Valor_final       : $vf_item.Valor_final
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
      
        conditional {
          if ($is_paga_status || $tem_parc_recebida) {
            array.push $vendas_pagas_ids {
              value = $vf_item.id
            }
          
            var.update $soma_valor_final_vendas_pagas {
              value = $soma_valor_final_vendas_pagas + ($vf_item.Valor_final ?? 0)
            }
          
            var $val_recebido_venda {
              value = ($soma_parcs_recebidas > 0) ? $soma_parcs_recebidas : ($vf_item.Valor_final ?? 0)
            }
          
            var.update $valor_liquido_recebido_periodo {
              value = $valor_liquido_recebido_periodo + $val_recebido_venda
            }
          }
        }
      }
    }
  
    var $vendas_pagas_count {
      value = ($vendas_pagas_ids|unique)|count
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
  
    // Auditoria da tabela venda_parcela para diagnostico
    db.query venda_parcela {
      return = {type: "list"}
    } as $todas_as_parcelas_banco
  
    var $total_parcelas_banco {
      value = $todas_as_parcelas_banco|count
    }
  
    var $status_distintos_raw {
      value = ($todas_as_parcelas_banco|map:$$.status)|unique
    }
  
    var $com_valor_maior_zero {
      value = ($todas_as_parcelas_banco|filter:($$.valor ?? 0) > 0)|count
    }
  
    var $com_recebido_em {
      value = ($todas_as_parcelas_banco|filter:$$.recebido_em != null)|count
    }
  
    var $com_forma_recebida_id {
      value = ($todas_as_parcelas_banco|filter:$$.forma_recebida_id != null)|count
    }
  
    var $com_recebido_por {
      value = ($todas_as_parcelas_banco|filter:$$.recebido_por != null)|count
    }
  
    var $com_venda_id {
      value = ($todas_as_parcelas_banco|filter:$$.venda_id != null)|count
    }
  
    var $totais_por_status {
      value = {
        RECEBIDA       : ($todas_as_parcelas_banco|filter:($$.status|to_upper) == "RECEBIDA")|count
        PENDENTE       : ($todas_as_parcelas_banco|filter:($$.status|to_upper) == "PENDENTE")|count
        CANCELADA      : ($todas_as_parcelas_banco|filter:($$.status|to_upper) == "CANCELADA")|count
        OUTROS_OU_NULOS: ($todas_as_parcelas_banco|filter:($$.status|to_upper) != "RECEBIDA" && ($$.status|to_upper) != "PENDENTE" && ($$.status|to_upper) != "CANCELADA")|count
      }
    }
  
    var $mensagem_diagnostico {
      value = ($vendas_pagas_count > 0) ? "Vendas pagas e parcelas processadas com sucesso." : "Nenhuma venda com status Paga/Concluida ou parcela recebida encontrada no periodo."
    }
  
    var $diagnostico_parcelas {
      value = ```
        {
          mensagem                     : $mensagem_diagnostico
          total_parcelas_banco         : $total_parcelas_banco
          parcelas_candidatas          : $total_vendas_periodo
          parcelas_recebidas_validas   : $vendas_pagas_count
          parcelas_fora_periodo        : 0
          parcelas_com_valor_zero      : 0
          parcelas_sem_venda           : 0
          vendas_pagas_distintas       : $vendas_pagas_count
          soma_valores_recebidos       : $valor_liquido_recebido_periodo
          soma_valor_final_vendas_pagas: $soma_valor_final_vendas_pagas
          status_distintos_encontrados : $status_distintos_raw
          total_por_status             : $totais_por_status
          com_recebido_em              : $com_recebido_em
          com_forma_recebida_id        : $com_forma_recebida_id
          com_recebido_por             : $com_recebido_por
          com_valor_maior_zero         : $com_valor_maior_zero
          com_venda_valida             : $total_parcelas_banco
          exemplos_parcelas_recebidas  : $exemplos_parcelas_recebidas
        }
        ```
    }
  
    // 11. Agregacao vendas_por_periodo (agrupamento por data)
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
  
    // 12. Agregacao vendas_por_status_pagamento
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
      
        var $valor_deste_status {
          value = (($vendas_deste_status|map:$$.Valor_final)|sum) ?? 0
        }
      
        array.push $vendas_por_status_pagamento {
          value = {
            status_id   : $sv.id
            descricao   : $sv.Descricao_venda
            total_vendas: $vendas_deste_status|count
            valor_total : $valor_deste_status
          }
        }
      }
    }
  
    // 13. Agregacao vendas_por_forma_pagamento
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
      
        var $valor_desta_forma {
          value = (($vendas_desta_forma|map:$$.Valor_final)|sum) ?? 0
        }
      
        array.push $vendas_por_forma_pagamento {
          value = {
            forma_id    : $fp.id
            metodo      : $fp.Metodo
            total_vendas: $vendas_desta_forma|count
            valor_total : $valor_desta_forma
          }
        }
      }
    }
  
    // 14. Agregacao mix_itens (veiculos vs pecas vendidos no periodo)
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
  
    // 15. Veiculos vendidos por marca
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
  
    // 16. Pecas vendidas por categoria
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
  
    // 17. Pecas vendidas por fabricante (indisponivel: nao ha campo fabricante na tabela peca)
    var $pecas_vendidas_por_fabricante {
      value = []
    }
  
    var $fabricante_disponivel {
      value = false
    }
  
    // 18. Conversao de estoque (indisponivel: nao ha estrutura de propostas/orcamentos no schema)
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
  
    // 19. Giro de estoque (indisponivel: nao ha historico de movimentacoes de estoque no schema)
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
  
    // 20. Agregacoes gerenciais exclusivas (estoque global e vendas_por_vendedor)
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
      if ($is_gerente) {
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
        vendas_concluidas: $vendas_concluidas,
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
    expect.to_be_defined ($response.kpis.vendas_concluidas)
  }

  guid = "zilVzjhxE40-X8XJFz5HtV9lwdE"
}