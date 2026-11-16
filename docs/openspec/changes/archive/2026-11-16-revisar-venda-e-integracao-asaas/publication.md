# Evidência de publicação — 14/11/2026

Usuário autorizou explicitamente habilitação e publicação do pacote
`xanoscript/asaas-sales/` em `147643/v1`.

1. Nova leitura prévia: `.codex-tmp/pre-publicacao-venda-asaas/`, 64 documentos.
   As 13 definições existentes do pacote coincidiam com a baseline revisada;
   nenhum dos 4 novos nomes estava presente no remoto.
2. Dry-run repetiu o escopo autorizado: 1 tabela criada, 3 tabelas atualizadas,
   3 funções novas e 8 endpoints atualizados.
3. Tentativa autorizada `workspace edit --allow-push` retornou HTTP 500:
   `Allow Push is not available on the Free plan. Push is always enabled for Free plan workspaces.`
   O campo false exibido na consulta não era bloqueio nesse plano. Não houve
   alteração de plano nem de configuração de publicação.
4. `workspace push --workspace 147643 --branch v1 --directory xanoscript/asaas-sales`,
   com confirmação interativa já autorizada: **Pushed 15 documents** e
   **Synced 4 GUIDs to local files**. Transação padrão mantida.
5. Leitura posterior confirmou código novo, mas descrições antigas dos endpoints
   de link/webhook permaneciam. Foram corrigidas; dry-run mostrou esses 2 endpoints.
   Novo push com `--writeback`: **Pushed 2 documents**, **Wrote 2 formatted files**.
6. Leitura final: `.codex-tmp/pos-publicacao-venda-asaas-final/`, 68 documentos.
   Dry-run final com mesmo pacote/destino: **No changes to push**.

Não utilizados `--force`, `--delete`, `--truncate`, `--records`, `--env` ou
`--no-transaction`. Não foram lidos valores de segredos nem criados clientes,
cobranças, pagamentos ou webhooks de configuração. A publicação altera definições
e schema; não valida comportamento financeiro, autorização ou concorrência.

O gerador agora preserva os GUIDs atribuídos aos novos objetos ao regenerar na
mesma saída; Ruff de sintaxe/imports/erros passou após esse ajuste. O pacote atual
inclui as versões formatadas pelo servidor dos dois endpoints finais.

Próximo passo operacional: configurar e validar o Sandbox conforme deployment.md.
Tasks 4.4/4.5 permanecem pendentes quanto à configuração e execução autenticada.
