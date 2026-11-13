// Exclusao de cliente com desvinculacao segura do historico de vendas
query "clientes/{id}" verb=DELETE {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "cliente"
    }
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $usuario

    db.get perfil {
      field_name = "id"
      field_value = $usuario.perfil_id
    } as $perfil

    precondition ($perfil != null && ($perfil.Cargo == "Gerente" || $perfil.Cargo == "Administrador")) {
      error_type = "accessdenied"
      error = "Somente gerente ou administrador pode excluir clientes"
    }

    db.get cliente {
      field_name = "id"
      field_value = $input.id
    } as $cliente

    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Cliente nao encontrado"
    }

    db.query venda {
      where = $db.venda.cliente_id == $input.id
      return = {type: "list"}
    } as $vendas_cliente

    db.transaction {
      stack {
        foreach ($vendas_cliente) {
          each as $item_venda {
            db.patch venda {
              field_name = "id"
              field_value = $item_venda.id
              data = {cliente_id: null}
            } as $venda_desvinculada
          }
        }

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
