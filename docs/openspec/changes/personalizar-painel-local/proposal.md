# Personalizar o painel localmente

## Contexto

A tela atual de Configurações não deve se tornar um CRUD de dados da empresa
nem exigir novas APIs. A proposta é usá-la para personalizações visuais e
individuais da experiência autenticada, mantendo os dados do Xano e as
permissões existentes inalterados.

## Escopo

- Manter a tela acessível somente a gerente/administrador.
- Permitir definir um nome de exibição local para a conta autenticada, sem
  alterar o nome ou o perfil cadastrados no Xano.
- Permitir selecionar tema escuro, claro ou automático (preferência do sistema),
  usando tema escuro como padrão.
- Permitir personalizar o título do Dashboard, a visibilidade e a ordem dos
  grupos de widgets existentes.
- Aplicar as preferências somente à apresentação dos dados já carregados pelo
  Dashboard; não criar métricas, widgets com dados fictícios ou chamadas novas.
- Salvar as preferências neste navegador, separadas por conta autenticada,
  com opção para restaurar os padrões.
- Aplicar os temas às telas autenticadas sem alterar a aparência da tela de login.

## Fora de escopo

- Notificações ou envio/agendamento de relatórios.
- Integrações, tokens ou configurações de API.
- Alterar nome, e-mail, cargo, senha, empresa ou permissões no Xano.
- Sincronizar preferências entre navegadores ou dispositivos.
- Criar novos widgets, endpoints ou fontes de dados.
- Alterar a aparência da tela de login ou implementar tradução.

## Critérios de aceitação

- Preferências podem ser editadas e restauradas sem chamadas de escrita ao
  Xano.
- O Dashboard mostra somente widgets existentes e preserva seus valores e
  filtros; ocultar um widget não altera os dados nem o resultado exportado.
- A ordem escolhida é refletida no Dashboard após recarregar a página.
- O nome personalizado é apenas um rótulo de exibição e não modifica a conta.
- As telas autenticadas aplicam o tema selecionado; o modo automático acompanha
  a preferência de cores do sistema operacional.
- Preferências de contas diferentes no mesmo navegador não se misturam.
- O tema escuro é o padrão; login, navegação, dados e fluxos existentes
  permanecem inalterados.
