// Detalhes de uma peca especifica
// Retorna os detalhes de uma peca de estoque e a respectiva secao/area
// Identificador da peca
query "pecas/{id}" verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "peca"
    }
  }

  stack {
    // Buscar peca no banco
    db.get peca {
      field_name = "id"
      field_value = $input.id
    } as $peca
  
    precondition ($peca != null) {
      error_type = "notfound"
      error = "Peca nao encontrada"
    }
  
    // Buscar area vinculada se existir
    var $area_secao {
      value = null
    }
  
    conditional {
      if ($peca.area_id != null) {
        db.get veiculo_area {
          field_name = "id"
          field_value = $peca.area_id
        } as $area
      
        conditional {
          if ($area != null) {
            var.update $area_secao {
              value = $area.Secao
            }
          }
        }
      }
    }
  }

  response = {
    id        : $peca.id
    PCNome    : $peca.PCNome
    PCvalor   : $peca.PCvalor
    qtd_disp  : ($peca.qtd_disp ?? 0)
    area_id   : $peca.area_id
    area_secao: $area_secao
  }

  guid = "CzDoHy16z9IGAk95r173dZhqVLo"
}