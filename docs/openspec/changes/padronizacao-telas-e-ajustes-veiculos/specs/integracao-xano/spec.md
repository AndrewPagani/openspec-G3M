# Requisitos da integração Xano para veículos

## ADDED Requirements

### Requirement: Cadastro persiste o status e a imagem informados

O cliente MUST enviar o identificador do status selecionado e, quando
informada, a URL HTTP ou HTTPS da imagem no cadastro de veículo. As respostas
de listagem e detalhe MUST disponibilizar a URL persistida para apresentação
do veículo. A ausência de imagem MUST permanecer válida.

#### Scenario: Cadastro com status e imagem

- **WHEN** o usuário cadastra um veículo com status existente e URL válida
- **THEN** a requisição MUST incluir status e URL e as consultas do veículo
  MUST retornar a imagem persistida

#### Scenario: Cadastro sem imagem

- **WHEN** o usuário cadastra um veículo sem URL de imagem
- **THEN** o cadastro MUST continuar válido e as telas MUST apresentar estado
  substituto para a imagem ausente
