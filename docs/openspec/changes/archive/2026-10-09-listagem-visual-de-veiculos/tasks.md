# Tarefas

## 1. Especificar o comportamento

- [x] 1.1 Definir carregamento de todas as páginas sem alterar os filtros da API.
- [x] 1.2 Definir cards com imagem retangular, nome, ano, quilometragem e preço.
- [x] 1.3 Definir grade responsiva de três colunas em telas amplas.
- [x] 1.4 Definir `Imagem_url` opcional e compatibilidade com veículos legados.

## 2. Implementar no workspace local

- [x] 2.1 Carregar todas as páginas de veículos conforme `total_pages`, com até
  100 registros por página e validação das respostas.
- [x] 2.2 Normalizar quilometragem e imagem para a apresentação dos cartões.
- [x] 2.3 Exibir imagem em destaque, marca/modelo, ano, quilometragem e preço
  em uma grade responsiva.
- [x] 2.4 Alinhar o schema local ao campo remoto existente `imagem_url` e
  expor/mapear a chave de API `Imagem_url` em listagem, criação, consulta e
  edição, sem renomear nem remover dados remotos.
- [x] 2.5 Cobrir paginação e exibição de quilometragem em testes locais.
- [x] 2.6 Atualizar a spec consolidada com os requisitos da change.

## 3. Validar e sincronizar

- [x] 3.1 Rodar testes focados de exibição/paginação, `compileall` e
  `git diff --check`.
- [x] 3.2 Concluir exportação/build Reflex; exportação completa passou em uma
  cópia temporária fora do OneDrive, pois a pasta `.web/build` original tem
  bloqueio de exclusão no Windows.
- [x] 3.3 Gerar dry-run do workspace Xano e conferir os objetos. A primeira
  prévia identificou diferença de caixa no campo (`imagem_url` remoto versus
  `Imagem_url` local), que indicava perda de dados. Após alinhar o mapeamento,
  a prévia de 09/10/2026 mostrou atualização da tabela `veiculo` e dos quatro
  endpoints (GET listagem, POST criação, GET detalhe e PATCH edição), sem
  operações destrutivas.
- [x] 3.4 Registrar publicação no workspace Xano e validação autenticada em
  runtime como etapa operacional separada, após autorização explícita; não
  publicar como parte desta change.

## Acompanhamento fora desta change

- Publicar a prévia aprovada no workspace 147643 após autorização explícita.
- Validar endpoints autenticados, imagem e paginação além da primeira página
  no ambiente publicado.
