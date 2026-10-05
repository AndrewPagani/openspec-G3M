# Esquema XanoScript do MVP

O arquivo [`mvp-schema.xs`](./mvp-schema.xs) é um bundle com todas as tabelas
do MVP. Os documentos são separados por `---`, formato aceito pelo comando
`xano flatten`.

## Publicação pelo Xano CLI

1. Autentique o CLI:

   ```powershell
   xano auth
   ```

2. Confira quais arquivos serão gerados, sem alterar nada:

   ```powershell
   xano flatten .\xanoscript\mvp-schema.xs --dry-run
   ```

3. Gere a estrutura de arquivos que o `workspace push` utiliza, preservando o
   bundle original:

   ```powershell
   xano flatten .\xanoscript\mvp-schema.xs --keep-source -o .\xanoscript\workspace
   ```

4. Faça primeiro uma prévia da publicação:

   ```powershell
   xano workspace push --dry-run -d .\xanoscript\workspace -w <WORKSPACE_ID>
   ```

5. Depois de revisar a prévia, publique o esquema:

   ```powershell
   xano workspace push -d .\xanoscript\workspace -w <WORKSPACE_ID>
   ```

O script não inclui registros iniciais. Após a criação das tabelas, cadastre
os perfis fixos, status, áreas de peças e formas de pagamento por seed
ou pela interface do Xano.

## Migração ASAAS publicada

O workspace `147643` contém as 11 tabelas base e as duas tabelas de pagamento.
`asaas-payment-migration.xs` adiciona os campos de integração e as tabelas
`pagamento` e `pagamento_evento`. Ela também acrescenta `cliente.Email`, que
estava ausente no schema base; o campo fica anulável para preservar registros
existentes, mas as APIs devem exigi-lo em novos cadastros.

O push foi concluído; o CLI alertou sobre três FKs de `venda`, mas a leitura
posterior do workspace confirmou que apontam para as tabelas existentes
`user`, `forma_pagamento` e `status_venda`. Para reproduzir a prévia:

```powershell
xano flatten .\xanoscript\asaas-payment-migration.xs --keep-source --force -o .\xanoscript\asaas-migration-workspace
xano workspace push --dry-run -d .\xanoscript\asaas-migration-workspace -w 147643
```

O CLI desta versão não oferece comandos de criação de grupos ou rotas de API;
consulte os contratos em `docs/api-plan-mvp.md.txt` para montá-los na interface
do Xano. Nenhum endpoint/grupo ASAAS está configurado ainda.

As regras que dependem de mais de uma tabela não são garantidas somente pelo
schema: as APIs/functions devem validar transações, transições de status,
estoque, cancelamento idempotente, autorização por perfil e a regra de que cada
item de venda possui exatamente um `veiculo_id` ou `peca_id`.

## Publicação realizada

O banco anterior foi removido do workspace Xano `147643`, junto com as APIs e
funções padrão que dependiam dele. O novo esquema mínimo foi publicado com 11
tabelas:

- `perfil`;
- `user`;
- `cliente`;
- `status_veiculo`;
- `veiculo`;
- `veiculo_area`;
- `peca`;
- `forma_pagamento`;
- `status_venda`;
- `venda`;
- `venda_item`.

Por exigência do XanoScript, a chave primária física usa o nome `id` em
minúsculas, embora seja conceitualmente o campo `Id` da especificação.

Os demais campos seguem a nomenclatura solicitada (`UNome`, `CNome`, `CPF`,
`PCNome`, `Valor_bruto`, `Valor_final` etc.). O XanoScript não suporta
diretamente `ON DELETE CASCADE` na declaração de campo; a remoção em cascata
de itens deve ser implementada na API de exclusão da venda, caso essa operação
seja adicionada ao MVP.
