// Diagnostico somente leitura: nunca retorna chaves, tokens ou dados de clientes.
function "asaas/check_setup" {
  input {
  }

  stack {
    var $sandbox {
      value = $env.ASAAS_ENV == "sandbox"
    }
  
    var $has_key {
      value = $env.ASAAS != null && $env.ASAAS != ""
    }
  
    var $has_token {
      value = $env.ASAAS_WEBHOOK_TOKEN != null && ($env.ASAAS_WEBHOOK_TOKEN|strlen) >= 32 && ($env.ASAAS_WEBHOOK_TOKEN|strlen) <= 255
    }
  
    var $asaas_status {
      value = 0
    }
  
    var $webhook_auth_status {
      value = 0
    }
  
    var $hooks {
      value = []
    }
  
    var $request_checked {
      value = false
    }
  
    var $probe_reached_reconcile {
      value = false
    }
  
    db.query perfil {
      return = {type: "list"}
    } as $profiles
  
    db.query status_venda {
      return = {type: "list"}
    } as $sale_statuses
  
    db.query status_veiculo {
      return = {type: "list"}
    } as $vehicle_statuses
  
    db.query forma_pagamento {
      return = {type: "list"}
    } as $payment_methods
  
    conditional {
      if ($sandbox && $has_key) {
        api.request {
          url = "https://api-sandbox.asaas.com/v3/webhooks"
          method = "GET"
          params = {limit: 100}
          headers = []
            |push:"access_token: " ~ $env.ASAAS
            |push:"User-Agent: AutoGestao/1.0"
          timeout = 15
          follow_location = false
        } as $upstream
      
        var.update $asaas_status {
          value = ($upstream.response.status ?? $upstream.status ?? 0)|to_int
        }
      
        conditional {
          if ($asaas_status == 200) {
            function.run "asaas/request" {
              input = {
                method: "GET"
                path  : "/webhooks"
                body  : {limit: 100}
              }
            } as $wrapped
          
            var.update $request_checked {
              value = $wrapped.data != null
            }
          
            var $body {
              value = $upstream.response.result ?? $upstream.body
            }
          
            var.update $hooks {
              value = $body.data|map:{matches_url: $$.url == "https://x8ki-letl-twmt.n7.xano.io/api:asaas_webhooks/webhooks/asaas/pagamentos", enabled: $$.enabled, interrupted: $$.interrupted, send_type: $$.sendType, events: $$.events}
            }
          }
        }
      }
    }
  
    conditional {
      if ($has_token) {
        api.request {
          url = "https://x8ki-letl-twmt.n7.xano.io/api:asaas_webhooks/webhooks/asaas/pagamentos"
          method = "POST"
          params = {
            id     : "setup-auth-probe-only"
            event  : "PAYMENT_RECEIVED"
            payment: {id: "setup-auth-probe-only"}
          }
        
          headers = []
            |push:"asaas-access-token: " ~ $env.ASAAS_WEBHOOK_TOKEN
            |push:"Content-Type: application/json"
            |push:"X-Branch: v1"
          timeout = 15
          follow_location = false
        } as $probe
      
        var.update $webhook_auth_status {
          value = ($probe.response.status ?? $probe.status ?? 0)|to_int
        }
      
        var $probe_body {
          value = $probe.response.result ?? $probe.body
        }
      
        var.update $probe_reached_reconcile {
          value = $probe_body.message == "Cobranca ainda nao vinculada; tentar evento novamente"
        }
      }
    }
  }

  response = {
    sandbox                              : $sandbox
    api_key_configured                   : $has_key
    webhook_token_valid_length           : $has_token
    asaas_http_status                    : $asaas_status
    authenticated_probe_http_status      : $webhook_auth_status
    webhooks                             : $hooks
    request_wrapper_checked              : $request_checked
    authenticated_probe_reached_reconcile: $probe_reached_reconcile
    profiles                             : $profiles|map:{id: $$.id, name: $$.Cargo}
    sale_statuses                        : $sale_statuses|map:{id: $$.id, name: $$.Descricao_venda}
    vehicle_statuses                     : $vehicle_statuses|map:{id: $$.id, name: $$.Descricao}
    payment_methods                      : $payment_methods|map:{id: $$.id, name: $$.Metodo}
  }

  guid = "dpeVAFhPI7BDZ8CQuXUko73ILhk"
}