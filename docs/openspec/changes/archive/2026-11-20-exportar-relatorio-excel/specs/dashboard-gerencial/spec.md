## MODIFIED Requirements

### Requirement: Dashboard preserva identidade visual e organiza a leitura dos indicadores

O dashboard MUST manter tema escuro, tipografia e linguagem de controles coerentes com o site, com azul como destaque principal e cores semânticas consistentes. A tela MUST identificar período e ações, agrupar os indicadores de vendas e separar visualmente a seção de estoque, informando seu escopo sem atribuir um período não comprovado aos dados. A hierarquia MUST permanecer legível e preservar as métricas e os controles fora da troca da ação de exportação.

#### Scenario: Leitura da visão gerencial
- **WHEN** gerente ou administrador abre o dashboard com dados válidos
- **THEN** período, atualização, indicadores de vendas e seção de estoque MUST ser identificáveis, com até três colunas de KPIs e exportação Excel disponível como ação secundária

#### Scenario: Tela estreita ou zoom ampliado
- **WHEN** o dashboard é exibido com largura de 390px ou zoom de 200% em viewport de 1366x768
- **THEN** filtros e ações MUST permanecer acessíveis, sem sobreposição ou rolagem horizontal da página, e a ordem de leitura MUST acompanhar a organização visual
