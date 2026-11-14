// Auditoria completa da tabela venda_parcela para diagnostico de indicadores financeiros
query auditoria_parcelas verb=GET {
  api_group = "gerenciamento"
  auth = "user"

  input {
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
  
    precondition ($perfil != null && $perfil.Cargo == "Gerente") {
      error_type = "accessdenied"
      error = "Apenas Gerente pode acessar o diagnostico de auditoria"
    }
  
    // 2. Consultar todas as parcelas do workspace
    db.query venda_parcela {
      return = {type: "list"}
    } as $todas_as_parcelas_banco
  
    var $total_parcelas {
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
          RECEBIDA: 0
          PENDENTE: 0
          CANCELADA: 0
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
      
        var $venda_match {
          value = null
        }
      
        conditional {
          if ($p.venda_id != null) {
            var.update $com_venda_id {
              value = $com_venda_id + 1
            }
          
            db.get venda {
              field_name = "id"
              field_value = $p.venda_id
            } as $db_venda_match
          
            var.update $venda_match {
              value = $db_venda_match
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
      
        var $venda_status_desc {
          value = ""
        }
      
        conditional {
          if ($venda_match != null && $venda_match.status_id != null) {
            db.get status_venda {
              field_name = "id"
              field_value = $venda_match.status_id
            } as $db_st_venda
          
            conditional {
              if ($db_st_venda != null && $db_st_venda.Descricao_venda != null) {
                var.update $venda_status_desc {
                  value = (($db_st_venda.Descricao_venda|trim)|to_lower)
                }
              }
            }
          }
        }
      
        var $venda_is_paga_ou_concluida {
          value = ($venda_status_desc == "paga" || $venda_status_desc == "concluída" || $venda_status_desc == "concluida")
        }
      
        // Identifica se e uma parcela recebida qualificada para exibicao de exemplos (Opcao 1)
        var $is_recebida {
          value = false
        }
      
        conditional {
          if ($st_norm != "CANCELADA") {
            conditional {
              if ($st_norm == "RECEBIDA" || ($p.recebido_em != null && $p.forma_recebida_id != null && $p.recebido_por != null) || $venda_is_paga_ou_concluida) {
                var.update $is_recebida {
                  value = true
                }
              }
            }
          }
        }
      
        conditional {
          if ($is_recebida && (($exemplos_parcelas_recebidas|count) < 10)) {
            array.push $exemplos_parcelas_recebidas {
              value = {
                id                : $p.id
                venda_id          : $p.venda_id
                valor             : $p.valor
                status_original   : $st_raw
                status_normalizado: $st_norm
                recebido_em       : ($p.recebido_em ?? $venda_match.data_venda)
                forma_recebida_id : ($p.forma_recebida_id ?? $venda_match.forma_pagamento_id)
                recebido_por      : $p.recebido_por
                data_venda        : ($venda_match.data_venda ?? null)
                Valor_final       : ($venda_match.Valor_final ?? null)
              }
            }
          }
        }
      }
    }
  }

  response = {
    total_parcelas             : $total_parcelas
    total_por_status           : $totais_por_status
    valores_distintos_status   : $status_distintos_raw
    com_valor_maior_zero       : $com_valor_maior_zero
    com_recebido_em            : $com_recebido_em
    com_forma_recebida_id      : $com_forma_recebida_id
    com_recebido_por           : $com_recebido_por
    com_venda_id               : $com_venda_id
    com_venda_existente        : $com_venda_existente
    exemplos_parcelas_recebidas: $exemplos_parcelas_recebidas
    mensagem                   : (($totais_por_status.RECEBIDA > 0 || ($exemplos_parcelas_recebidas|count) > 0) ? "Parcelas recebidas identificadas." : "Nenhuma parcela qualificada foi encontrada na tabela venda_parcela.")
  }

  guid = "KH3MD7nulh5yx2XZtC31G0Y9B9I"
}