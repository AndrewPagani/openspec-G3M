# Corrigir filtros opcionais de data na consulta de vendas

O usuário relata erro HTTP 400 de parsing de `venda.data_venda` após a
correção dos filtros JSON vazios. A consulta remota mistura guardas de
variáveis nulas e comparações de timestamp no `where`.

Preparar correção isolada de `GET /vendas`, usando filtros de comparação
condicional por data, sem modificar a semântica das datas preenchidas,
o schema, a resposta ou outros endpoints. O diagnóstico da instrução exata
e o sucesso da correção dependem de execução autenticada.

Prévia CLI na branch `v1 (live)`: somente um endpoint atualizado. A publicação
e a validação remota ainda estão pendentes.
