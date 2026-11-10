# Requisitos de sessão de usuários

## ADDED Requirements

### Requirement: Logout encerra sessão local e navega ao login

O evento de logout MUST limpar token e dados locais do usuário e MUST
redirecionar para a tela `/login`, independentemente da tela autenticada que
originou a ação.

#### Scenario: Logout em qualquer módulo

- **WHEN** o usuário aciona a ação compartilhada Sair em um módulo autenticado
- **THEN** a sessão local MUST ser limpa e a aplicação MUST navegar para
  `/login`

#### Scenario: Logout sem disponibilidade do Xano

- **WHEN** o usuário aciona Sair enquanto o Xano está indisponível
- **THEN** o logout local MUST ser concluído sem depender de comunicação com o
  Xano
