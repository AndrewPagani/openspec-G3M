# Proposta: Dashboard analítico de vendas

## Por que

O dashboard existente exibia KPIs e relatórios como texto, sem visualização
gráfica, seleção de granularidade, exportação ou uma hierarquia visual
adequada para acompanhamento de vendas. Também era necessário manter a
apresentação estritamente alinhada aos dados e métricas que o endpoint atual
do Xano realmente fornece.

## O que muda

- Organizar o dashboard responsivo em filtros, KPIs, evolução temporal e
  painéis de vendas e estoque, com gráficos Recharts, cartões e tema alinhado
  à aplicação.
- Oferecer filtros de data, atualização explícita e exportação CSV dos
  indicadores apresentados.
- Agrupar a série diária de vendas recebida do endpoint existente por dia,
  semana ISO, mês ou ano; apresentar a série de formas de pagamento e mix de
  itens com gráficos adequados aos campos disponíveis.
- Consultar os indicadores com `httpx.AsyncClient`, token da sessão e filtros
  já suportados pelo Xano, sem expor credenciais ao frontend.
- Identificar como indisponíveis as métricas sem fonte no contrato/schema
  atual, em vez de inventar valores ou resultados de contingência.
- Atualizar a especificação canônica do dashboard, este registro da mudança e
  a documentação de execução.

## Fora do escopo

- Criar ou publicar endpoints/alterações de schema Xano para métricas ainda
  não suportadas.
- Inferir taxa de conversão, giro, vendas por marca, participação de mercado,
  categoria/fabricante de peças ou canal de venda a partir de dados
  insuficientes.
- Substituir a autorização do backend, adicionar dados de demonstração ou
  usar ASAAS/gateway para determinar recebimentos.

## Impacto

- Reflex: `app/pages/gerenciamento.py`,
  `app/state/dashboard_state.py` e `app/services/xano_client.py`.
- Interface e dependências: Recharts no bundle Reflex e estilos em
  `assets/styles.css`.
- Testes: agregação temporal, transformação de séries e chamadas HTTP
  assíncronas em `tests/`.
- Documentação: spec `dashboard-gerencial` e instruções do `README.md`.

## Verificação

- 33 testes locais passaram, incluindo os novos testes do dashboard e do
  cliente assíncrono.
- `compileall` e `git diff --check` passaram.
- O componente Reflex compilou, o backend respondeu `pong` e a rota de
  gerenciamento foi verificada no navegador.
- Nenhuma alteração foi publicada no Xano.
