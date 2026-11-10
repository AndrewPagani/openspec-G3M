# Design: Redesign do dashboard e padronização do layout

## Princípios

- O Xano permanece a fonte de verdade; nenhum valor ilustrativo entra no
  estado da tela.
- Filtros exibem rótulos recebidos do Xano e mantêm seus IDs somente como
  valores de consulta.
- A aplicação mostra somente os campos entregues pelo contrato atual. Valores
  ausentes não são convertidos em zeros nem em categorias inventadas.
- A autorização continua aplicada pelo endpoint Xano.

## Layout

- Shell do dashboard: canvas `#090d16`, painel `#0f172a`, borda `#1e293b`,
  texto principal `#f8fafc`, secundário `#94a3b8` e microcopy `#64748b`.
- Acentos: azul `#3b82f6`, verde `#10b981`, roxo `#8b5cf6`, âmbar `#f59e0b`
  e rosa/vermelho `#f43f5e`.
- Cabeçalho único com título, subtítulo, exportação, datas e atualização.
- Filtros do gerente em cinco colunas em telas amplas, reduzindo para três,
  duas e uma coluna em viewports menores.
- KPIs em até três colunas; análises e inventário organizados em grids que
  passam a uma coluna em telas estreitas.

## Filtros com dados Xano

- Status da venda usa `status_id` e `descricao` de
  `vendas_por_status_pagamento`.
- Vendedor usa `vendedor_id` e `nome` de `vendas_por_vendedor`.
- Forma de pagamento usa `forma_id` e `metodo` de
  `vendas_por_forma_pagamento`.
- Status do veículo usa `status_id` e `descricao` de `veiculos_por_status`.
- Tipo de item usa somente os valores do domínio aceitos pelo endpoint:
  `veiculo` e `peca`.
- “Todos” é um estado sem filtro e não é enviado como ID ao Xano. Os seletores
  alimentados por listas ficam desativados quando a resposta não contém opções.

## Apresentação dos dados

- Os seis KPIs mantêm os valores formatados no estado já baseado no payload
  Xano.
- O gráfico de vendas mantém alternância de dia, semana, mês e ano.
- Pagamento, mix, marcas, categorias, status de estoque e vendedores mostram
  estados vazios informativos quando não há dados.
- A lista por status apresenta contagem devolvida pelo Xano e valor somente se
  `valor_total` estiver presente na resposta.
- O perfil mostra avatar e nome/cargo, sem indicador “On-line”.

## Verificação

- Testes de seleção de opções por IDs/rótulos, estados “Todos” e breakdown de
  status sem fabricação de valor.
- Testes existentes de dashboard continuam passando.
- Build Reflex e avaliação dos breakpoints em 1920x1080, 1440x900 e 1366x768.
