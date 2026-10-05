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
