# Seed compatível com o Xano

Execute `python scripts\generate_xano_seed.py` na raiz do projeto. O gerador
produz JSON e CSV usando somente os campos do schema em
`xanoscript/workspace_current/table`.

Importe nesta ordem:

1. `perfil`, `status_veiculo`, `status_venda`, `forma_pagamento`,
   `veiculo_area`;
2. `veiculo`, `peca`, `cliente`;
3. `venda`;
4. `venda_item`;
5. `venda_parcela`.

`venda_parcela.json` contém uma parcela integral por venda com
`status = "RECEBIDA"` e `recebido_em` igual à data da venda. Isso é necessário
para o endpoint `/gerenciamento/indicadores` calcular faturamento recebido,
vendas pagas e ticket médio.

O seed padrão usa `vendedor_id = 1`. Esse usuário precisa existir no Xano e,
para visualizar todas as vendas, a sessão deve ser de Gerente ou Administrador.
Para outro vendedor, use `--vendedor-id`.

O workspace atual não possui tabelas separadas de marcas/categorias nem os
campos `canal_venda` e `tipo_venda`; essas dimensões não são inventadas.
