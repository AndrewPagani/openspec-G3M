# Tarefas

## 1. Especificar a experiência

- [x] 1.1 Definir tema compartilhado para telas autenticadas e preservar a
  identidade independente do login.
- [x] 1.2 Definir o uso de status reais do Xano e as cores semânticas de
  Disponível, Reservado e Vendido.
- [x] 1.3 Definir logout compartilhado com limpeza de sessão e redirecionamento.

## 2. Implementar no workspace local

- [x] 2.1 Aplicar shell e estilos internos compartilhados com navegação e
  apresentação adaptável.
- [x] 2.2 Carregar opções de status do Xano, selecionar status no formulário e
  compor payload de cadastro com status e URL opcional da imagem.
- [x] 2.3 Reutilizar o mapeamento de cores em formulário/listagem e gráfico de
  estoque, mantendo estilo neutro para valores desconhecidos.
- [x] 2.4 Fazer a ação Sair limpar os dados locais e retornar à tela de login.
- [x] 2.5 Adicionar testes para dados de veículo, cores de status, gráfico e
  encerramento de sessão.

## 3. Verificar e sincronizar

- [x] 3.1 Executar testes unitários, compilação Python e `git diff --check`.
- [ ] 3.2 Concluir exportação Reflex sem bloqueios de arquivos em uso no Windows.
- [ ] 3.3 Revisar a prévia completa do Xano e separar mudanças relacionadas de
  alterações preexistentes ou destrutivas.
- [ ] 3.4 Publicar alterações Xano somente após revisão e autorização explícita;
  até lá, manter os scripts apenas locais.
