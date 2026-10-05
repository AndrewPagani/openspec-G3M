# integracao-xano Specification

## Purpose
Registra como a aplicação existente autentica operadores e consulta os grupos de API do Xano, incluindo os limites entre o comportamento implementado no cliente e a autorização que deve ser garantida pelo backend.

## Requirements

### Requirement: Chamadas da aplicação devem usar os grupos de API configurados
A aplicação MUST encaminhar chamadas de autenticação, cadastros, vendas, gerenciamento e webhooks aos respectivos grupos Xano configurados, permitindo substituir host e identificadores de grupo por configuração de ambiente.

#### Scenario: Roteamento para os grupos Xano
- **WHEN** um serviço da aplicação solicita uma rota conhecida, como `/clientes`, `/vendas` ou `/gerenciamento/indicadores`
- **THEN** a chamada MUST usar o grupo Xano configurado para aquela família de API e preservar o caminho da rota

### Requirement: Chamadas autenticadas devem transmitir a sessão
A aplicação MUST enviar o token retornado pelo login no cabeçalho Bearer para chamadas autenticadas e MUST tratar tokens já prefixados sem duplicar o esquema.

#### Scenario: Consulta autenticada
- **WHEN** um estado da aplicação chama o Xano com uma sessão válida
- **THEN** a requisição MUST conter `Authorization: Bearer <token>`

### Requirement: Erros do Xano devem ser apresentados como falha explícita
A aplicação MUST apresentar falhas de autenticação, autorização, respostas HTTP de erro e indisponibilidade sem tratá-las como sucesso ou substituir os dados por estatísticas fictícias.

#### Scenario: Xano recusa uma chamada
- **WHEN** o Xano responde com erro HTTP ou não pode ser alcançado
- **THEN** a aplicação MUST limpar ou preservar o estado conforme o fluxo da tela e MUST exibir uma mensagem de erro, sem inventar registros
