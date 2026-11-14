// Exclusao de cliente com desvinculacao segura do historico de vendas
query "clientes/{id}" verb=DELETE {
  api_group = "cadastros"
  auth = "user"

  input {
    // Identificador do cliente a ser excluido
    int id {
      table = "cliente"
    }
  }

  stack {
    // Carrega o usuario autenticado
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $usuario
  
    db.get perfil {
      field_name = "id"
      field_value = $usuario.perfil_id
    } as $perfil
  
    // Valida permissao de acesso: apenas Gerente ou Administrador
    precondition ($perfil != null && ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador")) {
      error_type = "accessdenied"
      error = "Somente gerente ou administrador pode excluir clientes"
    }
  
    // Busca o cliente pelo identificador informado
    db.get cliente {
      field_name = "id"
      field_value = $input.id
    } as $cliente
  
    // Valida se o cliente existe
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente nao encontrado"
    }
  
    // Busca todas as vendas vinculadas ao cliente para desvinculacao segura
    db.query venda {
      where = $db.venda.cliente_id == $input.id
      return = {type: "list"}
    } as $vendas_cliente
  
    // Executa atualizacoes e exclusao em transacao atomica
    db.transaction {
      stack {
        // Itera sobre as vendas do cliente desvinculando o cliente_id
        foreach ($vendas_cliente) {
          each as $item_venda {
            // Define cliente_id como nulo mantendo historico da venda
            db.patch venda {
              field_name = "id"
              field_value = $item_venda.id
              data = {cliente_id: null}
            } as $venda_desvinculada
          }
        }
      
        // Exclui o cadastro do cliente
        db.del cliente {
          field_name = "id"
          field_value = $input.id
        }
      }
    }
  }

  response = {
    id     : $input.id
    deleted: true
    message: "Cliente excluido com sucesso"
  }

  guid = "eupuTjMkIPKHHzzqWkJj-8qPPao"
}