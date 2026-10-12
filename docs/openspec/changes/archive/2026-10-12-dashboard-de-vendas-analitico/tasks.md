# Tarefas

## 1. Especificar a integração e a apresentação

- [x] 1.1 Conferir o endpoint Xano, suas métricas e dimensões realmente
  disponíveis.
- [x] 1.2 Definir KPIs, gráficos, filtros e exportação sem pressupor campos
  ausentes.
- [x] 1.3 Registrar limites do contrato para conversão, giro, marcas,
  categorias e canal de venda.

## 2. Implementar o dashboard

- [x] 2.1 Adicionar chamada Xano assíncrona autenticada via
  `httpx.AsyncClient`, com tratamento de erros.
- [x] 2.2 Transformar agregados temporais em séries por dia, semana ISO, mês
  e ano.
- [x] 2.3 Adaptar séries de pagamento, mix de itens e estoque aos gráficos
  Recharts, omitindo categorias sem valores e limitando legendas extensas.
- [x] 2.4 Criar cabeçalho, controles de data, atualização, exportação CSV e
  cards de indicadores responsivos.
- [x] 2.5 Sinalizar explicitamente indicadores que dependem de evolução
  futura do schema/API, sem fallback fictício.
- [x] 2.6 Atualizar estilos e instruções do projeto.

## 3. Testar e arquivar

- [x] 3.1 Testar formatação, agrupamento temporal, validação de dados e
  filtros de perfil.
- [x] 3.2 Testar cliente HTTP assíncrono autenticado e tratamento de sessão
  expirada.
- [x] 3.3 Executar toda a suíte `unittest` (33 testes), `compileall` e
  `git diff --check`.
- [x] 3.4 Compilar e renderizar a página Reflex localmente e verificar o
  endpoint de saúde do backend.
- [x] 3.5 Atualizar a especificação canônica e arquivar esta change. Nenhuma
  publicação no Xano foi executada.

## Acompanhamento fora desta change

- Estender e validar no Xano os agregados para conversão e giro de estoque.
- Modelar venda por marca, categoria e fabricante de peças e canal de venda;
  depois incluir essas dimensões em endpoint e testes próprios.
