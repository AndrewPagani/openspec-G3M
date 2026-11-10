# Requisitos de cadastro e listagem de veículos

## ADDED Requirements

### Requirement: Cadastro de veículo usa status reais do Xano

O formulário de veículo MUST carregar as opções disponíveis do Xano, permitir
selecionar um status existente e enviar o identificador selecionado no cadastro.
O formulário MUST NOT inventar opções ou IDs quando a consulta falhar; deve
exibir erro explícito e impedir o envio sem um status válido. A autorização e
validação do status MUST continuar sendo aplicadas pelo backend.

#### Scenario: Status disponíveis são carregados

- **WHEN** o endpoint de status retorna opções válidas
- **THEN** o formulário MUST apresentar as opções e enviar o ID selecionado ao
  criar o veículo

#### Scenario: Status não pode ser carregado

- **WHEN** a consulta de status falha ou não retorna opções válidas
- **THEN** o formulário MUST informar a falha e MUST NOT enviar um veículo com
  status inventado ou inválido

### Requirement: Status de veículo mantém cores semânticas consistentes

A interface MUST representar Disponível em verde, Reservado em amarelo e Vendido
em vermelho nos indicadores de status do formulário, dos cartões e do gráfico
de estoque. Status não reconhecidos MUST usar apresentação neutra.

#### Scenario: Status conhecido em qualquer indicador

- **WHEN** um badge, seletor ou gráfico recebe o status Disponível, Reservado
  ou Vendido
- **THEN** o indicador MUST usar respectivamente verde, amarelo ou vermelho

#### Scenario: Status desconhecido

- **WHEN** a API retorna status sem mapeamento semântico
- **THEN** o indicador MUST usar cor neutra sem atribuir incorretamente uma das
  cores dos status conhecidos
