# Requisitos do dashboard gerencial

## ADDED Requirements

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
