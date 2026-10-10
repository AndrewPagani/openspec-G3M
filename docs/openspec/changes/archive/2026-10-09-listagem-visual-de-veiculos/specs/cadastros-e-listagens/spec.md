## MODIFIED Requirements

### Requirement: Cartão de veículo deve apresentar imagem, nome, ano e preço
A listagem de veículos MUST carregar todas as páginas de resultados disponíveis
e apresentar cartões em três colunas em telas amplas, com menos colunas em
telas menores. Cada cartão MUST apresentar imagem retangular em destaque (ou
um estado substituto quando não houver imagem), marca/modelo, ano,
quilometragem em quilômetros e preço. A consulta de veículos MUST continuar
suportando paginação e filtros de busca, marca, modelo e status.

#### Scenario: Veículo possui imagem e quilometragem
- **WHEN** a API devolve marca, modelo, ano, quilometragem, preço e URL de
  imagem do veículo
- **THEN** a listagem MUST apresentar a imagem, o nome formado por
  marca/modelo, o ano, a quilometragem e o preço formatado em moeda brasileira

#### Scenario: Veículo possui imagem
- **WHEN** a API devolve marca, modelo, ano, preço e URL de imagem do veículo
- **THEN** a listagem MUST apresentar a imagem, o nome formado por
  marca/modelo, o ano e o preço formatado em moeda brasileira

#### Scenario: Veículo não possui imagem ou quilometragem
- **WHEN** a API devolve veículo sem URL de imagem ou sem quilometragem
- **THEN** a listagem MUST manter o nome, ano e preço e MUST exibir estados
  substitutos para imagem ou quilometragem não informadas

#### Scenario: Veículo não possui imagem
- **WHEN** a API devolve veículo sem URL de imagem
- **THEN** a listagem MUST manter nome, ano e preço e MUST informar que não
  há imagem cadastrada

#### Scenario: Existem mais veículos do que cabem em uma página
- **WHEN** a resposta paginada informa mais de uma página de veículos
- **THEN** a aplicação MUST carregar todas as páginas informadas antes de
  apresentar a lista como completa

#### Scenario: Grade de cartões em diferentes larguras
- **WHEN** a listagem é exibida em tela ampla ou estreita
- **THEN** a grade MUST apresentar três colunas em telas amplas e reduzir para
  duas ou uma coluna conforme o viewport

### Requirement: Cadastro de veículo aceita URL opcional de imagem
O schema de veículo MUST persistir a URL de imagem no campo opcional
`imagem_url`. Os endpoints de criação, consulta individual, atualização e
listagem MUST aceitar ou devolver a chave de API `Imagem_url` e mapeá-la para
o campo persistido, para que a imagem cadastrada esteja disponível no cartão.
O formulário MUST aceitar somente endereços HTTP ou HTTPS válidos no cliente
e enviar `Imagem_url` quando informado; registros sem imagem continuam
válidos.

#### Scenario: Imagem de veículo persistida e consultada
- **WHEN** um veículo é cadastrado ou atualizado com uma URL HTTP ou HTTPS
  válida
- **THEN** os endpoints de consulta individual e listagem MUST devolver
  `Imagem_url` para o registro

#### Scenario: Envio de imagem válida
- **WHEN** um operador informa uma URL HTTP ou HTTPS válida e salva um veículo
- **THEN** a requisição de criação MUST incluir o campo `Imagem_url`

#### Scenario: URL inválida
- **WHEN** um operador informa valor que não é uma URL HTTP ou HTTPS válida
- **THEN** o formulário MUST rejeitar o envio e exibir um erro de validação

#### Scenario: Veículo com identificador duplicado
- **WHEN** placa ou chassi já informado está associado a outro veículo
- **THEN** o backend MUST rejeitar a criação ou atualização sem alterar o
  registro existente
