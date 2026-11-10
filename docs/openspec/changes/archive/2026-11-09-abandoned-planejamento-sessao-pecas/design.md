# Design: Sessão de peças

## Contrato de dados

A listagem `GET /pecas` deve preservar paginação e filtros existentes e
retornar campos normalizados para a interface:

```json
{
  "id": 25,
  "nome": "Pastilha de freio",
  "preco": 299.90,
  "quantidade_disponivel": 8,
  "area_id": 2,
  "area_nome": "Freios",
  "imagem_url": "https://..."
}
```

O banco atualmente possui `PCNome`, `PCvalor`, `qtd_disp` e `area_id`. A
evolução do contrato deve adicionar uma URL de imagem opcional, sem quebrar
registros existentes. O backend deve validar URLs HTTP/HTTPS quando a imagem
for informada.

Filtros previstos:

- `page` e `per_page`;
- `busca`;
- `area_id`;
- `somente_disponiveis`;
- opcionalmente `estoque_baixo` e `sem_estoque`.

## Catálogo

O `ResourceState` deve normalizar os campos para apresentação, incluindo:

- nome;
- preço em moeda brasileira;
- área;
- quantidade;
- URL ou placeholder;
- classe de estoque;
- disponibilidade para compra.

O `resource_page` deve usar um card específico para `/pecas`, mantendo o
comportamento atual de tabela para os demais recursos. O card deve conter
imagem, nome, área, preço, estoque, botão `Comprar` e link de detalhe.

Limiares de estoque:

| Quantidade | Classe |
|---:|---|
| `0` | sem estoque |
| `1` a `5` | estoque baixo |
| `> 5` | disponível |

## Carrinho

Criar um estado de carrinho separado do estado de recursos e vendas:

```python
{
    "peca_id": 25,
    "nome": "Pastilha de freio",
    "preco_unitario": 299.90,
    "quantidade": 2,
    "estoque_disponivel": 8,
    "subtotal": 599.80
}
```

Responsabilidades:

- adicionar e remover peças;
- alterar quantidade;
- consolidar a mesma peça em um único item;
- impedir quantidade menor que 1 ou maior que o estoque conhecido;
- recalcular subtotais;
- limpar o carrinho após sucesso.

O preço exibido serve apenas para apresentação. O Xano deve recalcular o preço
e validar o estoque no momento da criação da venda.

## Checkout e venda

O checkout deve reutilizar o `VendasState` e o endpoint existente:

```json
{
  "cliente_id": 10,
  "forma_pagamento_id": 2,
  "numero_parcelas": 3,
  "Desconto": 0,
  "itens": [
    {"peca_id": 25, "qtd": 2}
  ]
}
```

O clique em `Comprar` não deve criar uma venda incompleta. Ele deve adicionar
ao carrinho e encaminhar o usuário ao checkout após a seleção dos itens.

## Cadastro e detalhe

O formulário de peça deve substituir o formulário genérico e suportar:

- nome;
- preço;
- quantidade inicial;
- área;
- URL da imagem;
- pré-visualização.

O detalhe deve exibir os mesmos dados do card em maior destaque. Cadastro,
edição e ajuste de estoque ficam restritos ao gerente. O ajuste deve continuar
usando o endpoint de ajuste de estoque do Xano.

## Permissões

| Ação | Gerente | Vendedor | Cliente |
|---|---:|---:|---:|
| Visualizar e buscar peças | Sim | Sim | Conforme contrato |
| Adicionar ao carrinho | Sim | Sim | Conforme contrato |
| Criar venda | Sim | Sim | Não |
| Cadastrar/editar peça | Sim | Não | Não |
| Ajustar estoque | Sim | Não | Não |

As permissões devem ser aplicadas no frontend para UX e no Xano para
segurança.
