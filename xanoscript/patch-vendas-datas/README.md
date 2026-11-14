# Correção isolada dos filtros de data de vendas

**Obsoleto em 14/11/2026 — não publicar este patch.** A definição remota consultada
usa quatro caminhos de consulta e contém a correção das referências
de IDs com `in`. A definição atual foi sincronizada em
`xanoscript/workspace_current/api/vendas/vendas_GET.xs` e conferida por uma
prévia CLI sem diferenças. O conteúdo abaixo é histórico de uma proposta
que não foi publicada por esta sessão.

Preparada em 13/11/2026 a partir de nova leitura do workspace `147643`.
A consulta de branches confirmou `v1 (live)` como única branch existente.

## Problema e alteração

O usuário relata HTTP 400 `ParseError: Invalid value for param:"venda.data_venda"`
nas consultas de vendas. A definição remota contém comparações de timestamp
com variáveis opcionais nulas protegidas por condições `OR` no `where`.
Esse trecho é o candidato à falha; não foi obtido trace autenticado que
identifique a instrução exata.

Este patch troca somente as duas condições de data:

```text
($parsed_data_inicio == null || $db.venda.data_venda >= $parsed_data_inicio)
→ $db.venda.data_venda >=? $parsed_data_inicio

($parsed_data_fim == null || $db.venda.data_venda <= $parsed_data_fim)
→ $db.venda.data_venda <=? $parsed_data_fim
```

A intenção é usar comparações condicionais para ignorar limites vazios na
consulta ao banco, em vez de depender de curto-circuito de uma expressão SQL.
Operadores condicionais de igualdade (`==?`) já estão presentes nas consultas
remotas de veículos e peças. A variante para comparações de data precisa ser
confirmada pelo importador/execução do Xano; a prévia CLI não comprova isso.

O arquivo mantém o GUID do endpoint, todos os outros filtros, a paginação,
o tratamento de vendedor e o formato da resposta obtidos do remoto. Não usar
`workspace_current` para publicar esta correção: ele contém diferenças alheias
à tarefa. O snapshot histórico em `docs/contexto/` permanece intacto.

## Prévia realizada

```powershell
xano.cmd workspace push --workspace 147643 --branch v1 --directory xanoscript/patch-vendas-datas --dry-run
```

Resultado: `API Endpoints ~1 updated`, `UPDATE query vendas GET`.
A prévia terminou com código 0; não houve publicação nem execução da consulta.
O CLI 1.3.4 não aceita `--no-records` ou `--no-env`, apesar de citá-los em seus
exemplos; essas flags não foram usadas na prévia bem-sucedida. O diretório só
contém um documento XanoScript de endpoint, sem schema, registros ou segredos.

## Aceite após publicação autorizada

Executar com sessão de teste, sem expor token: consulta sem datas, somente
início, somente fim e ambos os limites; conferir os registros nas bordas do
intervalo, forma/busca preenchidas e ambas as telas Clientes/Vendas.
Não reportar sucesso remoto com base na prévia ou em testes Python.

Backup de referência: definição obtida nesta análise em
`docs/contexto/xano-2026-11-13/api/vendas/vendas_GET.xs`; antes de publicar,
comparar novamente se houve edição concorrente do endpoint.
