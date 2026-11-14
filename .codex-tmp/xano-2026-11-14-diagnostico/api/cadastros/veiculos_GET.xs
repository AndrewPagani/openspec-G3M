// Listagem paginada de veiculos com filtros avancados
// Lista veiculos com filtros por busca textual, marca, modelo, status e disponibilidade
// Parametros de paginacao e filtros de veiculo
query veiculos verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
    int page?=1 filters=min:1
    int per_page?=20 filters=min:1|max:100
    text busca? filters=trim
    text marca? filters=trim
    text modelo? filters=trim
    int status_id?
    bool somente_disponiveis?
  }

  stack {
    // Definir status para filtro se solicitado
    var $filtro_status {
      value = $input.status_id
    }
  
    // Buscar id do status Disponivel se somente_disponiveis for verdadeiro
    conditional {
      if ($input.somente_disponiveis && $filtro_status == null) {
        db.query status_veiculo {
          where = $db.status_veiculo.Descricao == "Disponível" || $db.status_veiculo.Descricao == "Disponivel"
          return = {type: "single"}
        } as $st_disp
      
        conditional {
          if ($st_disp != null) {
            var.update $filtro_status {
              value = $st_disp.id
            }
          }
        }
      }
    }
  
    // Verificar se termo de busca textual foi informado
    var $termo_busca {
      value = ($input.busca != null && ($input.busca|strlen) > 0) ? $input.busca : null
    }
  
    // Consultar veiculos aplicando filtros dinamicos e join com status_veiculo
    conditional {
      if ($termo_busca != null) {
        db.query veiculo {
          join = {
            status_veiculo: {
              table: "status_veiculo"
              type : "left"
              where: $db.veiculo.status_id == $db.status_veiculo.id
            }
          }
        
          where = $db.veiculo.status_id ==? $filtro_status && $db.veiculo.Marca ==? $input.marca && $db.veiculo.Modelo ==? $input.modelo && ($db.veiculo.Marca includes $termo_busca || $db.veiculo.Modelo includes $termo_busca || $db.veiculo.Placa includes $termo_busca || $db.veiculo.Chassi includes $termo_busca)
          sort = {id: "desc"}
          eval = {status_descricao: $db.status_veiculo.Descricao}
          return = {
            type  : "list"
            paging: {
              page    : $input.page
              per_page: $input.per_page
              totals  : true
            }
          }
        } as $result
      }
    
      else {
        db.query veiculo {
          join = {
            status_veiculo: {
              table: "status_veiculo"
              type : "left"
              where: $db.veiculo.status_id == $db.status_veiculo.id
            }
          }
        
          where = $db.veiculo.status_id ==? $filtro_status && $db.veiculo.Marca ==? $input.marca && $db.veiculo.Modelo ==? $input.modelo
          sort = {id: "desc"}
          eval = {status_descricao: $db.status_veiculo.Descricao}
          return = {
            type  : "list"
            paging: {
              page    : $input.page
              per_page: $input.per_page
              totals  : true
            }
          }
        } as $result
      }
    }
  }

  response = {
    items     : $result.items
    pagination: ```
      {
        page       : $result.curPage
        per_page   : $result.perPage
        total      : ($result.total ?? ($result.items|count))
        total_pages: ($result.pageTotal ?? 1)
      }
      ```
  }

  guid = "0nRNiFt61PHtpypl-tP3dj1pN1s"
}