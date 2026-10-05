// Listagem paginada de pecas com filtros de busca, area e disponibilidade
// Lista pecas de estoque com filtros por nome, secao/area e disponibilidade
// Parametros de paginacao e filtros de busca
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
    // Obter areas para enriquecimento dos dados
    db.query veiculo_area {
      return = {type: "list"}
    } as $areas_list
  
    // Consultar pecas com filtros
    db.query peca {
      where = ($input.somente_disponiveis != true || $db.peca.qtd_disp > 0) && ($input.area_id == null || $db.peca.area_id == $input.area_id) && (($input.busca == null || $input.busca == "") || ($db.peca.PCNome includes $input.busca))
      sort = {id: "desc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }
    } as $result
  
    // Mapear resultado adicionando nome da secao/area
    var $sanitized_items {
      value = ```
        $result.items|map:{
                id: $$.id,
                PCNome: $$.PCNome,
                PCvalor: $$.PCvalor,
                qtd_disp: ($$.qtd_disp ?? 0),
                area_id: $$.area_id,
                area_secao: (($areas_list|find:$item.id == $$.area_id).Secao ?? null)
              }
        ```
    }
  }

  response = {
    items     : $sanitized_items
    pagination: ```
      {
        page: $result.curPage,
        per_page: $result.perPage,
        total: $result.total ?? ($result.items|count),
        total_pages: $result.pageTotal ?? 1
      }
      ```
  }

  guid = "4we4HpmQDmi_xL7w83t8q1Vnpdk"
}