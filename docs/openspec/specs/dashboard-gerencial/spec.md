# dashboard-gerencial Specification

## Purpose
Registra o dashboard que consulta indicadores do endpoint Xano e apresenta KPIs e séries de vendas e estoque conforme o perfil e o contrato de resposta atualmente suportado pela aplicação.

## Requirements

### Requirement: Dashboard deve buscar dados reais do endpoint de indicadores
A tela MUST consultar `/gerenciamento/indicadores` com o token da sessão e o período selecionado, aceitar KPIs agrupados em `kpis` ou no nível superior e apresentar apenas valores retornados pelo Xano. O contrato de resposta do MVP MUST incluir KPIs de vendas e indicadores de veículos/peças autorizados para o perfil, além das séries previstas no contrato. Erro, série ou campo ausente obrigatório MUST ser informado explicitamente e MUST NOT ser substituído por dados simulados.

#### Scenario: Resposta válida de indicadores
- **WHEN** o Xano devolve indicadores em um dos formatos suportados
- **THEN** a tela MUST formatar valores monetários e percentuais e exibir os KPIs e séries presentes na resposta

#### Scenario: Resposta inválida ou chamada recusada
- **WHEN** o Xano não devolve os campos obrigatórios do perfil, retorna erro ou não pode ser alcançado
- **THEN** o dashboard MUST apresentar erro explícito, sem dados simulados

#### Scenario: A API omite uma série prevista no contrato
- **WHEN** uma série obrigatória do perfil está ausente na resposta
- **THEN** o dashboard MUST distinguir resposta incompleta de uma série válida sem registros

### Requirement: Dashboard deve oferecer filtro de período e filtros gerenciais opcionais
A tela MUST permitir selecionar datas inicial/final e oferecer a gerente/administrador filtros opcionais por status de venda, vendedor, forma de pagamento, tipo de item e status de veículo; filtros por ID MUST ser inteiros positivos. O backend MUST aplicar todos os filtros aceitos e limitar o intervalo de consulta conforme limite operacional aprovado.

#### Scenario: Gerente aplica filtros válidos
- **WHEN** gerente ou administrador preenche filtros válidos e atualiza o dashboard
- **THEN** a aplicação MUST enviar somente os filtros preenchidos junto ao período e o backend MUST aplicá-los às métricas correspondentes

#### Scenario: Datas ou filtros inválidos
- **WHEN** a data inicial é posterior à final, ou um filtro numérico/tipo de item possui valor inválido
- **THEN** a aplicação MUST rejeitar a consulta e apresentar uma mensagem de erro

#### Scenario: Consulta excede o período máximo
- **WHEN** o intervalo solicitado excede o limite operacional configurado
- **THEN** o backend MUST rejeitar a consulta com erro compreensível sem carregar histórico ilimitado

### Requirement: Visibilidade do dashboard deve variar por perfil
Gerentes e administradores MUST receber as seções gerenciais autorizadas. A interface MUST omitir filtros gerenciais para vendedores; o escopo efetivo dos registros MUST ser derivado da sessão e imposto pelo backend, sem confiar em `vendedor_id` fornecido pelo cliente.

#### Scenario: Vendedor consulta o dashboard
- **WHEN** vendedor autenticado abre o dashboard
- **THEN** a interface MUST apresentar apenas as áreas autorizadas e MUST NOT enviar filtro de vendedor para ampliar ou substituir o escopo determinado pelo backend

#### Scenario: Gerente consulta o dashboard
- **WHEN** gerente ou administrador autenticado abre o dashboard
- **THEN** a interface MUST apresentar as seções autorizadas de vendas, veículos e peças disponíveis na resposta do Xano

#### Scenario: Vendedor tenta consultar indicadores de outro vendedor
- **WHEN** vendedor envia filtro ou chamada destinada a obter dados de outro vendedor
- **THEN** o backend MUST limitar os resultados às vendas do próprio vendedor ou rejeitar a chamada

### Requirement: Séries sem registros devem ter estado vazio
A tela MUST indicar que uma série está sem dados quando o Xano retorna lista vazia ou não há registros no período, sem converter ausência em registros fictícios. O backend MUST calcular agregações em dados persistidos e MUST NOT carregar coleções completas sem limite para calcular indicadores.

#### Scenario: Série vazia
- **WHEN** a resposta autorizada contém lista vazia para uma série
- **THEN** a seção correspondente MUST apresentar estado vazio legível

#### Scenario: Volume de dados cresce
- **WHEN** o dashboard é consultado sobre um conjunto de dados que excede uma página
- **THEN** o backend MUST usar agregação ou consultas limitadas e MUST NOT depender de carregar todas as entidades para a memória da requisição

### Requirement: Indicadores devem corresponder ao contrato e schema do MVP
O dashboard MUST apresentar, conforme o perfil, total de vendas, valor bruto, descontos, valor líquido recebido, vendas pagas/canceladas e ticket médio; séries por período, status, forma de pagamento, vendedor e mix de veículos/peças; quantidade de veículos por status e disponíveis; saldo disponível de peças e quantidade sem estoque (`qtd_disp = 0`). Cálculos MUST usar dados persistidos e recebimentos ASAAS autoritativos. Vendas canceladas, vencidas ou sem parcela recebida MUST NOT compor receita recebida ou ticket médio. O dashboard MUST NOT exigir limiar configurável de estoque baixo, valor vendido de peças ou contadores persistidos de estoque reservado/vendido que não existam no schema atual. Atualização em tempo real, conversão, leads, test-drives, oficina, pós-venda e tabelas de acompanhamento MUST NOT integrar o MVP.

#### Scenario: Peças sem estoque
- **WHEN** existem peças com `qtd_disp = 0`
- **THEN** o indicador de peças sem estoque MUST contar esses registros

#### Scenario: Venda sem parcela recebida
- **WHEN** a venda não possui cobrança em estado recebido confirmado pelo ASAAS
- **THEN** o valor recebido e o ticket médio MUST NOT contar a venda como paga

#### Scenario: Venda cancelada ou vencida
- **WHEN** venda está cancelada ou expirada
- **THEN** seus valores MUST NOT ser incluídos na receita recebida ou ticket médio

### Requirement: Dashboard apresenta dados Xano em layout responsivo

O dashboard MUST apresentar KPIs, filtros, gráficos e detalhamentos com os
dados autorizados retornados pelo endpoint atual do Xano. A interface MUST
adaptar suas grades ao viewport e MUST NOT substituir ausência de dados por
valores demonstrativos.

#### Scenario: Dashboard com dados reais

- **WHEN** o endpoint retorna indicadores e séries válidas
- **THEN** a interface MUST mapear os valores e rótulos do payload sem alterar
  IDs, estados ou valores numéricos

#### Scenario: API sem valores para uma série

- **WHEN** uma série não contém dados
- **THEN** a interface MUST exibir um estado vazio informativo e MUST NOT
  inventar categorias, usuários, contagens ou valores

#### Scenario: Abertura em resoluções suportadas

- **WHEN** o dashboard é exibido em 1920x1080, 1440x900 ou 1366x768
- **THEN** os KPIs MUST usar até três colunas e os filtros MUST ajustar a
  quantidade de colunas sem overflow ou ocultar controles

### Requirement: Filtros legíveis preservam identificadores Xano

Os filtros de status da venda, vendedor, forma de pagamento e status do veículo
MUST ser seletores preenchidos com rótulos e IDs obtidos das séries retornadas
pelo Xano. Tipo de item MUST oferecer apenas valores aceitos pelo endpoint.
“Todos” MUST omitir o parâmetro correspondente. A tela MUST NOT solicitar IDs
por digitação nem enviar rótulos no lugar de IDs.

#### Scenario: Seleção de um filtro dinâmico

- **WHEN** o operador seleciona uma opção retornada pelo Xano
- **THEN** a requisição MUST enviar o identificador original dessa opção

#### Scenario: Opções ausentes

- **WHEN** a resposta não fornece opções para um filtro dinâmico
- **THEN** o seletor MUST permanecer desativado sem apresentar opções
  presumidas

#### Scenario: Filtro “Todos”

- **WHEN** o operador mantém “Todos” selecionado
- **THEN** a aplicação MUST omitir o parâmetro de filtro da requisição

### Requirement: Breakdown de status exibe somente valores retornados

A lista de vendas por status MUST exibir descrição e quantidade retornadas pelo
Xano e MUST exibir valor total somente quando esse campo estiver no payload.
Campos ausentes MUST NOT ser substituídos por zero.

#### Scenario: API fornece quantidade e valor

- **WHEN** a API retorna descrição, contagem e valor total para um status
- **THEN** a interface MUST apresentar os três valores com formatação apropriada

#### Scenario: API não fornece valor total

- **WHEN** a API retorna descrição e contagem, mas omite valor total
- **THEN** a interface MUST exibir descrição e contagem e MUST NOT apresentar
  um valor presumido

### Requirement: Dashboard preserva identidade visual e organiza a leitura dos indicadores

O dashboard MUST manter tema escuro, tipografia e linguagem de controles coerentes com o site, com azul como destaque principal e cores semânticas consistentes. A tela MUST identificar período e ações, agrupar os indicadores de vendas e separar visualmente a seção de estoque, informando seu escopo sem atribuir um período não comprovado aos dados. A hierarquia MUST permanecer legível e preservar as métricas e os controles fora da troca da ação de exportação.

#### Scenario: Leitura da visão gerencial
- **WHEN** gerente ou administrador abre o dashboard com dados válidos
- **THEN** período, atualização, indicadores de vendas e seção de estoque MUST ser identificáveis, com até três colunas de KPIs e exportação Excel disponível como ação secundária

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
