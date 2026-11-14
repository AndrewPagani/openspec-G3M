# Inventário Xano consultado em 13/11/2026

Workspace `147643`. Branch selecionada pelo perfil do CLI; nome não confirmado.

Snapshot de definições retornadas pelo Metadata API, sem `--draft`, `--env` ou `--records`. Não comprova execução autenticada dos endpoints nem valida dados existentes. As definições de função/seed e agentes não foram copiadas.

## Tabelas

| Tabela | Campos declarados | Relações declaradas |
| --- | --- | --- |
| [asaas_cliente](table/asaas_cliente.xs) | `id` (int), `cliente_id` (int), `asaas_customer_id` (text) | `cliente_id → cliente.id` |
| [asaas_cobranca](table/asaas_cobranca.xs) | `id` (int), `venda_id` (int), `asaas_payment_id` (text), `invoice_url` (text), `status?` (text), `due_date` (date) | `venda_id → venda.id` |
| [cliente](table/cliente.xs) | `id` (int), `CNome` (text), `CPF` (text), `Telefone` (text), `Email?` (email), `created_at?` (timestamp) | — |
| [forma_pagamento](table/forma_pagamento.xs) | `id` (int), `Metodo` (text) | — |
| [pagamento](table/pagamento.xs) | `id` (int), `venda_id` (int), `asaas_payment_id` (text), `asaas_customer_id?` (text), `asaas_installment_id?` (text), `status_asaas` (text), `billing_type?` (text), `valor` (decimal), `valor_liquido?` (decimal), `taxa?` (decimal), `numero_parcela?` (int), `total_parcelas?` (int), `vencimento?` (timestamp), `recebido_em?` (timestamp), `updated_at?` (timestamp) | `venda_id → venda.id` |
| [peca](table/peca.xs) | `id` (int), `PCNome` (text), `PCvalor` (decimal), `qtd_disp?` (int), `area_id?` (int), `imagem_url?` (text) | `area_id → veiculo_area.id` |
| [perfil](table/perfil.xs) | `id` (int), `Cargo` (text) | — |
| [status_veiculo](table/status_veiculo.xs) | `id` (int), `Descricao` (text) | — |
| [status_venda](table/status_venda.xs) | `id` (int), `Descricao_venda` (text) | — |
| [user](table/user.xs) | `id` (int), `UNome` (text), `Email` (email), `perfil_id` (int), `Senha` (password), `created_at?` (timestamp) | `perfil_id → perfil.id` |
| [veiculo](table/veiculo.xs) | `id` (int), `Modelo` (text), `Marca` (text), `Cor` (text), `Ano` (int), `Placa?` (text), `Chassi?` (text), `Quilometragem?` (decimal), `Preco` (decimal), `status_id` (int), `created_at?` (timestamp), `imagem_url?` (text) | `status_id → status_veiculo.id` |
| [veiculo_area](table/veiculo_area.xs) | `id` (int), `Secao` (text) | — |
| [veiculo_detalhe](table/veiculo_detalhe.xs) | `id` (int), `veiculo_id` (int), `uf_registro?` (text), `cidade_registro?` (text), `ano_fabricacao?` (int), `motorizacao?` (text), `combustivel?` (text), `cambio?` (text), `quilometragem?` (decimal), `numero_portas?` (int), `numero_lugares?` (int), `opcionais?` (json), `created_at?` (timestamp) | `veiculo_id → veiculo.id` |
| [venda](table/venda.xs) | `id` (int), `cliente_id` (int), `vendedor_id` (int), `forma_pagamento_id` (int), `status_id` (int), `Valor_bruto` (decimal), `Desconto?` (decimal), `Valor_final` (decimal), `data_venda?` (timestamp), `cancel_reason?` (text), `cancelled_at?` (timestamp), `payment_email_status?` (text), `payment_email_requested_at?` (timestamp) | `cliente_id → cliente.id`, `vendedor_id → user.id`, `forma_pagamento_id → forma_pagamento.id`, `status_id → status_venda.id` |
| [venda_item](table/venda_item.xs) | `id` (int), `venda_id` (int), `veiculo_id?` (int), `peca_id?` (int), `qtd?` (int), `preco_unit` (decimal) | `venda_id → venda.id`, `veiculo_id → veiculo.id`, `peca_id → peca.id` |
| [venda_parcela](table/venda_parcela.xs) | `id` (int), `venda_id` (int), `numero_parcela` (int), `total_parcelas` (int), `valor` (decimal), `vencimento` (timestamp), `status?` (text), `forma_recebida_id?` (int), `recebido_em?` (timestamp), `recebido_por?` (int), `cancelada_em?` (timestamp), `updated_at?` (timestamp) | `venda_id → venda.id`, `forma_recebida_id → forma_pagamento.id`, `recebido_por → user.id` |

`?` representa a declaração opcional no XanoScript; campos, defaults, índices e validações completos estão nos arquivos vinculados. Valores dos catálogos e existência de registros não foram consultados.

## Endpoints

| Método | Rota no grupo | Grupo | Autenticação declarada | Fonte |
| --- | --- | --- | --- | --- |
| POST | `/webhooks/asaas/pagamentos` | `asaas_webhooks` | `não declarada` | [definição](api/asaas_webhooks/webhooks/asaas/pagamentos_POST.xs) |
| POST | `/auth/login` | `autenticacao` | `não declarada` | [definição](api/autenticacao/auth/login_POST.xs) |
| GET | `/auth/me` | `autenticacao` | `user` | [definição](api/autenticacao/auth/me_GET.xs) |
| DELETE | `/clientes/{id}` | `cadastros` | `user` | [definição](api/cadastros/clientes/id_DELETE.xs) |
| GET | `/clientes/{id}` | `cadastros` | `user` | [definição](api/cadastros/clientes/id_GET.xs) |
| PATCH | `/clientes/{id}` | `cadastros` | `user` | [definição](api/cadastros/clientes/id_PATCH.xs) |
| GET | `/clientes` | `cadastros` | `user` | [definição](api/cadastros/clientes_GET.xs) |
| POST | `/clientes` | `cadastros` | `user` | [definição](api/cadastros/clientes_POST.xs) |
| GET | `/formas-pagamento` | `cadastros` | `user` | [definição](api/cadastros/formas_pagamento_GET.xs) |
| POST | `/pecas/{id}/ajuste-estoque` | `cadastros` | `user` | [definição](api/cadastros/pecas/id/ajuste_estoque_POST.xs) |
| GET | `/pecas/{id}` | `cadastros` | `user` | [definição](api/cadastros/pecas/id_GET.xs) |
| PATCH | `/pecas/{id}` | `cadastros` | `user` | [definição](api/cadastros/pecas/id_PATCH.xs) |
| GET | `/pecas` | `cadastros` | `user` | [definição](api/cadastros/pecas_GET.xs) |
| POST | `/pecas` | `cadastros` | `user` | [definição](api/cadastros/pecas_POST.xs) |
| GET | `/perfis` | `cadastros` | `user` | [definição](api/cadastros/perfis_GET.xs) |
| GET | `/status-veiculos` | `cadastros` | `user` | [definição](api/cadastros/status_veiculos_GET.xs) |
| GET | `/status-vendas` | `cadastros` | `user` | [definição](api/cadastros/status_vendas_GET.xs) |
| GET | `/veiculo-areas` | `cadastros` | `user` | [definição](api/cadastros/veiculo_areas_GET.xs) |
| PATCH | `/veiculos/{id}/detalhes` | `cadastros` | `user` | [definição](api/cadastros/veiculos/id/detalhes_PATCH.xs) |
| POST | `/veiculos/{id}/detalhes` | `cadastros` | `user` | [definição](api/cadastros/veiculos/id/detalhes_POST.xs) |
| POST | `/veiculos/{id}/status` | `cadastros` | `user` | [definição](api/cadastros/veiculos/id/status_POST.xs) |
| GET | `/veiculos/{id}` | `cadastros` | `user` | [definição](api/cadastros/veiculos/id_GET.xs) |
| PATCH | `/veiculos/{id}` | `cadastros` | `user` | [definição](api/cadastros/veiculos/id_PATCH.xs) |
| GET | `/veiculos` | `cadastros` | `user` | [definição](api/cadastros/veiculos_GET.xs) |
| POST | `/veiculos` | `cadastros` | `user` | [definição](api/cadastros/veiculos_POST.xs) |
| GET | `/auditoria_parcelas` | `gerenciamento` | `user` | [definição](api/gerenciamento/auditoria_parcelas_GET.xs) |
| GET | `/indicadores` | `gerenciamento` | `user` | [definição](api/gerenciamento/indicadores_GET.xs) |
| GET | `/usuarios/{id}` | `gerenciamento` | `user` | [definição](api/gerenciamento/usuarios/id_GET.xs) |
| GET | `/usuarios` | `gerenciamento` | `user` | [definição](api/gerenciamento/usuarios_GET.xs) |
| POST | `/vendas/{id}/cancelar` | `vendas` | `user` | [definição](api/vendas/vendas/id/cancelar_POST.xs) |
| POST | `/vendas/{id}/entregar` | `vendas` | `user` | [definição](api/vendas/vendas/id/entregar_POST.xs) |
| POST | `/vendas/{id}/link-pagamento` | `vendas` | `user` | [definição](api/vendas/vendas/id/link_pagamento_POST.xs) |
| POST | `/vendas/{id}/pagamento/atualizar` | `vendas` | `user` | [definição](api/vendas/vendas/id/pagamento/atualizar_POST.xs) |
| POST | `/vendas/{id}/pagamento/notificar` | `vendas` | `user` | [definição](api/vendas/vendas/id/pagamento/notificar_POST.xs) |
| GET | `/vendas/{id}/pagamento` | `vendas` | `user` | [definição](api/vendas/vendas/id/pagamento_GET.xs) |
| POST | `/vendas/{id}/parcelas/{parcela_id}/receber` | `vendas` | `user` | [definição](api/vendas/vendas/id/parcelas/parcela_id/receber_POST.xs) |
| GET | `/vendas/{id}` | `vendas` | `user` | [definição](api/vendas/vendas/id_GET.xs) |
| GET | `/vendas` | `vendas` | `user` | [definição](api/vendas/vendas_GET.xs) |
| POST | `/vendas` | `vendas` | `user` | [definição](api/vendas/vendas_POST.xs) |

O caminho externo inclui `/api:<grupo>`; o app resolve indicadores por `/gerenciamento/indicadores` e usa o ID `Q9GErvvS` como padrão do grupo de vendas. A presença de uma rota não significa que o app a chama ou que suas precondições permitem execução.

## Diferenças em relação à exportação local

| Arquivo remoto | Comparação textual com `xanoscript/workspace_current` |
| --- | --- |
| [api/cadastros/clientes/id_DELETE.xs](api/cadastros/clientes/id_DELETE.xs) | divergente |
| [api/cadastros/clientes_POST.xs](api/cadastros/clientes_POST.xs) | divergente |
| [api/cadastros/pecas/id/ajuste_estoque_POST.xs](api/cadastros/pecas/id/ajuste_estoque_POST.xs) | divergente |
| [api/cadastros/pecas/id_GET.xs](api/cadastros/pecas/id_GET.xs) | divergente |
| [api/cadastros/pecas/id_PATCH.xs](api/cadastros/pecas/id_PATCH.xs) | divergente |
| [api/cadastros/pecas_GET.xs](api/cadastros/pecas_GET.xs) | divergente |
| [api/cadastros/pecas_POST.xs](api/cadastros/pecas_POST.xs) | divergente |
| [api/cadastros/veiculos/id/detalhes_PATCH.xs](api/cadastros/veiculos/id/detalhes_PATCH.xs) | divergente |
| [api/cadastros/veiculos/id/detalhes_POST.xs](api/cadastros/veiculos/id/detalhes_POST.xs) | divergente |
| [api/cadastros/veiculos/id/status_POST.xs](api/cadastros/veiculos/id/status_POST.xs) | divergente |
| [api/cadastros/veiculos/id_GET.xs](api/cadastros/veiculos/id_GET.xs) | divergente |
| [api/cadastros/veiculos/id_PATCH.xs](api/cadastros/veiculos/id_PATCH.xs) | divergente |
| [api/cadastros/veiculos_GET.xs](api/cadastros/veiculos_GET.xs) | divergente |
| [api/cadastros/veiculos_POST.xs](api/cadastros/veiculos_POST.xs) | divergente |
| [api/gerenciamento/auditoria_parcelas_GET.xs](api/gerenciamento/auditoria_parcelas_GET.xs) | ausente_local |
| [api/gerenciamento/indicadores_GET.xs](api/gerenciamento/indicadores_GET.xs) | divergente |
| [api/vendas/vendas/id/cancelar_POST.xs](api/vendas/vendas/id/cancelar_POST.xs) | divergente |
| [api/vendas/vendas/id/link_pagamento_POST.xs](api/vendas/vendas/id/link_pagamento_POST.xs) | divergente |
| [api/vendas/vendas/id/pagamento_GET.xs](api/vendas/vendas/id/pagamento_GET.xs) | divergente |
| [api/vendas/vendas/id/parcelas/parcela_id/receber_POST.xs](api/vendas/vendas/id/parcelas/parcela_id/receber_POST.xs) | divergente |
| [api/vendas/vendas/id_GET.xs](api/vendas/vendas/id_GET.xs) | divergente |
| [api/vendas/vendas_GET.xs](api/vendas/vendas_GET.xs) | divergente |
| [api/vendas/vendas_POST.xs](api/vendas/vendas_POST.xs) | divergente |
| [table/asaas_cliente.xs](table/asaas_cliente.xs) | ausente_local |
| [table/asaas_cobranca.xs](table/asaas_cobranca.xs) | ausente_local |
| [table/cliente.xs](table/cliente.xs) | divergente |
| [table/peca.xs](table/peca.xs) | divergente |
| [table/veiculo.xs](table/veiculo.xs) | divergente |
| [table/veiculo_detalhe.xs](table/veiculo_detalhe.xs) | divergente |
| [table/venda.xs](table/venda.xs) | divergente |
| [table/venda_parcela.xs](table/venda_parcela.xs) | divergente |

A comparação ignora diferenças CRLF/LF e espaços no início/fim do documento; não é uma comparação semântica. `pagamento_evento` existe no diretório local e não foi retornada nesta leitura remota. A função remota `seed/popular_tabelas` também não existe na exportação local; sua definição não foi copiada nem executada.

## Integridade

O arquivo [manifest.json](manifest.json) registra SHA-256 dos arquivos copiados, GUIDs e resultado da comparação local. Esta pasta é evidência histórica de consulta, não uma pasta de publicação ou sincronização.
