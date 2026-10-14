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
    // Obter tabela de status para lookup de descricao
    db.query status_veiculo {
      return = {type: "list"}
    } as $status_list
  
    // Identificar ID do status Disponivel se necessario
    var $disp_status_id {
      value = null
    }
  
    conditional {
      if ($input.somente_disponiveis) {
        var $disp_item {
          value = $status_list|find:($$.Descricao == "Disponível" || $$.Descricao == "Disponivel")
        }
      
        conditional {
          if ($disp_item != null) {
            var.update $disp_status_id {
              value = $disp_item.id
            }
          }
        }
      }
    }
  
    // Consultar veiculos aplicando filtros dinamicos
    db.query veiculo {
      where = ($input.somente_disponiveis != true || $db.veiculo.status_id == $disp_status_id) && ($input.status_id == null || $db.veiculo.status_id == $input.status_id) && ($input.marca == null || $db.veiculo.Marca == $input.marca) && ($input.modelo == null || $db.veiculo.Modelo == $input.modelo) && (($input.busca == null || $input.busca == "") || ($db.veiculo.Marca includes $input.busca || $db.veiculo.Modelo includes $input.busca || $db.veiculo.Placa includes $input.busca || $db.veiculo.Chassi includes $input.busca))
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
  
    // Mapear resultado associando a descricao do status
    var $sanitized_items {
      value = ```
        $result.items|map:{
                id: $$.id,
                Marca: $$.Marca,
                Modelo: $$.Modelo,
                Cor: $$.Cor,
                Ano: $$.Ano,
                Placa: $$.Placa,
                Chassi: $$.Chassi,
                Quilometragem: $$.Quilometragem,
                Preco: $$.Preco,
                Imagem_url: $$.Imagem_url,
                status_id: $$.status_id,
                status_descricao: (($status_list|find:$item.id == $$.status_id).Descricao ?? ""),
                created_at: $$.created_at
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

  guid = "0nRNiFt61PHtpypl-tP3dj1pN1s"
}