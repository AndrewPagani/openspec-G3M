// Atualizacao de informacoes cadastrais da peca
// Atualiza nome, preco ou area da peca sem permitir alteracao direta de quantidade em estoque
// Identificador da peca e atributos permitidos
query "pecas/{id}" verb=PATCH {
  api_group = "cadastros"
  auth = "user"

  input {
    int id {
      table = "peca"
    }
  
    text PCNome? filters=trim
    decimal PCvalor? filters=min:0
    int area_id?
    text imagem_url? filters=trim
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
  
    // Inicializar mapa de atualizacoes
    var $updates {
      value = {}
    }
  
    conditional {
      if ($input.PCNome != null && ($input.PCNome|strlen) > 0) {
        var.update $updates {
          value = $updates|set:"PCNome":$input.PCNome
        }
      }
    }
  
    conditional {
      if ($input.PCvalor != null) {
        var.update $updates {
          value = $updates|set:"PCvalor":$input.PCvalor
        }
      }
    }
  
    conditional {
      if ($input.area_id != null) {
        db.get veiculo_area {
          field_name = "id"
          field_value = $input.area_id
        } as $area
      
        precondition ($area != null) {
          error_type = "badrequest"
          error = "Area informada nao existe"
        }
      
        var.update $updates {
          value = $updates|set:"area_id":$input.area_id
        }
      }
    }
  
    // Atualizar imagem_url quando informada
    conditional {
      if ($input.imagem_url != null) {
        var.update $updates {
          value = $updates
            |set:"imagem_url":$input.imagem_url
        }
      }
    }
  
    // Aplicar patch se houver campos alterados
    conditional {
      if (($updates|is_empty) == false) {
        db.patch peca {
          field_name = "id"
          field_value = $input.id
          data = $updates
        } as $peca_atualizada
      }
    
      else {
        var $peca_atualizada {
          value = $peca
        }
      }
    }
  
    // Buscar descricao da area vinculada
    var $area_secao {
      value = null
    }
  
    conditional {
      if ($peca_atualizada.area_id != null) {
        db.get veiculo_area {
          field_name = "id"
          field_value = $peca_atualizada.area_id
        } as $area_final
      
        conditional {
          if ($area_final != null) {
            var.update $area_secao {
              value = $area_final.Secao
            }
          }
        }
      }
    }
  }

  response = {
    id        : $peca_atualizada.id
    PCNome    : $peca_atualizada.PCNome
    PCvalor   : $peca_atualizada.PCvalor
    qtd_disp  : ($peca_atualizada.qtd_disp ?? 0)
    area_id   : $peca_atualizada.area_id
    area_secao: $area_secao
    imagem_url: $peca_atualizada.imagem_url
  }

  guid = "OkGnAOoG1p5-c6LtpssI8i0iXLk"
}