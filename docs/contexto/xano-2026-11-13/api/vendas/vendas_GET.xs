// Listagem de vendas com autorizacao por perfil e filtros
// Lista vendas isolando vendedor aos seus proprios registros e permitindo a gerencia filtrar por equipe, datas e status
// Parametros de consulta e paginacao com filtros de data opcionais compativeis com YYYY-MM-DD
query vendas verb=GET {
  api_group = "vendas"
  auth = "user"

  input {
    int page?=1 filters=min:1
    int per_page?=20 filters=min:1|max:100
    text busca? filters=trim
    json? cliente_id?
    json? vendedor_id?
    json? status_id?
    json? forma_pagamento_id?
    json? data_inicio?
    json? data_fim?
  }

  stack {
    // Obter perfil do usuario autenticado
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $user
  
    db.get perfil {
      field_name = "id"
      field_value = $user.perfil_id
    } as $perfil
  
    var $busca_id {
      value = null
    }
  
    conditional {
      if ($input.busca != null && $input.busca != "") {
        var.update $busca_id {
          value = $input.busca|to_int
        }
      }
    }
  
    // Se o usuario for Vendedor, forcar filtro para seu proprio id
    var $vendedor_filtro {
      value = 0
    }
  
    // Parsing seguro de vendedor_id
    var $parsed_vendedor_id {
      value = 0
    }
  
    conditional {
      if ($input.vendedor_id != null && $input.vendedor_id != "" && $input.vendedor_id != [] && $input.vendedor_id != "{}") {
        var $v_int {
          value = $input.vendedor_id|to_int
        }
      
        conditional {
          if ($v_int > 0) {
            var.update $parsed_vendedor_id {
              value = $v_int
            }
          }
        }
      }
    }
  
    conditional {
      if ($perfil.Cargo == "Vendedor") {
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
  
    // Parsing seguro de cliente_id
    var $parsed_cliente_id {
      value = 0
    }
  
    conditional {
      if ($input.cliente_id != null && $input.cliente_id != "" && $input.cliente_id != [] && $input.cliente_id != "{}") {
        var $c_int {
          value = $input.cliente_id|to_int
        }
      
        conditional {
          if ($c_int > 0) {
            var.update $parsed_cliente_id {
              value = $c_int
            }
          }
        }
      }
    }
  
    // Parsing seguro de status_id
    var $parsed_status_id {
      value = 0
    }
  
    conditional {
      if ($input.status_id != null && $input.status_id != "" && $input.status_id != [] && $input.status_id != "{}") {
        var $s_int {
          value = $input.status_id|to_int
        }
      
        conditional {
          if ($s_int > 0) {
            var.update $parsed_status_id {
              value = $s_int
            }
          }
        }
      }
    }
  
    // Parsing seguro de forma_pagamento_id
    var $parsed_forma_pagamento_id {
      value = 0
    }
  
    conditional {
      if ($input.forma_pagamento_id != null && $input.forma_pagamento_id != "" && $input.forma_pagamento_id != [] && $input.forma_pagamento_id != "{}") {
        var $f_int {
          value = $input.forma_pagamento_id|to_int
        }
      
        conditional {
          if ($f_int > 0) {
            var.update $parsed_forma_pagamento_id {
              value = $f_int
            }
          }
        }
      }
    }
  
    // Parsing seguro de datas (suporta YYYY-MM-DD e ISO)
    var $parsed_data_inicio {
      value = null
    }
  
    conditional {
      if ($input.data_inicio != null && $input.data_inicio != "" && $input.data_inicio != [] && $input.data_inicio != "{}") {
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
      }
    }
  
    var $parsed_data_fim {
      value = null
    }
  
    conditional {
      if ($input.data_fim != null && $input.data_fim != "" && $input.data_fim != [] && $input.data_fim != "{}") {
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
      }
    }
  
    // Consultar vendas aplicando filtros e paginacao no banco
    db.query venda {
      join = {
        cliente: {
          table: "cliente"
          where: $db.venda.cliente_id == $db.cliente.id
        }
      }
    
      where = ($parsed_cliente_id == 0 || $db.venda.cliente_id == $parsed_cliente_id) && ($parsed_status_id == 0 || $db.venda.status_id == $parsed_status_id) && ($parsed_forma_pagamento_id == 0 || $db.venda.forma_pagamento_id == $parsed_forma_pagamento_id) && ($parsed_data_inicio == null || $db.venda.data_venda >= $parsed_data_inicio) && ($parsed_data_fim == null || $db.venda.data_venda <= $parsed_data_fim) && (($input.busca == null || $input.busca == "") || ($busca_id != null && $db.venda.id == $busca_id) || ($db.cliente.CNome includes $input.busca) || ($db.cliente.CPF includes $input.busca))
      sort = {id: "desc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }
    } as $result
  
    var $visible_items {
      value = $result.items
    }
  
    conditional {
      if ($perfil.Cargo == "Vendedor") {
        var.update $visible_items {
          value = $result.items|filter:$$.vendedor_id == $auth.id
        }
      }
    
      else {
        conditional {
          if ($parsed_vendedor_id > 0) {
            var.update $visible_items {
              value = $result.items|filter:$$.vendedor_id == $parsed_vendedor_id
            }
          }
        }
      }
    }
  
    // Carregar apenas registros de referencia necessarios para a pagina atual
    var $page_client_ids {
      value = ($visible_items|map:$$.cliente_id)|unique
    }
  
    var $page_vendedor_ids {
      value = ($visible_items|map:$$.vendedor_id)|unique
    }
  
    var $page_status_ids {
      value = ($visible_items|map:$$.status_id)|unique
    }
  
    var $page_forma_ids {
      value = ($visible_items|map:$$.forma_pagamento_id)|unique
    }
  
    db.query cliente {
      where = $page_client_ids contains $db.cliente.id
      return = {type: "list"}
    } as $page_clientes
  
    db.query user {
      where = $page_vendedor_ids contains $db.user.id
      return = {type: "list"}
    } as $page_vendedores
  
    db.query status_venda {
      where = $page_status_ids contains $db.status_venda.id
      return = {type: "list"}
    } as $todos_status
  
    db.query forma_pagamento {
      where = $page_forma_ids contains $db.forma_pagamento.id
      return = {type: "list"}
    } as $todas_formas
  
    db.query asaas_cobranca {
      return = {type: "list"}
    } as $cobrancas_asaas
  
    // Mapear cada venda com dados resumidos de cliente, vendedor, forma e status
    var $sanitized_items {
      value = ```
        $visible_items|map:{
                id: $$.id,
                cliente: {
                  id: $$.cliente_id,
                  CNome: (($page_clientes|find:$item.id == $$.cliente_id).CNome ?? "")
                },
                vendedor: {
                  id: $$.vendedor_id,
                  UNome: (($page_vendedores|find:$item.id == $$.vendedor_id).UNome ?? "")
                },
                forma_pagamento: {
                  id: $$.forma_pagamento_id,
                  Metodo: (($todas_formas|find:$item.id == $$.forma_pagamento_id).Metodo ?? "")
                },
                status: {
                  id: $$.status_id,
                  Descricao_venda: (($todos_status|find:$item.id == $$.status_id).Descricao_venda ?? "")
                },
                Valor_bruto: $$.Valor_bruto,
                Desconto: ($$.Desconto ?? 0),
                Valor_final: $$.Valor_final,
                data_venda: $$.data_venda,
                asaas_cobranca: {
                  invoice_url: (($cobrancas_asaas|find:$item.venda_id == $$.id).invoice_url ?? ""),
                  status: (($cobrancas_asaas|find:$item.venda_id == $$.id).status ?? ""),
                  due_date: (($cobrancas_asaas|find:$item.venda_id == $$.id).due_date ?? "")
                }
              }
        ```
    }
  }

  response = {
    items     : $sanitized_items
    pagination: ```
      {
        page: $result.curPage,
        per_page: $result.perPage,
        total: $result.total ?? ($result.items|count),
        total_pages: $result.pageTotal ?? 1
      }
      ```
  }

  test "nenhum filtro de data" {
    expect.to_be_defined ($response.pagination)
  }

  test "data_inicio formato YYYY-MM-DD" {
    input = {data_inicio: "2025-01-01"}
  
    expect.to_be_defined ($response.pagination)
  }

  test "data_fim formato YYYY-MM-DD" {
    input = {data_fim: "2025-01-31"}
  
    expect.to_be_defined ($response.pagination)
  }

  test "ambos filtros formato YYYY-MM-DD" {
    input = {data_inicio: "2025-01-01", data_fim: "2025-01-31"}
  
    expect.to_be_defined ($response.pagination)
  }

  guid = "mlx3IuCAqht3sXtC-476KgiYDnI"
}