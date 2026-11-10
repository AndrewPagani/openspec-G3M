# Especificação: Catálogo de peças e compra

## Requisito: Listagem visual

O sistema DEVE exibir peças em cards responsivos semelhantes aos cards de
veículos.

Cada card DEVE mostrar nome, imagem ou placeholder, preço, área do veículo,
quantidade disponível e estado de estoque.

## Requisito: Estoque

O sistema DEVE classificar peças com quantidade zero como sem estoque,
quantidade de um a cinco como estoque baixo e quantidade acima de cinco como
disponível.

Peças sem estoque NÃO DEVEM ser adicionadas ao carrinho.

## Requisito: Busca e filtros

O sistema DEVE suportar busca por nome, filtro por área e paginação. O filtro
de disponibilidade DEVE ser aplicado no backend quando disponível e validado
novamente no frontend para preservar a experiência.

## Requisito: Carrinho

Ao clicar em `Comprar`, o sistema DEVE adicionar a peça ao carrinho, sem criar
uma venda imediatamente.

O carrinho DEVE consolidar a mesma peça, limitar a quantidade ao estoque
disponível e permitir remoção e alteração de quantidade.

## Requisito: Venda

O checkout DEVE enviar itens no formato `peca_id` e `qtd` para o endpoint
existente de vendas. O backend DEVE recalcular o preço e revalidar o estoque;
valores enviados pelo frontend não podem ser considerados fonte de verdade.

## Requisito: Administração

Somente usuários com perfil autorizado de gerente podem cadastrar, editar ou
ajustar estoque de peças. A autorização DEVE ser aplicada também no Xano.
