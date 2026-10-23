# Plano de execução

## Fase 1 — Contrato Xano

- [ ] Adicionar campo opcional de imagem na tabela `peca`.
- [ ] Atualizar `pecas_POST.xs` e `pecas/id_PATCH.xs`.
- [ ] Atualizar `pecas_GET.xs` com campos normalizados.
- [ ] Preservar paginação, busca e filtro por área.
- [ ] Adicionar filtros de disponibilidade necessários.
- [ ] Validar live e draft com Xano CLI.

## Fase 2 — Catálogo

- [ ] Criar normalização específica de peças no `ResourceState`.
- [ ] Criar card visual de peça semelhante ao card de veículo.
- [ ] Exibir imagem ou placeholder.
- [ ] Exibir preço, área, quantidade e status de estoque.
- [ ] Criar grid responsivo.
- [ ] Adicionar busca, área e disponibilidade à interface.

## Fase 3 — Carrinho

- [ ] Criar `CartState`.
- [ ] Adicionar, remover e consolidar peças.
- [ ] Impedir quantidades inválidas.
- [ ] Calcular subtotais e total visual.
- [ ] Exibir resumo e estado vazio.
- [ ] Limpar o carrinho após venda criada.

## Fase 4 — Checkout

- [ ] Integrar os itens do carrinho ao `VendasState`.
- [ ] Substituir a entrada manual de JSON por seleção visual.
- [ ] Manter o suporte ao JSON durante a transição, se necessário.
- [ ] Validar cliente, pagamento e parcelas.
- [ ] Revalidar estoque e preço no Xano.

## Fase 5 — Cadastro e detalhe

- [ ] Criar formulário específico de peça.
- [ ] Adicionar URL e pré-visualização da imagem.
- [ ] Criar detalhe visual da peça.
- [ ] Integrar edição e ajuste de estoque.
- [ ] Aplicar permissões de gerente.

## Fase 6 — Verificação

- [ ] Testar normalização de campos e envelopes.
- [ ] Testar moeda, estoque baixo e sem estoque.
- [ ] Testar filtros e paginação.
- [ ] Testar carrinho e itens duplicados.
- [ ] Testar limite de estoque.
- [ ] Testar payload final de venda.
- [ ] Testar permissões.
- [ ] Importar páginas e executar a suíte completa.

