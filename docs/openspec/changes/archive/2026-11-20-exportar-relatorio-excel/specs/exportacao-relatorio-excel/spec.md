## Purpose

Permitir análise no Excel dos indicadores do Dashboard e dos registros operacionais autorizados ao operador.

## ADDED Requirements

### Requirement: Exportação reúne as áreas em um arquivo Excel

A ação **Exportar Excel** do Dashboard MUST entregar um único `.xlsx` com as abas Dashboard, Vendas, Clientes, Veículos e Peças. Usuários MUST aparecer somente para administradores autorizados. O arquivo MUST excluir Configurações. A aba Dashboard MUST incluir todos os indicadores, séries e detalhamentos autorizados que compõem o painel, inclusive widgets ocultados por preferência visual.

#### Scenario: Dashboard com todas as séries disponíveis
- **WHEN** o operador exporta um painel com dados válidos
- **THEN** o arquivo MUST incluir tabelas editáveis para indicadores, vendas por período, marca e categoria, formas de pagamento, mix de itens, estoque, peças com saldo baixo e detalhamentos por status e vendedor disponíveis ao perfil

#### Scenario: Área com resultado vazio válido
- **WHEN** uma área autorizada retorna uma lista válida sem registros
- **THEN** a aba MUST manter seus cabeçalhos e indicar ausência de registros

### Requirement: Relatório preserva o período aplicado e consulta todas as páginas autorizadas

O Dashboard MUST informar datas, agrupamento e filtros usados no relatório. Vendas MUST incluir todas as páginas do mesmo recorte das métricas de vendas, com datas, status, vendedor e forma de pagamento aplicáveis. Tipo de item e status do veículo MUST manter seu escopo nas séries de itens e no estoque, respectivamente. Clientes, Veículos, Peças e Usuários MUST incluir a coleção acessível de cada área, com identificação de seu escopo independente do período de vendas.

#### Scenario: Filtros alterados sem aplicação
- **WHEN** há filtros editados que ainda não foram aplicados ou o Dashboard está carregando
- **THEN** a ação MUST ficar indisponível até o Dashboard apresentar o resultado da consulta aplicada

#### Scenario: Coleções têm mais de uma página
- **WHEN** há vendas e cadastros autorizados além da primeira página
- **THEN** o arquivo MUST incluir todas as páginas do recorte correspondente e MUST incluir peças com saldo zero quando presentes na listagem autorizada

### Requirement: Abas e campos respeitam o acesso do operador

O relatório MUST usar o acesso concedido pelo Xano à sessão solicitante e exportar apenas campos operacionais aprovados de cada área. Vendedores MUST receber somente suas vendas. Credenciais, identificadores internos do ASAAS e links de cobrança MUST ficar fora do arquivo. Uma troca de identidade ou logout durante a geração MUST impedir a entrega do relatório à sessão seguinte.

#### Scenario: Exportação por vendedor
- **WHEN** um vendedor solicita a exportação
- **THEN** nenhuma venda de outro vendedor nem a aba Usuários MUST aparecer no arquivo

#### Scenario: Exportação por administrador autorizado
- **WHEN** o administrador exporta e o Xano autoriza a consulta de usuários
- **THEN** a aba Usuários MUST incluir identificação, nome, e-mail, perfil e data de cadastro disponíveis, sem campos de autenticação

### Requirement: Arquivo oferece dados próprios para análise e informa falhas

O arquivo MUST usar células numéricas para quantidades, percentuais e valores monetários, datas reconhecidas pelo Excel e texto para CPF, telefone e identificadores sujeitos à perda de zeros. Textos de origem externa MUST ser gravados como texto literal. A geração MUST indicar andamento e entregar o arquivo somente após concluir todas as consultas e abas esperadas.

#### Scenario: Falha após carregar parte da coleção
- **WHEN** uma aba autorizada falha em uma página ou retorna um formato inválido
- **THEN** a interface MUST identificar a área que falhou, permitir nova tentativa e impedir o download de um arquivo parcial como resultado completo

#### Scenario: Valores formatados e textos iniciados por sinais
- **WHEN** os dados incluem moeda, datas, documento com zero inicial ou texto que se parece com fórmula
- **THEN** o Excel MUST preservar os tipos e os zeros correspondentes e abrir o texto sem executá-lo como fórmula
