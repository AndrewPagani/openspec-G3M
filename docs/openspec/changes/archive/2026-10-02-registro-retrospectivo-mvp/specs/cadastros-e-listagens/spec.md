## Purpose

Registra as telas de consulta e criação de clientes, veículos e peças atualmente implementadas e a apresentação resumida usada para identificar clientes e veículos nas listagens.

## ADDED Requirements

### Requirement: Listagem de clientes deve identificar nome e CPF
A listagem de clientes MUST apresentar o nome seguido do CPF no formato `Nome - CPF`, usando os campos devolvidos pela API do Xano.

#### Scenario: Cliente possui nome e CPF
- **WHEN** a API devolve um cliente com `CNome` e `CPF`
- **THEN** a linha do cliente MUST exibir `CNome - CPF`

### Requirement: Cartão de veículo deve apresentar imagem, nome, ano e preço
A listagem de veículos MUST apresentar marca/modelo, ano e preço; quando houver URL de imagem reconhecida na resposta do Xano, MUST apresentar a imagem, e quando não houver MUST exibir um estado substituto sem imagem.

#### Scenario: Veículo possui imagem
- **WHEN** a API devolve marca, modelo, ano, preço e URL de imagem do veículo
- **THEN** a listagem MUST apresentar a imagem, o nome formado por marca/modelo, o ano e o preço formatado em moeda brasileira

#### Scenario: Veículo não possui imagem
- **WHEN** a API devolve veículo sem URL de imagem
- **THEN** a listagem MUST manter nome, ano e preço e MUST informar que não há imagem cadastrada

### Requirement: Cadastro de veículo aceita URL opcional de imagem
O formulário de criação de veículo MUST oferecer campo opcional para URL da imagem, aceitar somente endereços HTTP ou HTTPS válidos no cliente e enviar o valor como `Imagem_url` quando informado.

#### Scenario: Envio de imagem válida
- **WHEN** um operador informa uma URL HTTP ou HTTPS válida e salva um veículo
- **THEN** a requisição de criação MUST incluir o campo `Imagem_url`

#### Scenario: URL inválida
- **WHEN** um operador informa valor que não é uma URL HTTP ou HTTPS válida
- **THEN** o formulário MUST rejeitar o envio e exibir um erro de validação

### Requirement: Formulários de cadastro devem validar campos locais antes do envio
Os formulários existentes de clientes, veículos e peças MUST validar a presença dos campos obrigatórios e os formatos numéricos/URL suportados antes de enviar os dados ao Xano; a validação no cliente não substitui a validação do backend.

#### Scenario: Campo obrigatório ausente
- **WHEN** um formulário é enviado sem um campo obrigatório
- **THEN** a aplicação MUST informar o campo ausente e MUST NOT enviar a requisição de criação
