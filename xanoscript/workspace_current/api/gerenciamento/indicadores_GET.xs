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
  
    // 9. Determinar escopo de autorizacao (Vendedor restrito exclusivamente as suas vendas)
    var $cargo_normalizado {
      value = (($perfil.Cargo ?? "")|to_text)|to_lower
    }

    var $is_gerencia {
      value = ($perfil != null && (
        ($cargo_normalizado|contains:"gerente")
        || ($cargo_normalizado|contains:"administrador")
        || ($cargo_normalizado|contains:"admin")
      ))
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
        var.update $vendedor_filtro {
          value = $parsed_vendedor_id
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
  
    // 11. Considerar somente baixas manuais locais; o periodo segue data_venda.
    // recebido_em e opcional no schema e nao pode excluir uma venda ja recebida.
    db.query venda_parcela {
      join = {
        venda: {
          table: "venda"
          where: $db.venda_parcela.venda_id == $db.venda.id
        }
      }
    
      where = $db.venda_parcela.status == "RECEBIDA" && ($vendedor_filtro == null || $db.venda.vendedor_id == $vendedor_filtro) && ($parsed_status_id == null || $db.venda.status_id == $parsed_status_id) && ($parsed_forma_pagamento_id == null || $db.venda_parcela.forma_recebida_id == $parsed_forma_pagamento_id) && ($parsed_data_inicio == null || $db.venda.data_venda >= $parsed_data_inicio) && ($parsed_data_fim == null || $db.venda.data_venda <= $parsed_data_fim)
      return = {type: "list"}
    } as $parcelas_recebidas
  
    var $valor_liquido_recebido_periodo {
      value = (($parcelas_recebidas|map:$$.valor)|sum) ?? 0
    }
  
    var $vendas_pagas_ids {
      value = ($parcelas_recebidas|map:$$.venda_id)|unique
    }
  
    var $vendas_pagas_count {
      value = $vendas_pagas_ids|count
    }
  
    var $vendas_pagas_detalhe {
      value = $vendas_filtradas|filter:($vendas_pagas_ids|some:$$ == $this.id)
    }
  
    var $ticket_medio_vendas_pagas {
      value = 0
    }
  
    conditional {
      if ($vendas_pagas_count > 0) {
        var $soma_valor_pagas {
          value = (($vendas_pagas_detalhe|map:$$.Valor_final)|sum) ?? 0
        }
      
        var.update $ticket_medio_vendas_pagas {
          value = $soma_valor_pagas / $vendas_pagas_count
        }
      }
    }
  
    // 12. Agregacao vendas_por_periodo (agrupamento por data)
    var $datas_unicas {
      value = ($vendas_filtradas|map:($$.data_venda|format_timestamp:"Y-m-d":"UTC"))|unique
    }
  
    var $vendas_por_periodo {
      value = ```
        $datas_unicas|map:{
                periodo: $$,
                total_vendas: ($vendas_filtradas|filter:($$.data_venda|format_timestamp:"Y-m-d":"UTC") == $this)|count,
                valor_total: ((($vendas_filtradas|filter:($$.data_venda|format_timestamp:"Y-m-d":"UTC") == $this)|map:$$.Valor_final)|sum) ?? 0
              }
        ```
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
      value = ```
        $lista_status_venda|map:{
                status_id: $$.id,
                descricao: $$.Descricao_venda,
                total_vendas: ($vendas_filtradas|filter:$$.status_id == $this.id)|count
              }
        ```
    }
  
    // 14. Agregacao vendas_por_forma_pagamento
    db.query forma_pagamento {
      return = {type: "list"}
    } as $lista_formas_pagamento
  
    var $vendas_por_forma_pagamento {
      value = ```
        $lista_formas_pagamento|map:{
                forma_id: $$.id,
                metodo: $$.Metodo,
                total_vendas: ($vendas_filtradas|filter:$$.forma_pagamento_id == $this.id)|count
              }
        ```
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
              tipo: "veiculo",
              quantidade: $qtd_itens_veic
            },
            {
              tipo: "peca",
              quantidade: $qtd_itens_pecas
            }
          ]
        }
      }
    }
  
    // 16. Agregacoes gerenciais exclusivas (estoque global e vendas_por_vendedor)
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
      
        db.query peca {
          where = $db.peca.qtd_disp <= 5 || $db.peca.qtd_disp == null
          return = {type: "list"}
        } as $pecas_baixo_estoque_db

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
          value = ```
            $todos_status_veic|map:{
                        status_id: $$.id,
                        descricao: $$.Descricao,
                        quantidade: ($todos_veiculos_base|filter:$$.status_id == $this.id)|count
                      }
            ```
        }
      
        // vendas_por_vendedor
        db.query user {
          return = {type: "list"}
        } as $todos_usuarios
      
        var.update $vendas_por_vendedor {
          value = ```
            $todos_usuarios|map:{
                        vendedor_id: $$.id,
                        nome: $$.UNome,
                        total_vendas: ($vendas_filtradas|filter:$$.vendedor_id == $this.id)|count,
                        valor_total: ((($vendas_filtradas|filter:$$.vendedor_id == $this.id)|map:$$.Valor_final)|sum) ?? 0
                      }
            ```
        }
      }
    }
  }

  response = {
    kpis                       : ```
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
    vendas_por_periodo         : $vendas_por_periodo
    vendas_timeline             : $vendas_timeline
    vendas_por_status_pagamento: $vendas_por_status_pagamento
    vendas_por_forma_pagamento : $vendas_por_forma_pagamento
    vendas_por_vendedor        : $vendas_por_vendedor
    mix_itens                  : $mix_itens
    veiculos_por_status        : $veiculos_por_status
    valor_veiculos_disponiveis : $valor_veiculos_disponiveis
    valor_estoque_pecas        : $valor_estoque_pecas
    pecas_sem_estoque          : $pecas_sem_estoque
    pecas_baixo_estoque        : $pecas_baixo_estoque
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

  guid = "zilVzjhxE40-X8XJFz5HtV9lwdE"
}