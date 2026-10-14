# Proposta: Padronização de telas e ajustes de veículos

## Por que

As telas internas precisam compartilhar uma identidade visual consistente sem
alterar a identidade própria do login. O cadastro e a apresentação de veículos
também precisam refletir os status reais do Xano de forma uniforme, e o usuário
deve conseguir encerrar a sessão a partir de qualquer tela autenticada.

## O que muda

- Aplicar um tema escuro profissional, navegação e estilos compartilhados às
  telas internas, mantendo a tela de login isolada.
- Padronizar painéis, formulários, cartões, controles e comportamento responsivo
  sem introduzir dados simulados.
- Carregar os status disponíveis de veículos do Xano, permitir selecionar o
  status no cadastro e enviar o identificador selecionado junto aos dados do
  veículo e à URL opcional da imagem.
- Usar cores semânticas consistentes para Disponível, Reservado e Vendido nos
  formulários, cartões e gráfico de estoque; status desconhecidos permanecem
  neutros.
- Fazer a ação compartilhada de sair limpar os dados locais da sessão e
  redirecionar para o login em todas as telas autenticadas.

## Fora do escopo

- Alterar o visual da tela de login ou adicionar autenticação de novos tipos.
- Publicar automaticamente scripts ou alterações no workspace remoto do Xano.
- Remover ou renomear campos/dados existentes no Xano, nem aprovar mudanças
  remotas que impliquem operações destrutivas.
- Adicionar upload de arquivo de imagem; o formulário usa URL hospedada.

## Capabilities

### Novas

- `interface-interna`: identidade visual compartilhada para telas autenticadas.

### Modificadas

- `cadastros-e-listagens`: cadastro, apresentação e cores semânticas dos
  status de veículos.
- `integracao-xano`: leitura dos status e persistência do status/imagem no
  contrato de veículos.
- `usuarios-e-perfis`: encerramento previsível da sessão autenticada.

## Impacto

- Interface Reflex compartilhada em `app/components/app_shell.py` e estilos
  internos em `assets/styles.css`.
- Formulário e estados de veículos em `app/pages/simple.py`,
  `app/state/form_state.py` e `app/state/resource_state.py`.
- Mapeamento semântico de status em `app/services/vehicle_status.py`,
  `app/pages/resource.py` e no gráfico de `app/pages/gerenciamento.py`.
- Logout centralizado em `app/state/auth_state.py`.
- Contrato local dos endpoints Xano de veículos, especificações OpenSpec e
  testes correspondentes.

O contrato local do Xano deve ser revisado integralmente antes de qualquer
publicação. Uma prévia com operações destrutivas ou mudanças não relacionadas
não deve ser publicada como parte desta change.
