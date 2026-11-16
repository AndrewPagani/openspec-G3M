// Completa somente os status exigidos pela spec; preserva todos os IDs existentes.
function "asaas/prepare_catalog" {
  input {
  }

  stack {
    precondition ($env.ASAAS_ENV == "sandbox") {
      error_type = "badrequest"
      error = "Preparacao exige ambiente Sandbox explicito"
    }
  
    db.transaction {
      stack {
        foreach (["Reservado", "Paga", "Expirada"]) {
          each as $name {
            db.query status_venda {
              where = $db.status_venda.Descricao_venda == $name
              return = {type: "single"}
            } as $existing
          
            conditional {
              if ($existing == null) {
                db.add status_venda {
                  data = {Descricao_venda: $name}
                } as $created
              }
            }
          }
        }
      }
    }
  
    db.query status_venda {
      return = {type: "list"}
    } as $statuses
  }

  response = $statuses|map:{id: $$.id, name: $$.Descricao_venda}
  guid = "RN7izCIbjPgfo9egUZqYGc9u7-M"
}