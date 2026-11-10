# Requisitos da interface interna

## ADDED Requirements

### Requirement: Barra lateral usa marca simplificada e não indica presença

A barra lateral MUST apresentar somente o selo G3M na área da marca e MUST NOT
apresentar os textos “AutoGestão” ou “GESTÃO AUTOMOTIVA” nessa área. O cartão
de usuário MUST apresentar avatar e nome/cargo, MUST NOT apresentar ponto
verde de presença ou o texto “On-line” e MUST manter a ação Sair.

#### Scenario: Renderização da barra lateral

- **WHEN** uma tela autenticada é exibida
- **THEN** a marca mostra G3M e o perfil mostra usuário/cargo e ação Sair sem
  indicador de presença
