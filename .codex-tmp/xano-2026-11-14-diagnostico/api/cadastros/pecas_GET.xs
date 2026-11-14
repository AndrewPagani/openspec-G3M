// Listagem paginada de pecas com filtros avancados
// Lista pecas com filtros por busca textual, area e disponibilidade
// Parametros de paginacao e filtros de peca
query pecas verb=GET {
  api_group = "cadastros"
  auth = "user"

  input {
    int page?=1 filters=min:1
    int per_page?=20 filters=min:1|max:100
    text busca? filters=trim
    int area_id?
    bool somente_disponiveis?
  }

  stack {
    // Verificar se termo de busca textual foi informado
    var $termo_busca {
      value = ($input.busca != null && ($input.busca|strlen) > 0) ? $input.busca : null
    }
  
    // Consultar pecas aplicando filtros dinamicos e join com veiculo_area
    conditional {
      if ($input.somente_disponiveis) {
        conditional {
          if ($termo_busca != null) {
            db.query peca {
              join = {
                veiculo_area: {
                  table: "veiculo_area"
                  type : "left"
                  where: $db.peca.area_id == $db.veiculo_area.id
                }
              }
            
              where = $db.peca.qtd_disp > 0 && $db.peca.area_id ==? $input.area_id && $db.peca.PCNome includes $termo_busca
              sort = {id: "desc"}
              eval = {area_secao: $db.veiculo_area.Secao}
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
            db.query peca {
              join = {
                veiculo_area: {
                  table: "veiculo_area"
                  type : "left"
                  where: $db.peca.area_id == $db.veiculo_area.id
                }
              }
            
              where = $db.peca.qtd_disp > 0 && $db.peca.area_id ==? $input.area_id
              sort = {id: "desc"}
              eval = {area_secao: $db.veiculo_area.Secao}
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
    
      else {
        conditional {
          if ($termo_busca != null) {
            db.query peca {
              join = {
                veiculo_area: {
                  table: "veiculo_area"
                  type : "left"
                  where: $db.peca.area_id == $db.veiculo_area.id
                }
              }
            
              where = $db.peca.area_id ==? $input.area_id && $db.peca.PCNome includes $termo_busca
              sort = {id: "desc"}
              eval = {area_secao: $db.veiculo_area.Secao}
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
            db.query peca {
              join = {
                veiculo_area: {
                  table: "veiculo_area"
                  type : "left"
                  where: $db.peca.area_id == $db.veiculo_area.id
                }
              }
            
              where = $db.peca.area_id ==? $input.area_id
              sort = {id: "desc"}
              eval = {area_secao: $db.veiculo_area.Secao}
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

  guid = "4we4HpmQDmi_xL7w83t8q1Vnpdk"
}