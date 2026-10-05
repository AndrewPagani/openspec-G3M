## Purpose

Definir integridade e segurança do núcleo comercial sem pressupor tabelas ou campos de auditoria genérica não presentes no schema do MVP.

## ADDED Requirements

### Requirement: Validação de integridade e autorização no backend
Operações relacionadas a autenticação, autorização, estoque, vendas e status MUST ser validadas no backend. Registros MUST apontar apenas para entidades existentes. O backend MUST derivar vendedor da sessão, validar permissão por ação e rejeitar transições inválidas. Senhas, tokens, credenciais ASAAS, segredo de Webhook, PAN e CVV MUST NOT aparecer em respostas, logs ou mensagens de erro. A auditoria genérica persistente não faz parte do schema atual do MVP; eventos de pagamento devem usar a tabela `pagamento_evento` e o cancelamento deve registrar motivo/data nos campos próprios da venda.

#### Scenario: Operação não autorizada
- **WHEN** usuário sem permissão solicita ajuste de estoque, cancelamento pendente ou outra operação crítica
- **THEN** o backend MUST bloquear a execução sem alterar dados

#### Scenario: Venda com item inexistente ou vendedor forjado
- **WHEN** item aponta para entidade inexistente ou cliente envia `vendedor_id` diferente da sessão
- **THEN** o backend MUST rejeitar a requisição sem registrar venda nem reservar recursos

#### Scenario: Erro com dado sensível
- **WHEN** uma chamada falha contendo credenciais ou dados de cartão
- **THEN** respostas e logs MUST ser sanitizados e MUST NOT incluir esses dados

### Requirement: Operações críticas devem preservar consistência e idempotência
Reserva de veículo/peças, criação de venda, ajuste de estoque, cancelamento, expiração e processamento de Webhook MUST ser atômicos ou idempotentes conforme aplicável. Estoque disponível MUST NOT ficar negativo. A liberação de recursos MUST aguardar confirmação de que cobranças pendentes não podem mais ser pagas. Falhas em serviços externos MUST ser explícitas e não podem produzir resposta de sucesso nem estado local irreconciliável.

#### Scenario: Quantidade superior ao estoque
- **WHEN** vendas concorrentes tentam reservar mais peças que o saldo disponível
- **THEN** no máximo as unidades cobertas pelo saldo MUST ser reservadas e o estoque MUST NOT ficar negativo

#### Scenario: Cancelamento ou evento repetido
- **WHEN** cancelamento, expiração ou Webhook é processado mais de uma vez
- **THEN** o backend MUST aplicar baixa/liberação ou transição de estado no máximo uma vez

#### Scenario: Cancelamento externo inconclusivo
- **WHEN** ASAAS não confirma cancelamento de cobrança pendente
- **THEN** o backend MUST manter reserva e venda em estado recuperável e retornar pendência/falha explícita
