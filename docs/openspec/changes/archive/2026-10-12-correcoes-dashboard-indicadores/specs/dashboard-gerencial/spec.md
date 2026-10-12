# Correções da especificação do dashboard gerencial

## Requisitos

### Requisito: timeline baseada em vendas

O endpoint de indicadores MUST retornar `vendas_timeline` derivada de
`venda.data_venda` e `venda.Valor_final`, respeitando os filtros e o escopo de
autorização existentes.

#### Cenário: vendas no período

- **DADO** que existem vendas autorizadas no intervalo selecionado
- **QUANDO** o dashboard consulta os indicadores
- **ENTÃO** cada venda deve contribuir com um ponto de timeline contendo data,
  quantidade e valor.

### Requisito: agrupamento de períodos

A aplicação MUST agrupar a série carregada em dia, semana ISO, mês e ano sem
precisar consultar novamente o Xano ao alternar o período.

#### Cenário: seleção semanal, mensal ou anual

- **QUANDO** o usuário seleciona Semana, Mês ou Ano
- **ENTÃO** os dados já carregados devem ser reagrupados localmente e exibidos
  no gráfico.

### Requisito: respostas compatíveis

A aplicação MUST aceitar séries na raiz ou dentro de envelopes suportados e
MUST aceitar os nomes de campos documentados no design desta change.

#### Cenário: resposta envelopada

- **QUANDO** o Xano retorna a série dentro de `data`, `result`, `payload` ou
  `response`
- **ENTÃO** o dashboard deve extrair e transformar a série sem descartá-la.

### Requisito: estado sem movimento

O dashboard MUST preservar categorias com valor zero e MUST informar
explicitamente quando todas as categorias retornadas estiverem zeradas, em vez
de apresentar um gráfico vazio sem diagnóstico.

#### Cenário: métodos sem vendas

- **QUANDO** a API retorna métodos de pagamento com `total_vendas = 0`
- **ENTÃO** o card deve informar que não há movimento no período e mostrar os
  valores recebidos.
