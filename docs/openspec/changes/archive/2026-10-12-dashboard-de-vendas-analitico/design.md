# Design: Dashboard de vendas analítico

## Contexto

O app já possui `GET /api:gerenciamento/indicadores`, autenticação Xano e
agregações de vendas/estoque. A resposta existente oferece KPIs como valor
recebido por baixas manuais, vendas pagas, ticket médio e cancelamentos, além
de séries diárias, formas de pagamento, mix de itens e estoque por status.
Ela não devolve as dimensões necessárias para algumas análises desejadas
(propostas, entradas/saídas de estoque, marca vendida, categoria/fabricante
de peças ou canal de venda).

## Decisões

1. **Fonte dos dados:** manter o endpoint existente, o token da sessão e os
   filtros de datas/gerência já suportados. Usar `httpx.AsyncClient` para a
   chamada de rede. Nenhuma chave ou token é copiado para um campo de estado
   visível ao cliente.
2. **KPIs:** apresentar recebimentos efetivamente registrados, vendas pagas,
   ticket médio geral de vendas pagas e cancelamentos. O ticket é o campo
   agregado devolvido pelo endpoint; não classificá-lo por veículo ou peça
   quando o contrato não fornece essa separação. Dados em branco ou erro da
   API não são substituídos por fixtures.
3. **Série temporal:** o Xano fornece agregados por data com `periodo`,
   `total_vendas` e `valor_total`. Reagrupar localmente em dia, semana ISO,
   mês ou ano; uma alteração de granularidade refaz a consulta ao endpoint
   existente e atualiza a série derivada. O gráfico apresenta a métrica
   `valor_total` disponível, sem fabricar séries separadas de veículos e
   peças.
4. **Pagamentos e mix:** o donut mostra quantidades por método de pagamento,
   pois não há valor financeiro por forma na resposta. Excluir categorias
   zeradas e agregar caudas longas em “Outros” para preservar legibilidade.
   O gráfico de mix usa quantidades de veículos e peças. Estoque por status é
   uma contagem, não uma projeção de vendas.
5. **Filtros e perfil:** datas continuam sendo aplicadas ao clicar em
   “Atualizar dados”. Filtros por ID continuam restritos a gerente e
   administrador; o endpoint Xano permanece responsável pelo escopo de
   autorização. Filtro de tipo de item não é descrito como filtro de todos os
   KPIs, pois a API não o aplica uniformemente a cada agregado.
6. **Exportação:** o botão gera CSV local dos KPIs já apresentados e do
   intervalo selecionado; não inicia uma nova chamada nem inclui informações
   de credenciais.
7. **Métricas sem contrato:** conversão, giro, marcas vendidas, participação,
   categorias/fabricantes de peças e canais são exibidos como indisponíveis,
   com a razão. Sua implementação requer extensão futura e versionada do
   contrato/schema Xano.
8. **Apresentação:** cards escuros com contraste, grade adaptável a tablet e
   desktop, gráficos Recharts com tooltip/legenda e indicação de estado
   vazio/carregamento/erro.

## Riscos e validação

- A série temporal do contrato é diária e consolidada. Semana, mês e ano são
  agrupamentos no cliente e não adicionam dimensões que a API não retorna.
- O endpoint atual reporta dados agregados globais para métodos de pagamento;
  essas contagens não devem ser rotuladas como valores recebidos por método.
- Relatórios não suportados permanecem intencionalmente indisponíveis até que
  os campos de origem existam no Xano.
- Testes verificam formatação, agrupamento e transporte HTTP; a rota Reflex
  foi renderizada em ambiente local, sem publicar scripts no Xano.
