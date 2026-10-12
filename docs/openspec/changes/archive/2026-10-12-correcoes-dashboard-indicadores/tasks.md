# Tarefas

## Implementação

- [x] Adicionar `vendas_timeline` ao contrato versionado do endpoint.
- [x] Aceitar datas ISO, datas simples, timestamps e objetos de data.
- [x] Aceitar envelopes de resposta do Xano para séries e timeline.
- [x] Agrupar semana ISO, mês e ano localmente sem nova requisição.
- [x] Aceitar variações de nomes de campos de pagamentos, status e estoque.
- [x] Preservar categorias zeradas retornadas pela API.
- [x] Exibir diagnóstico quando o gráfico não possui movimento visível.

## Verificação

- [x] Testar agrupamento diário, semanal, mensal e anual.
- [x] Testar timeline com `data_venda`, `Valor_final` e timestamp numérico.
- [x] Testar respostas aninhadas e variações de campos.
- [x] Testar categorias com valor zero.
- [x] Executar testes de dashboard e cliente Xano: 30 aprovados.
- [x] Executar `compileall`, importação do dashboard e `git diff --check`.

## Limitação conhecida

- [x] Registrar que a publicação do `.xs` no Xano remoto é necessária para
      disponibilizar `vendas_timeline`; a alteração local não publica API.
- [x] Registrar que a exportação Reflex foi bloqueada ao limpar `.web/build`
      por permissão de processo externo, depois de compilar os componentes.
