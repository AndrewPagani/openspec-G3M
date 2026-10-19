# Especificação: Dashboard gerencial — gráficos e formatação

## Requisitos

### Requisito: Timeline formatada

O dashboard DEVE exibir as datas visíveis da timeline no formato brasileiro
`DD/MM/AAAA`.

O dashboard DEVE identificar o eixo vertical da timeline como `R$` e DEVE
preservar o valor da série como número para manter escala, ordenação e
interação corretas.

O tooltip da timeline DEVE exibir valores monetários com duas casas decimais
no formato brasileiro.

### Requisito: Gráfico de peças por categoria

O dashboard DEVE exibir peças vendidas por categoria em gráfico de barras.

Ao passar o mouse sobre uma categoria, o tooltip DEVE exibir a quantidade de
peças e o valor total em reais, ambos arredondados para duas casas decimais
quando forem valores decimais.

O gráfico DEVE manter as barras agrupadas, com largura consistente e rótulos
do eixo X alinhados às respectivas categorias.

### Requisito: Cores das colunas

Os gráficos de veículos por marca e peças por categoria DEVEM usar cores
distintas por coluna. A timeline NÃO DEVE receber a paleta por categoria.

### Requisito: Interação dos gráficos

Os gráficos de barras NÃO DEVEM exibir quantidade permanentemente sobre as
colunas. A quantidade DEVE aparecer no tooltip durante a interação.

### Requisito: Relatório de vendas por status

O relatório DEVE renderizar `total_vendas` como quantidade inteira, sem
prefixo monetário.

O relatório DEVE renderizar `valor_total` como moeda brasileira com duas casas
decimais.

### Requisito: Compatibilidade com Xano

O frontend DEVE aceitar os agregados retornados por
`GET /api:gerenciamento/indicadores`, incluindo `kpis`,
`vendas_timeline`, `veiculos_vendidos_por_marca` e
`pecas_vendidas_por_categoria`.

A regra de faturamento do endpoint DEVE permanecer explícita no contrato do
Xano. Esta change não deve inferir recebimento a partir de dados ausentes nem
alterar registros financeiros.
