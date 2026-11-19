# interface-interna Specification

## Purpose
Define os padrões da interface interna para marca e identificação do operador, navegação entre telas e apresentação de dados vinculados à consulta e à conta atuais, incluindo carregamento e descarte de respostas obsoletas.

## Requirements

### Requirement: Barra lateral usa marca simplificada e não indica presença

A barra lateral MUST apresentar somente o selo G3M na área da marca e MUST NOT
apresentar os textos “AutoGestão” ou “GESTÃO AUTOMOTIVA” nessa área. O cartão
de usuário MUST apresentar avatar e nome/cargo, MUST NOT apresentar ponto
verde de presença ou o texto “On-line” e MUST manter a ação Sair.

#### Scenario: Renderização da barra lateral

- **WHEN** uma tela autenticada é exibida
- **THEN** a marca mostra G3M e o perfil mostra usuário/cargo e ação Sair sem
  indicador de presença

### Requirement: Navegação apresenta somente conteúdo correspondente à consulta atual

A interface MUST associar os resultados exibidos à conta autenticada, ao recurso, ao identificador de detalhe e aos filtros da consulta atual. Ao trocar de recurso ou detalhe, MUST apresentar o estado inicial de carregamento antes de esperar a resposta remota e MUST NOT mostrar registros, erros ou ações vinculados à consulta incompatível anterior. Busca e paginação de um recurso MUST NOT alterar as de outro recurso.

#### Scenario: Troca de veículos para peças com rede pendente
- **WHEN** o operador abre Peças após consultar Veículos e a resposta de peças ainda não chegou
- **THEN** a tela MUST identificar Peças e seu carregamento e MUST NOT apresentar cartões ou links dos veículos anteriores

#### Scenario: Busca restrita ao recurso
- **WHEN** o operador pesquisa um nome em Clientes e abre Veículos
- **THEN** a busca de Clientes MUST NOT ser aplicada à listagem de Veículos

#### Scenario: Mudança de identificador em detalhe
- **WHEN** o operador abre outro cliente, veículo ou venda e sua consulta está pendente
- **THEN** o detalhe anterior MUST NOT ser apresentado como se pertencesse ao novo identificador

### Requirement: Leituras demoradas preservam a interação e descartam resultados obsoletos

Durante uma leitura remota demorada, a interface MUST permitir navegar e processar outra interação independente da sessão, com estado de carregamento perceptível e controles identificados. Se rota, conta ou parâmetros mudarem, resultados, erros e finalizações da consulta anterior MUST NOT substituir o estado da consulta vigente. Atualizações anteriores a uma alteração confirmada de dados MUST NOT restaurar a versão antiga da entidade.

#### Scenario: Operador abandona uma leitura lenta
- **WHEN** Clientes está aguardando rede e o operador abre Vendas
- **THEN** a navegação para Vendas MUST ser processada antes de terminar a leitura de Clientes e a resposta posterior de Clientes MUST NOT modificar a tela de Vendas

#### Scenario: Respostas chegam fora de ordem
- **WHEN** uma busca nova termina antes de uma busca anterior
- **THEN** os registros e o estado de carregamento da busca nova MUST permanecer vigentes mesmo após a resposta ou falha da busca anterior

#### Scenario: Registro alterado durante uma leitura
- **WHEN** uma alteração é confirmada depois do início de uma leitura antiga da mesma entidade
- **THEN** a conclusão dessa leitura antiga MUST NOT restaurar os dados anteriores à alteração

### Requirement: Consulta de outra conta não reutiliza dados operacionais anteriores

Logout e troca de identidade MUST invalidar as consultas pendentes e os dados operacionais de apresentação da identidade anterior. Rascunhos e informações de confirmação de venda MUST seguir o fluxo existente durante a navegação dentro da mesma conta e MUST NOT ser expostos a outra conta. Preferências locais por conta MUST continuar seguindo a personalização existente.

#### Scenario: Outra conta entra no mesmo navegador
- **WHEN** um operador sai e outra conta entra enquanto uma leitura anterior ainda está pendente
- **THEN** a conta nova MUST NOT receber registros, erros, rascunhos ou resultados dessa leitura e suas preferências próprias MUST ser preservadas

#### Scenario: Falha de link após venda criada
- **WHEN** uma venda foi criada e a geração do link falha
- **THEN** a navegação e os estados de carregamento MUST preservar a identificação da venda conforme o fluxo existente e MUST NOT disparar nova criação automática para tentar recuperar o link
