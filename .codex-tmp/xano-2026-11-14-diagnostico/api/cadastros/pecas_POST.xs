// Cadastro de nova peca no estoque
// Cadastra uma nova peca no catalogo com preco, quantidade inicial e area opcional
// Dados cadastrais da peca
query pecas verb=POST {
  api_group = "cadastros"
  auth = "user"

  input {
    text PCNome filters=trim
    decimal PCvalor filters=min:0
    int qtd_disp? filters=min:0
    int area_id?
    text imagem_url? filters=trim
  }

  stack {
    // Validar nome da peca
    precondition (($input.PCNome|strlen) > 0) {
      error_type = "inputerror"
      error = "Nome da peca e obrigatorio"
    }
  
    // Validar area se fornecida
    var $area_secao {
      value = null
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
      
        var.update $area_secao {
          value = $area.Secao
        }
      }
    }
  
    // Inserir peca no banco
    db.add peca {
      data = {
        PCNome    : $input.PCNome
        PCvalor   : $input.PCvalor
        qtd_disp  : ($input.qtd_disp ?? 0)
        area_id   : $input.area_id
        imagem_url: $input.imagem_url
      }
    } as $nova_peca
  }

  response = {
    id        : $nova_peca.id
    PCNome    : $nova_peca.PCNome
    PCvalor   : $nova_peca.PCvalor
    qtd_disp  : $nova_peca.qtd_disp
    area_id   : $nova_peca.area_id
    area_secao: $area_secao
    imagem_url: $nova_peca.imagem_url
  }

  guid = "lFYjHUzfPsLqT79cAWoGUGS-B40"
}