// Consulta o cronograma e as baixas manuais locais da venda
// Identificador da venda
query "vendas/{id}/pagamento" verb=GET {
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

    // Validar permissao de perfil
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


    precondition ($perfil.Cargo == "Vendedor" || $perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador") {

    error_type = "accessdenied"
    error = "Perfil sem permissao para consultar pagamento"
    }
    // Buscar descricao do status
    db.get status_venda {

    field_name = "id"

    field_value = $venda.status_id
    } as $status_venda

    db.query venda_parcela {

    where = $db.venda_parcela.venda_id == $input.id
      sort = {numero_parcela: "asc"}

    return = {type: "list"}
    } as $parcelas_db

    db.query forma_pagamento {

    return = {type: "list"}
    } as $formas_pagamento

    db.query asaas_cobranca {

    where = $db.asaas_cobranca.venda_id == $input.id

    return = {type: "single"}
    } as $cobranca_asaas

    var $parcelas_recebidas {
      value = $parcelas_db|filter:$$.status == "RECEBIDA"
    }

    var $valor_recebido {
      value = (($parcelas_recebidas|map:$$.valor)|sum) ?? 0
    }

    var $parcelas_pagas {
      value = $parcelas_recebidas|count
    }

    var $parcelas_pendentes {
      value = ($parcelas_db|filter:$$.status == "PENDENTE")|count
    }

    conditional {
      if ($venda.payment_flow == "ASAAS") {
        var.update $valor_recebido { value = $cobranca_asaas.valor_recebido ?? 0 }
      }
    }

    var $parcelas_sanitizadas {
      value = ```
        $parcelas_db|map:{
                id: $$.id,
                status: $$.status,
                valor: $$.valor,
                numero_parcela: $$.numero_parcela,
                total_parcelas: $$.total_parcelas,
                vencimento: $$.vencimento,
                forma_recebida: (($formas_pagamento|find:$item.id == $$.forma_recebida_id).Metodo ?? null),
                recebido_em: $$.recebido_em,
                recebido_por: $$.recebido_por,
                cancelada_em: $$.cancelada_em
              }
        ```
    }
  }

  response = {
    payment_flow      : ($venda.payment_flow ?? "LEGADO")
    venda_id          : $venda.id
    status_venda      : ($status_venda.Descricao_venda ?? "")
    total_venda       : $venda.Valor_final
    valor_recebido    : $valor_recebido
    parcelas_pagas    : $parcelas_pagas
    parcelas_pendentes: $parcelas_pendentes
    parcelas          : $parcelas_sanitizadas
    asaas_cobranca    : ```
      {
        invoice_url: ($cobranca_asaas.invoice_url ?? ""),
        status: ($cobranca_asaas.status ?? ""),
        due_date: ($cobranca_asaas.due_date ?? "")
      }
      ```
  }

  guid = "qBBU4QSyG1Dna4ujKi8Cl8f7nog"
}
