## Requisitos

### Requisito: Personalização local do Dashboard

A aplicação MUST permitir que gerente ou administrador personalize, por conta,
o nome de exibição local, o tema, o título do Dashboard, a visibilidade e ordem
dos grupos de widgets existentes. As preferências MUST ser persistidas somente
no navegador e separadas por conta.
Elas MUST NOT alterar os dados, consultas, filtros, exportação, autorização ou
cadastro no Xano. A aplicação MUST manter valores padrão e permitir restaurá-los.

### Requisito: Tema consistente nas telas autenticadas

A aplicação MUST oferecer os modos escuro, claro e automático conforme a
preferência de cores do sistema operacional. O modo escuro MUST ser o padrão.
O tema MUST ser aplicado consistentemente às telas autenticadas, incluindo
navegação, formulários, tabelas, diálogos e gráficos. A tela de login MUST
manter sua aparência atual. Cores semânticas de sucesso, alerta, erro e séries
de gráficos MUST continuar distinguíveis e legíveis em todos os modos.

#### Cenário: Selecionar tema manualmente

- **WHEN** gerente ou administrador seleciona claro ou escuro
- **THEN** todas as telas autenticadas MUST aplicar o modo selecionado sem
  alterar os dados, o comportamento ou a aparência da tela de login

#### Cenário: Seguir a preferência do sistema

- **WHEN** o usuário seleciona o modo automático
- **THEN** as telas autenticadas MUST acompanhar a preferência atual do sistema
  operacional e atualizar a aparência quando essa preferência mudar

#### Cenário: Persistência da aparência

- **WHEN** o usuário salva uma preferência de tema e recarrega ou navega entre
  telas
- **THEN** o modo escolhido MUST permanecer aplicado para a conta no navegador
  atual

#### Cenário: Legibilidade e cores semânticas

- **WHEN** qualquer modo de tema é aplicado a uma tela autenticada
- **THEN** texto, campos, controles, gráficos e tooltips MUST permanecer
  legíveis e as cores semânticas MUST manter seus significados

#### Cenário: Aplicar preferências

- **WHEN** gerente ou administrador salva preferências válidas e abre o Dashboard
- **THEN** a interface MUST aplicar o título, a ordem e a visibilidade dos
  componentes já existentes, sem criar dados ou chamadas de API

#### Cenário: Ocultar um widget

- **WHEN** o usuário oculta um grupo de widgets
- **THEN** a interface MUST ocultar somente sua apresentação e MUST preservar
  os dados retornados, filtros e exportação existentes

#### Cenário: Preferências locais e isolamento por conta

- **WHEN** a mesma instalação do navegador é usada por contas diferentes
- **THEN** cada conta MUST receber somente suas próprias preferências locais;
  os valores MUST NOT ser apresentados como sincronizados com outros dispositivos

#### Cenário: Restaurar padrão

- **WHEN** o usuário solicita restaurar a configuração padrão
- **THEN** a aplicação MUST restaurar o nome da conta como nome de exibição, o
  título, os widgets e sua ordem

#### Cenário: Perfil sem acesso às configurações

- **WHEN** um usuário que não seja gerente ou administrador abre a tela
- **THEN** a restrição de acesso existente MUST ser preservada
