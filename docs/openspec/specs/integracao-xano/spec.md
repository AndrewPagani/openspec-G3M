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

### Requirement: Catálogos de referência possuem reutilização limitada e atualização explícita

A aplicação MUST limitar a reutilização temporária de referências às formas de pagamento, status de veículos e áreas de veículos/peças, por ambiente e contexto autenticado. Uma resposta completa válida MUST ter validade máxima de cinco minutos; falhas ou respostas inválidas MUST NOT ser reutilizadas como sucesso. Atualização explícita MUST consultar novamente a fonte. Logout, troca de credencial e alteração local confirmada do catálogo MUST invalidar as entradas afetadas. Estoque, preços, clientes, veículos, vendas, pagamentos e indicadores MUST NOT receber esse cache de catálogo.

#### Scenario: Catálogo válido consultado novamente
- **WHEN** a mesma identidade consulta o mesmo catálogo no mesmo ambiente dentro da validade
- **THEN** a aplicação MUST reutilizar a resposta válida sem uma nova chamada remota, preservando IDs e rótulos, salvo atualização explícita

#### Scenario: Catálogo expirado ou atualização explícita
- **WHEN** a validade do catálogo termina ou o operador solicita sua atualização
- **THEN** a aplicação MUST fazer nova consulta e MUST NOT apresentar uma resposta expirada como confirmação atual se essa consulta falhar

#### Scenario: Credencial ou ambiente diferente
- **WHEN** outra identidade, credencial ou ambiente solicita o catálogo
- **THEN** a aplicação MUST NOT servir a entrada pertencente ao contexto anterior

### Requirement: Leituras independentes têm concorrência controlada sem repetir escritas

A aplicação MUST permitir que leituras independentes de uma tela avancem sem aguardar desnecessariamente umas pelas outras, com limite de três chamadas HTTP de leitura simultâneas por processo. Consumidores do mesmo catálogo no mesmo contexto MUST compartilhar uma leitura igual em andamento; a saída de um consumidor MUST NOT interromper o atendimento de outro consumidor válido. Essa otimização MUST preservar cabeçalhos, grupos, parâmetros, payloads e tratamento de erros existentes, e MUST NOT repetir ou paralelizar automaticamente operações de escrita.

#### Scenario: Vendas e formas de pagamento independentes
- **WHEN** a listagem de vendas termina enquanto as formas de pagamento ainda estão sendo consultadas
- **THEN** as vendas MUST aparecer e o filtro dependente do catálogo MUST indicar indisponibilidade temporária até receber opções válidas

#### Scenario: Duas telas solicitam a mesma referência
- **WHEN** dois consumidores válidos solicitam o mesmo catálogo e contexto antes de a primeira consulta terminar
- **THEN** a aplicação MUST realizar uma única leitura remota compartilhada e MUST preservar o atendimento do consumidor restante se o outro abandonar a consulta

#### Scenario: Muitas leituras independentes pendentes
- **WHEN** há mais de três leituras HTTP independentes prontas para execução no mesmo processo
- **THEN** a aplicação MUST respeitar o limite de três chamadas simultâneas sem perder o resultado ou erro de cada consumidor vigente

#### Scenario: Escrita recebe timeout
- **WHEN** criar uma venda, salvar um cadastro ou gerar um link recebe timeout
- **THEN** a otimização de leituras MUST NOT repetir a operação de escrita automaticamente e o tratamento existente de falha ou resultado incerto MUST ser preservado
