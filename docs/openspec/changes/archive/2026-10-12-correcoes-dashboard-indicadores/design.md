# Design: Correções dos indicadores do dashboard

## Timeline

O endpoint de indicadores mantém `vendas_por_periodo` por compatibilidade e
passa a retornar `vendas_timeline`, com uma entrada por venda filtrada:

```json
{
  "periodo": "2026-10-12T13:00:00Z",
  "total_vendas": 1,
  "valor_total": 1000.00
}
```

A aplicação aceita também registros com `data_venda`, `data`, `date`,
`created_at` ou `timestamp`, inclusive timestamps numéricos e objetos de data.
Depois da primeira consulta, a série é mantida em `timeline_rows`; os botões
de dia, semana, mês e ano apenas reagrupam esses registros localmente.

## Séries de análise

As séries podem estar na raiz da resposta ou em envelopes `data`, `result`,
`payload` e `response`. O estado procura os nomes canônicos e algumas
variações compatíveis:

- pagamentos: `vendas_por_forma_pagamento`,
  `vendas_por_metodo_pagamento` ou `pagamentos`;
- status: `vendas_por_status_pagamento` ou `vendas_por_status`;
- estoque: `veiculos_por_status` ou `estoque_veiculos_por_status`;
- mix: `mix_itens` ou `vendas_por_tipo_item`.

O parser aceita `metodo`, `Metodo`, `forma_pagamento`, `nome`, `descricao`,
`Descricao` ou `status` para o rótulo e `total_vendas`, `quantidade` ou `total`
para o valor.

## Estado vazio

Categorias retornadas pelo Xano com valor zero são preservadas. Entretanto,
um gráfico com todas as categorias zeradas não tem elementos visíveis para o
Recharts desenhar. Nessa situação o card apresenta os valores recebidos e
informa que não existe movimento no período, evitando um canvas aparentemente
quebrado.

## Segurança e fonte dos dados

O token continua sendo enviado somente pelo cliente HTTP autenticado. Nenhum
fallback de negócio é criado no frontend. O escopo de vendas permanece
determinado pelo endpoint Xano e pelo perfil da sessão.
