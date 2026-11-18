# Design

## Decisões

- Remover a rota Reflex `/auditoria` e o item correspondente da navegação local.
  Não alterar o endpoint remoto distinto `auditoria_parcelas`.
- Remover os atalhos de criação do Dashboard e seus controles nas Configurações.
- Ignorar o campo `shortcuts` de preferências locais antigas para manter a
  compatibilidade com dados já salvos no navegador.
- Preservar as rotas de cadastro e suas autorizações; nenhum endpoint ou fluxo
  de dados muda.

## Verificação

- Executar a suíte de testes Python.
- Gerar o build do frontend Reflex.
- Confirmar que não há referências locais à página de Auditoria nem aos
  componentes de atalhos removidos e executar `git diff --check`.
