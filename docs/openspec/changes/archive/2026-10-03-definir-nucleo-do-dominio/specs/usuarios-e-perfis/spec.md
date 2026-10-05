## Purpose

Definir usuários, perfis e autorização por ação no MVP usando cargos pré-definidos no backend, sem CRUD de permissões.

## ADDED Requirements

### Requirement: Usuários e perfis devem ser geridos com segurança
O sistema MUST permitir cadastrar e consultar usuários administrativos conforme o contrato aprovado; cadastro público, criação/edição de usuário pelo app, CRUD de permissões e autoalteração de perfil MUST NOT fazer parte do MVP. Credenciais MUST ser processadas pelo backend e nunca expostas. O sistema MUST suportar vendedor, gerente e administrador, com autorização aplicada no Xano por ação e recurso. A matriz mínima MUST permitir consulta de clientes, veículos e peças a todos os perfis; criação de cliente e venda a todos os perfis autorizados; desconto maior que zero, ajuste de estoque e cancelamento de cobrança pendente somente a gerente/administrador; gerenciamento de usuários/perfis somente ao administrador. Vendedor MUST consultar apenas suas próprias vendas. Estorno de venda paga MUST NOT ser permitido no MVP.

#### Scenario: Login válido e consulta da sessão
- **WHEN** usuário com credenciais válidas autentica e consulta a própria sessão
- **THEN** o backend MUST retornar token, usuário e perfil sem expor senha

#### Scenario: Credencial inválida
- **WHEN** usuário envia credenciais inválidas
- **THEN** o backend MUST rejeitar com mensagem genérica que não confirme a existência do e-mail

#### Scenario: Ação reservada a gerente ou administrador
- **WHEN** vendedor tenta aplicar desconto, ajustar estoque ou cancelar cobrança pendente
- **THEN** o backend MUST rejeitar a operação sem alterar dados

#### Scenario: Vendedor consulta vendas
- **WHEN** vendedor solicita lista ou detalhe de vendas
- **THEN** o backend MUST limitar os resultados às vendas associadas à sua sessão, ignorando ou rejeitando `vendedor_id` forjado

#### Scenario: Administração de usuários
- **WHEN** usuário sem perfil administrador solicita consulta administrativa de usuários
- **THEN** o backend MUST rejeitar a operação
