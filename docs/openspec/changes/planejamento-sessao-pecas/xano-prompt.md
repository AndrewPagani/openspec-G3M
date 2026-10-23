# Prompt para alterações no Xano

Implemente as alterações abaixo no workspace Xano `147643`, grupo de APIs
`cadastros`, preservando os GUIDs dos endpoints existentes e sem apagar dados.

## Contexto importante

A tabela `peca` já existe e deve ser reutilizada. **Não crie uma segunda
tabela de peças.** A tabela atual possui:

- `id`;
- `PCNome`;
- `PCvalor`;
- `qtd_disp`;
- `area_id`, relacionado a `veiculo_area`.

O endpoint `GET /api:cadastros/pecas` já possui paginação, busca, filtro por
área e `somente_disponiveis`. Preserve esse comportamento.

## 1. Alterar a tabela `peca`

Adicionar o campo opcional:

```text
Imagem_url: text?
```

Regras:

- aceitar vazio/nulo;
- quando preenchido, aceitar apenas URLs HTTP ou HTTPS;
- não alterar os registros existentes;
- manter os índices atuais.

## 2. Atualizar `POST /api:cadastros/pecas`

Adicionar ao input:

```text
text Imagem_url?
```

Validar:

- `PCNome` obrigatório;
- `PCvalor >= 0`;
- `qtd_disp >= 0`;
- `area_id`, quando informado, deve existir em `veiculo_area`;
- `Imagem_url`, quando informada, deve usar esquema `http` ou `https`.

Persistir o campo na tabela e retorná-lo na resposta:

```json
{
  "id": 25,
  "PCNome": "Pastilha de freio",
  "PCvalor": 299.90,
  "qtd_disp": 8,
  "area_id": 2,
  "area_secao": "Freios",
  "Imagem_url": "https://..."
}
```

## 3. Atualizar `PATCH /api:cadastros/pecas/{id}`

Adicionar `Imagem_url?` aos campos permitidos para edição, com a mesma
validação HTTP/HTTPS. Não permitir alteração direta de `qtd_disp`; o estoque
deve continuar sendo alterado exclusivamente pelo endpoint de ajuste de
estoque existente.

Retornar também `Imagem_url`.

## 4. Atualizar `GET /api:cadastros/pecas`

Manter:

- `page`;
- `per_page`;
- `busca`;
- `area_id`;
- `somente_disponiveis`;
- paginação com `total_pages`.

Adicionar filtros opcionais:

```text
bool estoque_baixo?
bool sem_estoque?
```

Regras:

```text
estoque_baixo = qtd_disp > 0 && qtd_disp <= 5
sem_estoque = qtd_disp == 0
```

Se `estoque_baixo` ou `sem_estoque` forem informados, combinar os filtros com
os demais usando `AND`. Não permitir que os dois filtros retornem registros
simultaneamente; retornar erro de entrada caso ambos sejam `true`.

Normalizar cada item para:

```json
{
  "id": 25,
  "nome": "Pastilha de freio",
  "preco": 299.90,
  "quantidade_disponivel": 8,
  "area_id": 2,
  "area_nome": "Freios",
  "imagem_url": "https://..."
}
```

Se a compatibilidade do frontend atual precisar ser preservada, inclua também
temporariamente os campos antigos `PCNome`, `PCvalor`, `qtd_disp` e
`area_secao` na resposta. Não remova campos sem confirmar a migração do
frontend.

## 5. Segurança e venda

- Manter autenticação `user` nos endpoints.
- Cadastro, edição e ajuste de estoque devem continuar restritos ao perfil
  `Gerente`, conforme as regras existentes.
- O endpoint `POST /api:vendas/vendas` deve continuar sendo a fonte de verdade
  para preço e estoque.
- Ao receber `peca_id` e `qtd`, revalidar estoque e preço dentro da operação
  da venda.
- Não confiar em preço enviado pelo frontend.
- Não criar venda apenas ao abrir ou clicar no card; o frontend usará carrinho
  antes do checkout.

## 6. Validação obrigatória

Antes de publicar:

1. Executar validação sintática dos documentos.
2. Executar testes dos endpoints com:
   - peça com imagem;
   - peça sem imagem;
   - estoque zero;
   - estoque baixo;
   - estoque acima de cinco;
   - filtro por área;
   - busca por nome;
   - paginação.
3. Comparar live e draft.
4. Executar `--dry-run` antes de qualquer publicação.
5. Não publicar alterações destrutivas nem substituir a tabela `peca`.

Retorne o contrato final dos endpoints, exemplos de resposta e o resultado da
validação live/draft.

## Correção prioritária: paginação inválida

O frontend está recebendo o erro:

```text
A API retornou paginação inválida para a listagem de peças e estoque.
```

Corrija o endpoint `GET /api:cadastros/pecas` para que **toda resposta de
sucesso**, inclusive quando não houver peças, tenha exatamente esta estrutura:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 0,
    "total_pages": 1
  }
}
```

Quando houver registros:

```json
{
  "items": [
    {
      "id": 25,
      "nome": "Pastilha de freio",
      "preco": 299.90,
      "quantidade_disponivel": 8,
      "area_id": 2,
      "area_nome": "Freios",
      "imagem_url": null
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

Regras obrigatórias:

1. `items` deve ser sempre uma lista, nunca `null`, objeto ou resposta sem
   envelope.
2. `pagination` deve ser sempre um objeto.
3. `page`, `per_page`, `total` e `total_pages` devem ser inteiros JSON, não
   strings.
4. `page` deve refletir o parâmetro recebido, com padrão `1`.
5. `per_page` deve refletir o parâmetro recebido, com padrão `20` e máximo
   `100`.
6. `total` deve ser a quantidade total de registros após aplicar os filtros.
7. `total_pages` deve ser no mínimo `1`, mesmo quando `total` for `0`.
8. Calcular `total_pages` como:

   ```text
   max(1, ceil(total / per_page))
   ```

9. Se o retorno nativo de `db.query` usar nomes como `curPage`, `perPage`,
   `pageTotal` ou `total`, converta explicitamente esses campos para
   `page`, `per_page`, `total_pages` e `total` antes de montar a resposta.
10. Não retornar uma lista diretamente no nível raiz.

Teste obrigatoriamente estas chamadas:

```text
GET /api:cadastros/pecas?page=1&per_page=20
GET /api:cadastros/pecas?page=2&per_page=20
GET /api:cadastros/pecas?busca=freio
GET /api:cadastros/pecas?area_id=2
GET /api:cadastros/pecas?somente_disponiveis=true
```

Para cada chamada, valide:

- existência de `items`;
- existência de `pagination`;
- tipo inteiro de `pagination.page`;
- tipo inteiro de `pagination.per_page`;
- tipo inteiro de `pagination.total`;
- tipo inteiro de `pagination.total_pages`;
- `pagination.total_pages >= 1`.

Depois compare live e draft e retorne um exemplo real da resposta corrigida.

## Prompt emergencial para o erro persistente

O erro continua ocorrendo mesmo após a alteração anterior. A verificação pelo
Xano CLI confirmou que **live e draft estão idênticos**, portanto a correção
deve ser feita no documento do endpoint, não apenas publicada em um ambiente.

O documento atual ainda monta a paginação diretamente com:

```text
page: $result.curPage
per_page: $result.perPage
total: $result.total ?? ($result.items|count)
total_pages: $result.pageTotal ?? 1
```

Substitua essa lógica. Não repasse `curPage`, `perPage` ou `pageTotal`
diretamente, pois algum deles está chegando nulo, decimal ou em formato que o
frontend não aceita.

### Alteração obrigatória no endpoint

No endpoint `GET /api:cadastros/pecas`, mantenha a consulta paginada, mas crie
variáveis explícitas antes do `response`:

```text
var $pagina_atual {
  value = $input.page ?? 1
}

var $itens_por_pagina {
  value = $input.per_page ?? 20
}

var $total_registros {
  value = $result.total ?? ($result.items|count)
}

var $total_paginas_calculado {
  value = (($total_registros + $itens_por_pagina - 1) / $itens_por_pagina)|floor
}

conditional {
  if ($total_paginas_calculado < 1) {
    var.update $total_paginas_calculado {
      value = 1
    }
  }
}
```

Se o Xano exigir conversão explícita, aplique a conversão inteira nativa
disponível no workspace a todas as quatro variáveis. O resultado final precisa
ser JSON numérico inteiro, nunca string, `null`, decimal ou booleano.

Substitua o `response` por:

```text
response = {
  items: ($sanitized_items ?? [])
  pagination: {
    page: $pagina_atual
    per_page: $itens_por_pagina
    total: $total_registros
    total_pages: $total_paginas_calculado
  }
}
```

Se a sintaxe de objeto literal exigir bloco multilinha, use o formato de
objeto multilinha equivalente do XanoScript. O ponto essencial é que o
`response.pagination` seja construído com as variáveis calculadas, e não com
`$result.curPage`, `$result.perPage` ou `$result.pageTotal`.

### Não usar fallback silencioso

Não retorne:

```text
pagination: null
pagination: []
pagination: $result
```

Não retorne `total_pages: 0` quando não houver registros. Nesse caso, retorne
`total: 0` e `total_pages: 1`.

### Teste de contrato obrigatório

Execute o endpoint autenticado nas cinco chamadas abaixo e inspecione o JSON
bruto, não apenas a interface:

```text
GET /api:cadastros/pecas?page=1&per_page=20
GET /api:cadastros/pecas?page=2&per_page=20
GET /api:cadastros/pecas?busca=freio
GET /api:cadastros/pecas?area_id=2
GET /api:cadastros/pecas?somente_disponiveis=true
```

Para cada resposta, confirme literalmente:

```text
typeof response.items === "array"
typeof response.pagination === "object"
Number.isInteger(response.pagination.page)
Number.isInteger(response.pagination.per_page)
Number.isInteger(response.pagination.total)
Number.isInteger(response.pagination.total_pages)
response.pagination.page >= 1
response.pagination.per_page >= 1
response.pagination.total >= 0
response.pagination.total_pages >= 1
```

Também teste uma consulta sem resultados. A resposta esperada é:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 0,
    "total_pages": 1
  }
}
```

Só considere a correção concluída depois de:

1. salvar o documento no draft;
2. executar os testes do endpoint;
3. publicar o endpoint corrigido;
4. executar novamente o endpoint live;
5. comparar live e draft;
6. enviar o JSON bruto de uma resposta live corrigida.
