## ADDED Requirements

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
