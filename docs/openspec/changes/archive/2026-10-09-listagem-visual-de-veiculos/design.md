# Design: Listagem visual de veículos

## Contexto

O endpoint `GET /veiculos` é paginado (padrão de 20, máximo de 100) e retorna
metadados `pagination.total_pages`. O estado compartilhado do app fazia uma
única chamada sem parâmetros, portanto a tela exibia no máximo a primeira
página. A API também sanitizava os campos devolvidos e omitia `Imagem_url`.
O formulário de cadastro já enviava essa propriedade, mas o schema não a
persistia.

## Decisões

1. **Carregamento completo:** apenas a tela de veículos percorrerá as páginas
   informadas pela API, solicitando 100 registros por página e acumulando os
   resultados antes de atualizar a tela. Respostas ou metadados inválidos
   devem resultar em erro explícito, sem apresentar uma lista parcial como
   completa.
2. **Apresentação:** em telas amplas, a grade apresenta três colunas; em
   viewports menores, reduz para duas ou uma coluna. A imagem usa proporção
   paisagem e `object-fit: cover`, com alternativa textual quando não existe
   URL. Os dados incluem marca/modelo, ano, quilometragem e preço.
3. **Imagem no contrato:** reutilizar o campo `imagem_url` opcional já
   existente no schema remoto. Cadastro, consulta individual, edição e
   listagem recebem/exibem a chave de API `Imagem_url` e mapeiam para o nome
   persistido em minúsculas, evitando remover dados por diferença de caixa.
4. **Compatibilidade:** registros sem imagem e sem quilometragem permanecem
   válidos e são apresentados com textos substitutos.
5. **Busca:** a busca existente na tela continua local sobre os registros
   carregados; este escopo não altera a semântica de filtros do endpoint.
6. **Publicação:** esta change termina no dry-run remoto não destrutivo. Os
   scripts locais não são prova de que o workspace publicado tenha o mesmo
   contrato; publicação e validação autenticada em runtime são uma etapa
   operacional separada, após autorização explícita.

## Riscos e validação

- Muitas páginas podem aumentar o tempo de carregamento; limitar cada
  resposta a 100 e seguir o total publicado pela API, em vez de uma consulta
  sem limite.
- A operação remota requer schema e endpoints compatíveis. O primeiro dry-run
  detectou que o nome local `Imagem_url` causaria remoção do campo remoto
  `imagem_url`; o contrato local foi alinhado ao campo remoto. O segundo
  dry-run confirmou somente atualizações sem operação destrutiva. A aplicação
  efetiva no Xano ainda requer autorização e validação separadas.
- Testes locais verificam paginação e apresentação, mas não substituem a
  validação de autenticação e do contrato remoto.
