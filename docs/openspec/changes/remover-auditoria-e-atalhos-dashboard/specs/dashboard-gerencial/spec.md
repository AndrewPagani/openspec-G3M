## ADDED Requirements

### Requirement: Dashboard não apresenta atalhos de criação

O Dashboard MUST NOT apresentar atalhos para criação de cliente, veículo ou
venda. As Configurações MUST NOT oferecer controles para ativar esses atalhos.
As rotas de cadastro existentes MUST manter sua disponibilidade e autorização
atuais, independentemente dos atalhos removidos.

#### Scenario: Dashboard carregado

- **WHEN** um usuário autorizado abre o Dashboard
- **THEN** a tela MUST NOT apresentar os atalhos “Novo cliente”, “Novo veículo”
  ou “Nova venda”

#### Scenario: Preferências locais antigas

- **WHEN** as preferências salvas no navegador contêm a seleção antiga de atalhos
- **THEN** a aplicação MUST carregar as demais preferências sem erro e MUST NOT
  renderizar os atalhos

#### Scenario: Acesso aos cadastros

- **WHEN** o usuário navega até uma rota de cadastro existente
- **THEN** as permissões e o comportamento da rota MUST permanecer inalterados
