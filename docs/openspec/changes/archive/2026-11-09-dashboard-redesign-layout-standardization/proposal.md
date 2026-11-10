# Proposta: Redesign do dashboard e padronização do layout

## Por que

O dashboard atual apresenta filtros por ID digitável, hierarquia visual pouco
clara e identidade inconsistente com a referência de produto. Os operadores
precisam selecionar filtros legíveis, revisar indicadores e análises em uma
interface responsiva, mantendo os valores e limites de autorização fornecidos
pela API Xano.

## O que muda

- Simplificar a marca da barra lateral para o selo G3M e remover o indicador
  “On-line” do perfil.
- Aplicar ao shell do dashboard a paleta Dark Slate, superfícies elevadas,
  texto com hierarquia clara e acentos por categoria de indicador.
- Consolidar título, intervalo de datas, exportação CSV e atualização dos dados
  no cabeçalho do dashboard.
- Substituir campos numéricos de IDs por seletores que mostram os nomes e
  enviam os identificadores originais retornados pela API.
- Apresentar os seis KPIs, gráficos, inventário e detalhamentos com estados
  vazios explícitos e grids responsivos.
- Preservar dados dinâmicos do Xano: não inserir contagens, status, usuários,
  marcas, categorias ou valores de exemplo.

## Fora do escopo

- Alterar regras de autorização, filtros ou cálculos do endpoint Xano.
- Publicar alterações Xano ou introduzir endpoints para dados que a API atual
  não fornece.
- Exibir valor total por status de venda se o payload não contiver esse campo.
- Alterar a identidade visual da tela de login ou criar conteúdo de demonstração.

## Capabilities

### Novas

- `interface-interna`: marca simplificada e remoção do indicador de presença
  no perfil da barra lateral.

### Modificadas

- `dashboard-gerencial`: cabeçalho, filtros, KPIs, gráficos, inventário,
  detalhamentos e adaptação responsiva.

## Impacto

- Reflex: `app/pages/gerenciamento.py`, `app/state/dashboard_state.py` e
  `app/components/app_shell.py`.
- Estilos: `assets/styles.css` e paleta semântica em
  `app/services/vehicle_status.py`.
- Validação: `tests/test_dashboard_state.py`, compilação Python, exportação
  Reflex e revisão visual/responsiva.
