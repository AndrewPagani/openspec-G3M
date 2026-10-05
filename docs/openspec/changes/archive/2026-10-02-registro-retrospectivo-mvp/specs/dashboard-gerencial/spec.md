## Purpose

Registra o dashboard que consulta indicadores do endpoint Xano e apresenta KPIs e séries de vendas e estoque conforme o perfil e o contrato de resposta atualmente suportado pela aplicação.

## ADDED Requirements

### Requirement: Dashboard deve buscar dados reais do endpoint de indicadores
A tela MUST consultar `/gerenciamento/indicadores` com o token da sessão e o período selecionado, aceitar KPIs agrupados em `kpis` ou no nível superior e apresentar apenas valores retornados pelo Xano.

#### Scenario: Resposta válida de indicadores
- **WHEN** o Xano devolve indicadores em um dos formatos suportados
- **THEN** a tela MUST formatar valores monetários e percentuais e exibir os KPIs e séries presentes na resposta

#### Scenario: Resposta inválida ou chamada recusada
- **WHEN** o Xano não devolve os campos obrigatórios do perfil, retorna erro ou não pode ser alcançado
- **THEN** o dashboard MUST apresentar erro explícito, sem dados simulados

### Requirement: Dashboard deve oferecer filtro de período e filtros gerenciais opcionais
A tela MUST permitir selecionar datas inicial/final e oferecer a gerente/administrador filtros opcionais por status de venda, vendedor, forma de pagamento, tipo de item e status de veículo; filtros por ID MUST ser inteiros positivos.

#### Scenario: Gerente aplica filtros válidos
- **WHEN** gerente ou administrador preenche filtros válidos e atualiza o dashboard
- **THEN** a aplicação MUST enviar somente os filtros preenchidos junto ao período

#### Scenario: Datas ou filtros inválidos
- **WHEN** a data inicial é posterior à final, ou um filtro numérico/tipo de item possui valor inválido
- **THEN** a aplicação MUST rejeitar a consulta e apresentar uma mensagem de erro

### Requirement: Visibilidade do dashboard deve variar por perfil
Gerentes e administradores MUST receber as seções gerenciais apresentadas pela aplicação. Para vendedores, a interface MUST omitir filtros gerenciais e apresentar as áreas de indicadores e séries de vendas disponíveis para seu perfil. O escopo efetivo dos registros MUST ser aplicado pelo backend Xano e derivado da sessão autenticada; sua configuração publicada não foi verificada por este registro.

#### Scenario: Vendedor consulta o dashboard
- **WHEN** vendedor autenticado abre o dashboard
- **THEN** a interface MUST apresentar as áreas de vendas do perfil e MUST NOT enviar filtro de vendedor para ampliar ou substituir o escopo determinado pelo backend

#### Scenario: Gerente consulta o dashboard
- **WHEN** gerente ou administrador autenticado abre o dashboard
- **THEN** a interface MUST apresentar as seções de vendas, veículos e peças disponíveis na resposta autorizada do Xano

### Requirement: Séries sem registros devem ter estado vazio
A tela MUST indicar que uma série está sem dados quando o Xano retorna lista vazia ou não há registros no período, sem converter ausência em registros fictícios.

#### Scenario: Série vazia
- **WHEN** a resposta autorizada não contém registros em uma série
- **THEN** a seção correspondente MUST apresentar estado vazio legível
