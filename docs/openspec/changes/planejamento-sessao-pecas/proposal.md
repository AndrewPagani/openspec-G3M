# Proposta: Sessão de peças com catálogo e compra

## Problema

A sessão de peças atualmente usa a listagem genérica de recursos, enquanto a
sessão de veículos possui cards com imagem, preço, informações resumidas e
acesso visual aos detalhes. O fluxo de vendas aceita `peca_id` e `qtd`, mas a
interface ainda exige a montagem manual de JSON.

## Objetivo

Criar uma sessão de peças visualmente equivalente à de veículos, com catálogo
responsivo, informações de estoque e uma entrada segura para o fluxo de
compra/venda.

## Escopo

- Cards de peças com nome, foto, preço, área do veículo e quantidade disponível.
- Placeholder quando a peça não possuir imagem.
- Busca, filtro por área, filtro de disponibilidade e paginação.
- Status visuais para sem estoque, estoque baixo e disponível.
- Botão `Comprar` tratado inicialmente como `Adicionar ao carrinho`.
- Carrinho com múltiplas peças, consolidação de itens repetidos e validação de
  quantidade.
- Integração do carrinho com o payload existente de `POST /vendas`.
- Formulário específico de peça com imagem e seleção de área.
- Detalhe visual da peça e ajuste de estoque para gerente.
- Normalização de campos e contratos no frontend.

## Fora do escopo

- Pagamento externo ou checkout público.
- Criação automática de venda ao clicar no card.
- Confiança no preço enviado pelo frontend.
- Alteração da regra financeira do dashboard.

## Resultado esperado

O usuário consegue localizar uma peça, visualizar seus dados, adicioná-la ao
carrinho, ajustar a quantidade dentro do estoque disponível e encaminhar uma
venda validada pelo Xano.
