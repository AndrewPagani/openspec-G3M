# Proposta: Correções dos indicadores do dashboard

## Problema

Após a implementação do dashboard analítico, alguns indicadores não eram
exibidos corretamente. A timeline dependia de um formato único de resposta do
Xano, os períodos semanal, mensal e anual disparavam novas consultas
desnecessárias, e os gráficos de pagamentos, mix e estoque podiam aparecer
vazios mesmo quando a API retornava categorias com valores zero.

## Objetivo

Tornar o dashboard resiliente ao contrato de resposta efetivamente devolvido
pela API de indicadores, mantendo os dados originados no Xano e deixando
explícito quando não há movimento no período consultado.

## Escopo

- Aceitar datas da timeline em formatos ISO, timestamp e envelopes comuns do
  Xano.
- Derivar semana ISO, mês e ano localmente a partir da série carregada da
  tabela `venda`.
- Aceitar séries de indicadores dentro de envelopes como `data`, `result`,
  `payload` e `response`.
- Aceitar variações de nomes de campos para métodos de pagamento e status.
- Preservar categorias retornadas com quantidade zero.
- Substituir gráficos sem pontos visíveis por diagnóstico com os valores
  recebidos pela API.
- Registrar a série de timeline no endpoint versionado
  `indicadores_GET.xs` como `vendas_timeline`, usando `venda.data_venda` e
  `venda.Valor_final`.

## Fora do escopo

- Criar dados fictícios no frontend.
- Alterar regras de autorização do Xano.
- Criar conversão, giro, marca, fabricante ou canal sem campos/fontes
  existentes no backend.
- Publicar automaticamente a alteração no workspace remoto do Xano.

## Verificação

- Testes unitários do estado e cliente Xano.
- Compilação Python e importação da página Reflex.
- `git diff --check`.
- Exportação Reflex tentou compilar a aplicação; a compilação chegou a 100%,
  mas a limpeza do diretório `.web/build` foi bloqueada por um processo
  externo no Windows.
