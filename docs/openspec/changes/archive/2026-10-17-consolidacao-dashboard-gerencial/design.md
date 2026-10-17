# Design: Consolidação do dashboard gerencial

## Responsabilidades

O Xano permanece responsável por autenticação, autorização, consultas,
persistência, parcelas recebidas e agregações de domínio. O frontend Reflex
faz apenas normalização de envelopes, validação de formato, agrupamento visual
e apresentação.

## Indicadores financeiros

O endpoint `GET /api:gerenciamento/indicadores` retorna os KPIs dentro de
`kpis`, incluindo:

- `total_vendas_periodo`;
- `valor_bruto_vendido`;
- `valor_liquido_recebido_periodo`;
- `vendas_pagas`;
- `ticket_medio_vendas_pagas`;
- vendas canceladas e percentual.

O ticket médio exibido no frontend é calculado com os valores da própria API:

```text
valor_bruto_vendido / total_vendas_periodo
```

Quando o total de vendas é zero, o resultado é `R$ 0,00`. Se o campo
`total_vendas_periodo` não estiver presente, a resposta é tratada como
incompleta em vez de usar um valor inventado.

## Parcelas recebidas

Para cada parcela, o endpoint busca a venda relacionada diretamente por
`venda_id`, evitando dependência de uma lista geral sujeita a paginação ou
comparação incorreta de tipos.

Uma parcela recebida válida possui status normalizado `RECEBIDA`, ou os campos
de baixa preenchidos, não é `PENDENTE` nem `CANCELADA`, tem valor positivo,
venda válida e está dentro do período de recebimento.

O diagnóstico interno inclui parcelas candidatas, parcelas válidas, status,
valores, vendas distintas e soma dos valores. Esse diagnóstico não é exibido
como bloco na interface.

## Autorização e filtros

Os cargos do sistema são `Gerente`, `Vendedor` e `Cliente`.

- `Gerente` pode consultar o escopo geral e filtrar por vendedor.
- `Vendedor` fica restrito ao próprio usuário.
- `Cliente` não acessa o dashboard gerencial.
- Somente `Gerente` confirma recebimentos.

O filtro opcional usa `$vendedor_filtro`, inicializado com `null`; nenhuma
consulta usa a variável removida `$parsed_vendedor_id`.

## Interface

O dashboard mantém KPIs, timeline, pagamentos, mix, estoque e análises
disponíveis. A lista de vendedores mostra no máximo cinco linhas visíveis,
permite pesquisa por nome e possui rolagem. Foram removidos os blocos de
descontos, canal de venda, conversão e giro.

As séries aceitam envelopes comuns do Xano e variações de nomes de campos.
Categorias com valor zero são preservadas, mas o bloco de diagnóstico textual
de parcelas foi removido da interface.
