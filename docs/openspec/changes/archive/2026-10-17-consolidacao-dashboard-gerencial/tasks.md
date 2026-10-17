# Tarefas

## Frontend

- [x] Normalizar envelopes e variações dos indicadores do Xano.
- [x] Corrigir cards de estoque, pagamentos, análises e vendas por vendedor.
- [x] Calcular ticket médio com valor bruto e quantidade de vendas retornados
      pela API.
- [x] Remover o bloco visual de diagnóstico de parcelas.
- [x] Remover descontos, canal de venda, conversão e giro da interface.

## Backend Xano

- [x] Calcular parcelas recebidas com status, valor, data e venda válida.
- [x] Buscar venda relacionada diretamente pelo `venda_id`.
- [x] Calcular vendas pagas distintas e ticket médio da API.
- [x] Adicionar diagnóstico interno de parcelas.
- [x] Corrigir o filtro opcional de `vendedor_id`.
- [x] Restringir dashboard e recebimento ao cargo `Gerente`.
- [x] Sincronizar e publicar o endpoint de indicadores no workspace 147643.

## Verificação

- [x] Executar `python -m unittest discover -s tests`.
- [x] Validar importação de `app.pages.gerenciamento`.
- [x] Executar `git diff --check` nos arquivos alterados.
- [x] Confirmar live e draft do Xano quando aplicável.

## Observação

- [x] Registrar que a validação de valores reais depende de uma sessão
      autenticada com parcelas de produção qualificadas.
