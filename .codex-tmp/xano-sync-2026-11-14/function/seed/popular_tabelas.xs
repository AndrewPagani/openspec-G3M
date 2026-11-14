// Funcao responsavel por popular todas as 14 tabelas do sistema com 50 registros cada respeitando chaves estrangeiras e restricoes unicas
// Popula 50 registros em cada uma das 14 tabelas do workspace mantendo a integridade referencial
function "seed/popular_tabelas" {
  input {
    // Prefixo para geracao de dados unicos permitindo execucoes repetidas sem conflito de indices
    text prefix?=s1
  
    // Se verdadeiro, trunca todas as tabelas em ordem reversa antes de inserir os novos dados
    bool limpar_tabelas_antes?
  }

  stack {
    // Limpa registros anteriores se solicitado pelo usuario
    conditional {
      if ($input.limpar_tabelas_antes) {
        db.truncate "" {
          reset = true
        }
      
        db.truncate pagamento {
          reset = true
        }
      
        db.truncate venda_parcela {
          reset = true
        }
      
        db.truncate venda_item {
          reset = true
        }
      
        db.truncate venda {
          reset = true
        }
      
        db.truncate peca {
          reset = true
        }
      
        db.truncate veiculo {
          reset = true
        }
      
        db.truncate user {
          reset = true
        }
      
        db.truncate cliente {
          reset = true
        }
      
        db.truncate veiculo_area {
          reset = true
        }
      
        db.truncate status_venda {
          reset = true
        }
      
        db.truncate status_veiculo {
          reset = true
        }
      
        db.truncate forma_pagamento {
          reset = true
        }
      
        db.truncate perfil {
          reset = true
        }
      }
    }
  
    // Define prefixo seguro para nomes e identificadores
    var $pfx {
      value = $input.prefix ?? "s1"
    }
  
    // Prefixo normalizado de duas letras em maiusculo para placas e chassis
    var $pfx_plate {
      value = ($pfx ~ "XX")|substr:0:2|to_upper
    }
  
    // Executa o laco de 50 iteracoes para gerar 50 registros em cada uma das 14 tabelas
    for (50) {
      each as $i {
        // Indice de 1 a 50
        var $idx {
          value = $i + 1
        }
      
        // Indice formatado em 2 digitos
        var $str_idx {
          value = ($idx < 10) ? ("0" ~ ($idx|to_text)) : ($idx|to_text)
        }
      
        // Indice formatado em 3 digitos
        var $str_3 {
          value = ($idx < 10) ? ("00" ~ ($idx|to_text)) : (($idx < 100) ? ("0" ~ ($idx|to_text)) : ($idx|to_text))
        }
      
        // 1. Tabela perfil (Nivel 0)
        db.add perfil {
          data = {Cargo: "Cargo " ~ $pfx ~ " " ~ $str_3}
        } as $new_perfil
      
        // 2. Tabela forma_pagamento (Nivel 0)
        db.add forma_pagamento {
          data = {Metodo: "Metodo " ~ $pfx ~ " " ~ $str_3}
        } as $new_fp
      
        // 3. Tabela status_veiculo (Nivel 0)
        db.add status_veiculo {
          data = {Descricao: "Status Veiculo " ~ $pfx ~ " " ~ $str_3}
        } as $new_sv
      
        // 4. Tabela status_venda (Nivel 0)
        db.add status_venda {
          data = {Descricao_venda: "Status Venda " ~ $pfx ~ " " ~ $str_3}
        } as $new_svenda
      
        // 5. Tabela veiculo_area (Nivel 0)
        db.add veiculo_area {
          data = {Secao: "Secao " ~ $pfx ~ " " ~ $str_3}
        } as $new_va
      
        // 6. Tabela cliente (Nivel 0)
        db.add cliente {
          data = {
            CNome            : "Cliente " ~ $pfx ~ " " ~ $str_3
            CPF              : "111" ~ $str_idx ~ $str_3 ~ $str_idx
            Telefone         : "(11) 980" ~ $str_idx ~ "-" ~ $str_3 ~ "0"
            Email            : "cliente_" ~ $pfx ~ "_" ~ $str_3 ~ "@seedexemplo.com"
            asaas_customer_id: "cus_" ~ $pfx ~ "_" ~ $str_3
            created_at       : now
          }
        } as $new_cli
      
        // 7. Tabela user (Nivel 1 - depende de perfil)
        db.add user {
          data = {
            UNome     : "Usuario " ~ $pfx ~ " " ~ $str_3
            Email     : "usuario_" ~ $pfx ~ "_" ~ $str_3 ~ "@seedconcessionaria.com"
            perfil_id : $new_perfil.id
            Senha     : "SenhaSegura123!"
            created_at: now
          }
        } as $new_user
      
        // 8. Tabela veiculo (Nivel 1 - depende de status_veiculo)
        db.add veiculo {
          data = {
            Marca        : "Marca " ~ $str_3
            Modelo       : "Modelo " ~ $str_3
            Cor          : "Cor " ~ $str_3
            Ano          : 2020 + ($i % 5)
            Placa        : "S" ~ $pfx_plate ~ $str_idx ~ $str_idx
            Chassi       : "9BW" ~ $pfx_plate ~ "ZZZ377VT" ~ $str_idx ~ $str_idx
            Quilometragem: (($idx * 1500)|to_decimal)
            Preco        : (40000 + ($idx * 1000))|to_decimal
            status_id    : $new_sv.id
            created_at   : now
            imagem_url   : "https://images.unsplash.com/photo-vehicle-" ~ $str_3 ~ ".jpg"
          }
        } as $new_veic
      
        // 9. Tabela peca (Nivel 1 - depende de veiculo_area)
        db.add peca {
          data = {
            PCNome  : "Peca " ~ $str_3
            PCvalor : (50 + ($idx * 20))|to_decimal
            qtd_disp: 10 + $idx
            area_id : $new_va.id
          }
        } as $new_peca
      
        // Prepara valores monetarios calculados da venda
        var $bruto {
          value = (50000 + ($idx * 1000))|to_decimal
        }
      
        // Desconto da venda
        var $desc {
          value = (500 + ($idx * 10))|to_decimal
        }
      
        // Valor liquido final da venda
        var $final {
          value = $bruto - $desc
        }
      
        // 10. Tabela venda (Nivel 2 - depende de cliente, user, forma_pagamento, status_venda)
        db.add venda {
          data = {
            cliente_id               : $new_cli.id
            vendedor_id              : $new_user.id
            forma_pagamento_id       : $new_fp.id
            status_id                : $new_svenda.id
            Valor_bruto              : $bruto
            Desconto                 : $desc
            Valor_final              : $final
            data_venda               : now
            asaas_payment_link_id    : "lnk_" ~ $pfx ~ "_" ~ $str_3
            asaas_payment_link_url   : "https://sandbox.asaas.com/link/" ~ $pfx ~ "/" ~ $str_3
            payment_link_expires_at  : now|add_secs_to_timestamp:2592000
            payment_installment_limit: 12
          }
        } as $new_venda
      
        // 11. Tabela venda_item (Nivel 3 - depende de venda, veiculo, peca)
        db.add venda_item {
          data = {
            venda_id  : $new_venda.id
            veiculo_id: $new_veic.id
            peca_id   : $new_peca.id
            qtd       : 1
            preco_unit: $bruto
          }
        } as $new_item
      
        // 12. Tabela venda_parcela (Nivel 3 - depende de venda, forma_pagamento, user)
        db.add venda_parcela {
          data = {
            venda_id         : $new_venda.id
            numero_parcela   : 1
            total_parcelas   : 1
            valor            : $final
            vencimento       : now|add_secs_to_timestamp:2592000
            status           : "PENDENTE"
            forma_recebida_id: $new_fp.id
            updated_at       : now
          }
        } as $new_parcela
      
        // 13. Tabela pagamento (Nivel 3 - depende de venda)
        db.add pagamento {
          data = {
            venda_id            : $new_venda.id
            asaas_payment_id    : "pay_" ~ $pfx ~ "_" ~ $str_3
            asaas_customer_id   : "cus_" ~ $pfx ~ "_" ~ $str_3
            asaas_installment_id: "inst_" ~ $pfx ~ "_" ~ $str_3
            status_asaas        : "PENDING"
            billing_type        : "PIX"
            valor               : $final
            valor_liquido       : ($final - 10.00)|to_decimal
            taxa                : 10|to_decimal
            numero_parcela      : 1
            total_parcelas      : 1
            vencimento          : now|add_secs_to_timestamp:2592000
            updated_at          : now
          }
        } as $new_pag
      
        // 14. Tabela pagamento_evento (Nivel 4 - evento vinculado ao pagamento)
        db.add "" {
          data = {
            asaas_event_id      : "evt_" ~ $pfx ~ "_" ~ $str_3
            asaas_payment_id    : $new_pag.asaas_payment_id
            evento              : "PAYMENT_CREATED"
            recebido_em         : now
            processado_em       : now
            status_processamento: "PROCESSADO"
          }
        } as $new_evento
      }
    }
  }

  response = {
    sucesso                  : true
    tabelas_populadas        : 14
    registros_por_tabela     : 50
    total_registros_inseridos: 700
    prefixo_utilizado        : $pfx
  }

  guid = "BeyAAz1YMUZA5QGsRYRzyef2owY"
}