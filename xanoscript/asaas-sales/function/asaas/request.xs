// A chave e o ambiente sao configurados somente no Xano. Sem fallback para producao.
function "asaas/request" {
  input {
    text method
    text path
    json? body?
  }
  stack {
    precondition ($env.ASAAS_ENV == "sandbox" || $env.ASAAS_ENV == "production") {

    error_type = "badrequest"

    error = "Configure ASAAS_ENV no Xano antes de usar a integracao"
    }
    precondition ($env.ASAAS != null && $env.ASAAS != "") {

    error_type = "badrequest"

    error = "Credencial ASAAS nao configurada no Xano"
    }
    var $base { value = "https://api-sandbox.asaas.com/v3" }
    conditional {
      if ($env.ASAAS_ENV == "production") {
        var.update $base { value = "https://api.asaas.com/v3" }
      }
    }
    api.request {
      url = $base ~ $input.path
      method = $input.method
      params = $input.body ?? {}
      timeout = 20
      follow_location = false
      headers = []|push:("access_token: " ~ $env.ASAAS)|push:"Content-Type: application/json"|push:"User-Agent: AutoGestao/1.0"
    } as $http
    var $http_status { value = ($http.response.status ?? $http.status ?? 0)|to_int }
    precondition ($http_status >= 200 && $http_status < 300) {

    error_type = "badrequest"

    error = "ASAAS indisponivel ou recusou a operacao; a tentativa foi preservada para recuperacao"
    }
  }
  response = ($http.response.result ?? $http.body)

  guid = "SK04wPcOrLRutZPTGGsXJ64GuUg"
}
