## MODIFIED Requirements

### Requirement: Chamadas da aplicação devem usar os grupos de API configurados
A aplicação MUST encaminhar chamadas de autenticação, cadastros, vendas e gerenciamento aos respectivos grupos Xano configurados, permitindo substituir host e identificadores de grupo por configuração de ambiente. O fluxo de pagamentos MUST usar somente endpoints autenticados do grupo de vendas para ler parcelas e registrar baixas manuais. A aplicação MUST NOT chamar grupos de Webhook, gateways ou serviços de processamento de pagamentos.

#### Scenario: Roteamento para os grupos Xano
- **WHEN** um serviço solicita login, cadastro, venda ou indicador
- **THEN** a chamada MUST usar o grupo Xano configurado para a família da rota e preservar o caminho

#### Scenario: Pagamentos registrados localmente
- **WHEN** a aplicação carrega parcelas ou registra uma baixa manual autorizada
- **THEN** MUST persistir os dados exclusivamente via API do Xano e MUST NOT iniciar chamada externa de pagamento
