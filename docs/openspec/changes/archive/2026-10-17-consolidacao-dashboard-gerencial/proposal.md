# Proposta: Consolidação do dashboard gerencial e indicadores financeiros

## Problema

O dashboard gerencial passou por várias correções de contrato, visualização e
regras de negócio. Havia divergências entre o frontend Reflex e o endpoint
Xano para KPIs financeiros, séries de gráficos, estoque, permissões e filtros.
Também era necessário registrar a correção de erros de runtime do Xano e a
remoção de blocos que deixaram de fazer parte do escopo.

## Objetivo

Consolidar em uma única mudança o estado final do dashboard gerencial,
mantendo o Xano como fonte de dados e regras de negócio, com parsing resiliente
no frontend e apresentação consistente dos indicadores.

## Escopo

- Corrigir o consumo dos KPIs dentro do envelope `kpis`.
- Exibir estoque baixo ou sem estoque com nome, quantidade e valor.
- Restaurar gráficos de formas de pagamento e preservar categorias zeradas.
- Exibir análises disponíveis de veículos por marca e peças por categoria.
- Exibir vendas por vendedor com busca, ordenação e área rolável.
- Remover conversão/giro de estoque, descontos e canal de venda da interface.
- Corrigir o processamento de parcelas recebidas, vendas pagas distintas e
  diagnóstico financeiro no endpoint Xano.
- Corrigir o filtro opcional `vendedor_id` sem variáveis ausentes.
- Restringir operações gerenciais ao cargo `Gerente`.
- Calcular no frontend o ticket médio com
  `valor_bruto_vendido / total_vendas_periodo`, usando os valores retornados
  pela API.

## Fora do escopo

- Criar dados financeiros fictícios ou alterar registros de produção.
- Mover regras de autorização ou persistência para o frontend.
- Criar canais de venda, fabricante, conversão ou giro sem dados no backend.
- Alterar permissões de outros endpoints não relacionados ao dashboard e ao
  recebimento de parcelas.

## Resultado

A implementação foi concluída, validada com a suíte local e arquivada nesta
change em 17/10/2026.
