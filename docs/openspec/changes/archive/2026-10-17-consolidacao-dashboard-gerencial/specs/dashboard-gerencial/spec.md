# Especificação: Dashboard gerencial consolidado

## Requisito: KPIs financeiros

O dashboard MUST consumir os KPIs retornados em `kpis` e MUST calcular o
ticket médio visual com `valor_bruto_vendido / total_vendas_periodo`.

### Cenário: vendas no período

- **DADO** que a API retorna valor bruto e quantidade de vendas
- **QUANDO** o dashboard carrega os indicadores
- **ENTÃO** o card de ticket médio deve mostrar a divisão desses valores.

### Cenário: período sem vendas

- **DADO** que `total_vendas_periodo` é zero
- **QUANDO** o dashboard calcula a média
- **ENTÃO** deve mostrar `R$ 0,00` sem erro de divisão por zero.

## Requisito: parcelas recebidas

O endpoint MUST contar vendas pagas por `venda_id` distinto e MUST somar
parcelas recebidas somente quando a parcela for válida, positiva e relacionada
a uma venda existente.

### Cenário: múltiplas parcelas da mesma venda

- **DADO** que uma venda possui mais de uma parcela recebida
- **QUANDO** os indicadores são calculados
- **ENTÃO** a venda deve ser contada uma vez em `vendas_pagas`.

## Requisito: autorização

O sistema MUST reconhecer somente o cargo exato `Gerente` para o escopo
gerencial e para confirmação de recebimentos.

### Cenário: filtro sem vendedor

- **DADO** que um gerente consulta o endpoint sem `vendedor_id`
- **QUANDO** os indicadores são carregados
- **ENTÃO** a consulta deve funcionar sem erro de variável ausente e sem filtro
  de vendedor.

## Requisito: apresentação

O dashboard MUST exibir formas de pagamento como gráfico, estoque baixo como
lista normalizada e vendedores em uma área compacta com pesquisa e rolagem.

### Cenário: série envelopada

- **DADO** que o Xano retorna uma série dentro de `data`, `result`, `payload`
  ou `response`
- **QUANDO** o frontend processa a resposta
- **ENTÃO** a série deve ser extraída sem perder categorias válidas ou zeradas.

## Requisito: escopo removido

O dashboard MUST NOT exibir descontos, canal de venda, conversão de estoque,
giro de estoque ou a mensagem textual de diagnóstico de parcelas.
