# integracao-xano Specification

## Purpose
Registra como a aplicação existente autentica operadores e consulta os grupos de API do Xano, incluindo os limites entre o comportamento implementado no cliente e a autorização que deve ser garantida pelo backend.

## Requirements

### Requirement: Consultas de vendas devem compartilhar o contrato de parâmetros
Toda chamada da aplicação a `GET /vendas`, incluindo consultas auxiliares na tela de clientes e páginas subsequentes, MUST enviar `page` e `per_page` como strings e `busca` como texto. Os filtros opcionais `cliente_id`, `vendedor_id`, `status_id`, `forma_pagamento_id`, `data_inicio` e `data_fim` MUST ser omitidos quando vazios e MUST preservar o valor selecionado quando preenchidos. A aplicação MUST NOT usar objetos ou o texto `{}` como sentinela de filtro vazio: o Xano declara esses inputs como JSON e pode decodificá-los como objetos incompatíveis com operações escalares. Este contrato padroniza a montagem da consulta GET, sem adicionar corpo JSON.

#### Scenario: Clientes consulta vendas em mais de uma página
- **WHEN** a tela de clientes consulta vendas para calcular atividade e pendências
- **THEN** cada página MUST enviar paginação e busca, omitir filtros opcionais vazios e alterar somente `page` ao avançar a paginação

#### Scenario: Operador filtra a listagem de vendas
- **WHEN** o operador informa busca, forma de pagamento ou datas
- **THEN** a consulta MUST enviar os valores informados e omitir os demais filtros vazios

#### Scenario: Filtros JSON opcionais não estão preenchidos
- **WHEN** clientes ou vendas consultam a listagem sem filtros
- **THEN** a URL MUST conter apenas `page`, `per_page` e `busca`, sem parâmetros com `{}` ou objetos vazios

### Requirement: Chamadas da aplicação devem usar os grupos de API configurados
A aplicação MUST encaminhar chamadas de autenticação, cadastros, vendas, gerenciamento e webhooks aos respectivos grupos Xano configurados, permitindo substituir host e identificadores de grupo por configuração de ambiente.

#### Scenario: Roteamento para os grupos Xano
- **WHEN** um serviço da aplicação solicita uma rota conhecida, como `/clientes`, `/vendas` ou `/gerenciamento/indicadores`
- **THEN** a chamada MUST usar o grupo Xano configurado para aquela família de API e preservar o caminho da rota

### Requirement: Chamadas autenticadas devem transmitir a sessão
A aplicação MUST enviar o token retornado pelo login no cabeçalho Bearer para chamadas autenticadas e MUST tratar tokens já prefixados sem duplicar o esquema.

#### Scenario: Consulta autenticada
- **WHEN** um estado da aplicação chama o Xano com uma sessão válida
- **THEN** a requisição MUST conter `Authorization: Bearer <token>`

### Requirement: Erros do Xano devem ser apresentados como falha explícita
A aplicação MUST apresentar falhas de autenticação, autorização, respostas HTTP de erro e indisponibilidade sem tratá-las como sucesso ou substituir os dados por estatísticas fictícias.

#### Scenario: Xano recusa uma chamada
- **WHEN** o Xano responde com erro HTTP ou não pode ser alcançado
- **THEN** a aplicação MUST limpar ou preservar o estado conforme o fluxo da tela e MUST exibir uma mensagem de erro, sem inventar registros
