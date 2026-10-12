# Dashboard gerencial — delta da mudança

## Adicionado

### Requirement: Dashboard apresenta indicadores em painel responsivo
O dashboard MUST organizar filtros, KPIs, séries temporais e análises
autorizadas em cartões e grades responsivas. MUST apresentar estados
compreensíveis de carregamento, erro e ausência de dados.

#### Scenario: Usuário gerente abre o dashboard
- **WHEN** gerente ou administrador abre o dashboard
- **THEN** o sistema MUST apresentar os KPIs autorizados, a evolução de
  vendas, os pagamentos, o mix de itens e as análises de estoque retornadas
  pelo Xano em uma grade responsiva

### Requirement: Série temporal suporta granularidade selecionável
A aplicação MUST oferecer dia, semana, mês e ano. Ao alterar a granularidade,
MUST consultar novamente o endpoint de indicadores autenticado existente e
agrupar a série diária que ele retorna por data, semana ISO, mês ou ano. A
visualização MUST usar somente as métricas presentes na resposta.

#### Scenario: Usuário seleciona uma granularidade
- **WHEN** o usuário seleciona dia, semana, mês ou ano
- **THEN** o dashboard MUST atualizar a série a partir dos indicadores
  autorizados pelo Xano, sem inventar uma divisão de faturamento por tipo de
  item

### Requirement: Dashboard oferece exportação local dos KPIs
O dashboard MUST permitir exportar em CSV os KPIs exibidos e o intervalo de
datas selecionado, sem iniciar requisição adicional ou incluir credenciais.

#### Scenario: Usuário exporta o resumo
- **WHEN** o usuário aciona a exportação
- **THEN** a aplicação MUST baixar um CSV com os valores atuais do dashboard e
  o intervalo consultado

### Requirement: Integração do dashboard é assíncrona e autenticada
O servidor Reflex MUST consultar o endpoint de indicadores com cliente HTTP
assíncrono e o token da sessão. O token MUST permanecer no estado de
autenticação e MUST NOT ser copiado para estado público do dashboard.

#### Scenario: Consulta autenticada
- **WHEN** o dashboard busca indicadores
- **THEN** a requisição MUST enviar o token da sessão ao endpoint Xano por
  chamada assíncrona e apresentar explicitamente respostas recusadas ou
  indisponibilidade

### Requirement: Indicadores fora do contrato não são simulados
Indicadores que necessitam de dimensões não fornecidas pelo contrato/schema
atual MUST ser identificados como indisponíveis, sem dados fixos, estimativas
ou substitutos com rótulos enganosos. Pagamentos MUST ser descritos como
contagens quando o endpoint só fornecer quantidades. O ticket MUST manter o
significado da métrica agregada devolvida pelo Xano.

#### Scenario: Métrica exige dado ausente no Xano
- **WHEN** a métrica requer propostas, histórico de entrada/saída de estoque,
  marca vendida, categoria/fabricante de peça ou canal de venda não disponível
- **THEN** o dashboard MUST informar que a métrica não é fornecida pelo
  endpoint atual e MUST NOT inferir um resultado

#### Scenario: Método de pagamento só possui contagem
- **WHEN** a API devolve quantidade de vendas por forma, mas não valor
  recebido por forma
- **THEN** o gráfico MUST apresentar distribuição por quantidade e MUST NOT
  apresentar essa quantidade como valor financeiro

#### Scenario: Série diária possui granularidade maior
- **WHEN** o usuário escolhe semana, mês ou ano
- **THEN** o dashboard MUST agrupar os pontos diários por calendário ISO,
  mês ou ano, respectivamente, sem alterar os dados recebidos
