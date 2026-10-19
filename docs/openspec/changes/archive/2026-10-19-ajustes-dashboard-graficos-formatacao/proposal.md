# Proposta: Ajustes visuais e validação dos gráficos do dashboard

## Problema

Os ajustes do dashboard realizados em 19/10/2026 ainda não estavam
consolidados em uma change. A timeline precisava de formatação brasileira
para datas e moeda, os gráficos precisavam exibir informações adicionais
sem poluir a interface e os relatórios de status estavam confundindo
quantidades com valores monetários.

## Objetivo

Registrar e consolidar as alterações de apresentação, parsing e validação
realizadas no dashboard gerencial, mantendo os dados numéricos adequados para
os gráficos e a API Xano como fonte dos indicadores.

## Escopo

- Formatar datas visíveis da timeline como `DD/MM/AAAA`.
- Identificar o eixo Y da timeline como `R$` e manter valores numéricos para
  escala, ordenação e interação.
- Exibir valores monetários da timeline no tooltip com duas casas decimais.
- Exibir quantidade e valor total de peças por categoria no tooltip.
- Aplicar cores distintas às colunas de marcas e categorias, sem alterar a
  timeline.
- Ajustar largura, espaçamento e alinhamento das colunas de categorias.
- Exibir quantidades e valores somente ao passar o mouse sobre os gráficos.
- Corrigir o relatório de vendas por status para exibir quantidade como inteiro
  e valor total como moeda brasileira.
- Arredondar valores financeiros para duas casas decimais com arredondamento
  financeiro.
- Validar a resposta do endpoint de indicadores via Xano CLI e registrar a
  compatibilidade do frontend com o contrato atual.

## Fora do escopo

- Alterar registros financeiros no Xano.
- Criar dados de vendas, parcelas ou categorias.
- Alterar a regra de negócio de faturamento recebido.
- Publicar uma nova versão do endpoint sem uma mudança explícita no contrato.

## Resultado

A implementação foi concluída e arquivada nesta change em 19/10/2026.
