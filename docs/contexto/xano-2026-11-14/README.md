# GET /vendas sincronizado em 14/11/2026

Origem: `xano workspace pull --workspace 147643 --branch v1`.
Leitura de definições sem registros, variáveis de ambiente ou drafts.

- [Definição consultada](api/vendas/vendas_GET.xs).
- [Manifesto com SHA-256 e verificações estruturais](manifest.json).
- Arquivo operacional atualizado: `xanoscript/workspace_current/api/vendas/vendas_GET.xs`.

Confirmado por leitura de código: quatro caminhos de data, filtro de vendedor
nas quatro consultas antes da paginação, `in` para referências de clientes e
vendedores, com proteção de listas vazias. O envelope permanece `items` e
`pagination`, compatível com os consumidores locais de clientes e vendas.

Validação de sincronização:

```powershell
xano.cmd workspace push --workspace 147643 --branch v1 --directory xanoscript/workspace_current --include 'api/vendas/vendas_GET.xs' --dry-run
```

O CLI selecionou somente um arquivo e retornou `No changes to push`.
Não foi realizado push efetivo nem execução autenticada do endpoint.
Este snapshot é referência histórica e não deve ser usado como pasta de publicação.
