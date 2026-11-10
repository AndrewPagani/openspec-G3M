# Design: Padronização de telas e ajustes de veículos

## Contexto

O app usa Python/Reflex e Xano. A tela de login deve continuar independente do
tema autenticado. As telas internas usam o shell comum; veículos e seus status
devem continuar baseados nos dados recebidos do Xano, sem IDs ou registros de
negócio fixos no frontend.

## Decisões

### Tema compartilhado, login isolado

- Centralizar layout de navegação autenticada no shell existente e estilos
  internos em seletores delimitados pelo shell.
- Usar a paleta escura azul-marinho/ciano e componentes com bordas sutis,
  hierarquia tipográfica legível e adaptação a larguras menores.
- Não aplicar regras do tema interno aos componentes de login.

### Status de veículo dirigido pelo Xano

- Buscar opções de status no endpoint de status de veículos; não assumir IDs
  estáticos e não substituir uma resposta indisponível por opções fictícias.
- Enviar o ID selecionado no cadastro e preservar a validação/autorização do
  backend como autoridade.
- Reutilizar um mapeamento semântico único: Disponível em verde, Reservado em
  amarelo, Vendido em vermelho e valores desconhecidos em neutro.
- Aplicar a semântica nos badges de listagem/formulário e nas cores do gráfico
  de estoque.
- Continuar aceitando URL opcional de imagem hospedada; não implementar upload
  local nesta change.

### Encerramento da sessão

- Manter um único evento de logout compartilhado pelo shell autenticado.
- Limpar token e dados de perfil guardados no estado/local storage, além dos
  campos transitórios de autenticação.
- Retornar um redirecionamento explícito para `/login` depois da limpeza, sem
  depender da tela atual ou do sucesso de uma chamada ao Xano.

## Verificação

- Testes unitários para logout, seleção/persistência de status, normalização e
  cores semânticas.
- Testes do estado do dashboard para a cor correspondente a cada status.
- Compilação Python, exportação Reflex e `git diff --check`.
- Revisão de `workspace push --dry-run` como etapa separada; não publicar se a
  prévia incluir operações destrutivas ou objetos não relacionados.

## Riscos e questões operacionais

- O endpoint de status ou sua resposta pode não estar disponível; mostrar erro
  explícito e impedir o envio sem uma opção válida.
- A prévia local do Xano pode conter alterações preexistentes não relacionadas.
  Nenhuma publicação remota é autorizada por esta change.
- No Windows, processos Reflex/npm podem bloquear arquivos em `.web`; uma falha
  de limpeza (`EBUSY`) deve ser diferenciada de uma falha de compilação do app.
