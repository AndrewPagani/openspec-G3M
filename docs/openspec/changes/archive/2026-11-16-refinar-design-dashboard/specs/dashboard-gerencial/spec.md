## ADDED Requirements

### Requirement: Dashboard preserva identidade visual e organiza a leitura dos indicadores

O dashboard MUST manter tema escuro, tipografia e linguagem de controles coerentes com o site, com azul como destaque principal e cores semânticas consistentes. A tela MUST identificar período e ações, agrupar os indicadores de vendas e separar visualmente a seção de estoque, informando seu escopo sem atribuir um período não comprovado aos dados. A hierarquia MUST permanecer legível sem modificar valores ou controles existentes.

#### Scenario: Leitura da visão gerencial
- **WHEN** gerente ou administrador abre o dashboard com dados válidos
- **THEN** período, atualização, indicadores de vendas e seção de estoque MUST ser identificáveis, com até três colunas de KPIs e exportação CSV disponível como ação secundária

#### Scenario: Tela estreita ou zoom ampliado
- **WHEN** o dashboard é exibido com largura de 390px ou zoom de 200% em viewport de 1366x768
- **THEN** filtros e ações MUST permanecer acessíveis, sem sobreposição ou rolagem horizontal da página, e a ordem de leitura MUST acompanhar a organização visual

### Requirement: Gráficos apresentam unidades legíveis e cores consistentes

Os gráficos MUST identificar a métrica e a unidade exibidas, formatar contagens como inteiros e valores monetários em reais no padrão brasileiro. Tooltips MUST apresentar rótulos e valores completos com contraste legível. Categorias com nomes longos MUST permanecer identificáveis sem depender exclusivamente de hover. Cores semânticas MUST manter seu significado; quando uma cor identifica uma categoria, sua associação MUST permanecer estável ao reordenar ou filtrar os mesmos dados. Cor MUST NOT ser o único meio de identificação.

#### Scenario: Consulta de um valor monetário
- **WHEN** o usuário consulta um ponto de uma série monetária
- **THEN** o tooltip MUST identificar período ou categoria e mostrar o valor completo em reais, mesmo quando o eixo usa abreviações

#### Scenario: Comparação de quantidades e categorias longas
- **WHEN** o gráfico apresenta contagens e nomes extensos
- **THEN** as contagens MUST aparecer sem frações e os nomes MUST estar disponíveis de forma legível também em tela estreita

#### Scenario: Reordenação de uma distribuição
- **WHEN** os mesmos identificadores de categoria reaparecem em outra ordem
- **THEN** categorias identificadas por cores distintas MUST manter a associação entre cor e categoria, com legenda ou rótulo textual correspondente

### Requirement: Textos descrevem os dados sem expor detalhes de implementação

Títulos, descrições e estados vazios MUST usar linguagem de negócio, distinguir valor bruto, recebimento líquido e quantidades, e MUST NOT apresentar instruções sobre contratos internos como explicação principal. Uma revisão de texto MUST NOT atribuir a um número significado diferente de seu cálculo ou origem. Estados vazios, carregamento, falha e resposta incompleta MUST permanecer distinguíveis. Textos e controles MUST ter contraste mínimo de 4,5:1 para texto comum e 3:1 para texto grande; controles MUST apresentar foco visível e nome acessível.

#### Scenario: Série válida sem registros
- **WHEN** uma série autorizada retorna vazia
- **THEN** sua seção MUST informar a ausência de registros com orientação aplicável, sem valores demonstrativos ou instruções genéricas para verificar o Xano

#### Scenario: Indicador local ainda usa média bruta
- **WHEN** o valor apresentado é calculado por valor bruto dividido pelo total de vendas
- **THEN** o cartão MUST identificá-lo como “Valor médio por venda” e explicitar essa base, sem apresentá-lo como ticket médio de recebimentos nem alterar sua fórmula nesta revisão visual

#### Scenario: Navegação por teclado
- **WHEN** o operador percorre filtros, agrupamentos e ações pelo teclado
- **THEN** cada controle MUST ter identificação acessível e foco visível, preservando suas ações e restrições de perfil
