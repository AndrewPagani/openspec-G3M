# Requisitos de interface interna

## ADDED Requirements

### Requirement: Telas autenticadas compartilham o tema visual interno

As telas autenticadas MUST usar uma estrutura visual compartilhada, com tema
escuro profissional, navegação consistente, tipografia legível e componentes
adaptáveis ao viewport. O tema MUST NOT alterar a identidade visual da tela de
login.

#### Scenario: Usuário navega entre telas internas

- **WHEN** o usuário navega entre módulos autenticados
- **THEN** a navegação e a identidade visual interna MUST permanecer
  consistentes e a opção correspondente à tela atual MUST indicar o estado
  ativo

#### Scenario: Tela interna em viewport estreito

- **WHEN** uma tela autenticada é aberta em viewport estreito
- **THEN** seu conteúdo MUST adaptar o layout sem ocultar ações ou campos
  essenciais

#### Scenario: Login permanece visualmente isolado

- **WHEN** a tela de login é apresentada
- **THEN** estilos e componentes exclusivos do shell autenticado MUST NOT
  alterar sua identidade visual

### Requirement: A ação de sair funciona em todas as telas autenticadas

O shell autenticado MUST disponibilizar uma ação de saída que limpe o token e
os dados de usuário da sessão local e redirecione para `/login`, sem depender
do módulo atual ou de uma chamada ao Xano.

#### Scenario: Sair de uma tela autenticada

- **WHEN** o usuário aciona Sair em qualquer tela autenticada
- **THEN** a aplicação MUST limpar token, perfil e nome de usuário da sessão
  local e MUST redirecionar para `/login`

#### Scenario: Sair com formulário ou mensagem transitória preenchida

- **WHEN** o usuário aciona Sair enquanto existem campos ou mensagens
  transitórias de autenticação preenchidos
- **THEN** a aplicação MUST limpar esses valores junto com a sessão e concluir
  o redirecionamento
