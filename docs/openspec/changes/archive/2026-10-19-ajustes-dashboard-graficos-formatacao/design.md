# Design: Ajustes visuais e validação dos gráficos

## Dados e formatação

O estado do dashboard preserva os campos numéricos usados pelo Recharts.
Campos derivados são adicionados somente quando necessários para a
apresentação:

- `periodo_formatado`: data em `DD/MM/AAAA`;
- `valor_total`: número arredondado para duas casas decimais;
- `cor`: cor da categoria ou coluna;
- `valor_total` auxiliar no gráfico de categorias para o tooltip.

Valores monetários usam formatação brasileira:

```text
R$ 56.780,67
```

O arredondamento usa `ROUND_HALF_UP`, evitando depender do comportamento
binário de `float` para valores financeiros.

## Timeline

O eixo X utiliza `periodo_formatado`, enquanto `periodo` permanece disponível
para agrupamento e ordenação. O eixo Y é identificado como `R$`. Não são
renderizados rótulos permanentes sobre os pontos; os valores aparecem no
tooltip durante a interação.

## Gráficos de barras

Os gráficos de veículos por marca e peças por categoria usam células
individuais com cores distintas. A largura e o espaçamento das barras são
configurados explicitamente para manter agrupamento visual consistente.

O gráfico de peças mantém uma série auxiliar transparente de `valor_total`.
Essa série não cria uma coluna adicional visível, mas permite que o tooltip
apresente:

- quantidade de peças;
- valor total em reais.

As barras não exibem rótulos permanentes. Quantidades e valores são exibidos
somente no tooltip.

## Relatório por status

O parser diferencia campos de quantidade e campos monetários. `total_vendas`
é renderizado como inteiro, enquanto `valor_total`, `valor_bruto`,
`valor_liquido` e campos equivalentes são renderizados como moeda.

Exemplo:

```text
Descricao: Concluída · Total vendas: 99 · Valor total: R$ 3.123.723,30
```

## Validação Xano

O Xano CLI foi usado para puxar live e draft do workspace `147643`. As duas
versões remotas estavam idênticas e continham os agregados consumidos pelo
frontend, incluindo `kpis`, `vendas_timeline`,
`veiculos_vendidos_por_marca` e `pecas_vendidas_por_categoria`.

Foi registrado que o endpoint remoto ainda considera status de venda
`Paga`/`Concluída` no cálculo financeiro, além de parcelas explicitamente
recebidas. Essa regra permanece uma decisão de contrato do Xano e não foi
alterada por esta change.
