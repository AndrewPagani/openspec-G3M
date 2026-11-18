## ADDED Requirements

### Requirement: Auditoria genérica não é exposta na interface local

A aplicação local MUST NOT registrar nem expor a rota genérica `/auditoria`,
pois não há endpoint local correspondente no MVP. Esta remoção MUST NOT ser
interpretada como alteração do endpoint remoto distinto
`/auditoria_parcelas`.

#### Scenario: Navegação autenticada

- **WHEN** gerente ou administrador navega pelas telas autenticadas
- **THEN** a navegação MUST NOT apresentar uma opção de Auditoria

#### Scenario: Acesso direto à rota genérica

- **WHEN** um usuário tenta abrir `/auditoria` na aplicação local
- **THEN** a aplicação MUST NOT carregar a página genérica de Auditoria

