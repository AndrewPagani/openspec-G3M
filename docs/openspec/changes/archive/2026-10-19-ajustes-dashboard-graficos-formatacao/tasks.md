# Tarefas

## Timeline

- [x] Formatar datas para `DD/MM/AAAA`.
- [x] Identificar o eixo Y como `R$`.
- [x] Remover rótulos permanentes dos pontos.
- [x] Manter valores numéricos para escala e tooltip.
- [x] Arredondar valores financeiros para duas casas decimais.

## Gráficos

- [x] Transformar peças vendidas por categoria em gráfico de barras.
- [x] Incluir valor total de peças no tooltip.
- [x] Aplicar cores distintas por coluna em marcas e categorias.
- [x] Remover rótulos permanentes de quantidade.
- [x] Ajustar largura e espaçamento das barras de categorias.
- [x] Alinhar as categorias com os rótulos do eixo X.

## Relatórios e integração

- [x] Corrigir quantidade de vendas por status para não usar `R$`.
- [x] Manter valores totais dos status como moeda brasileira.
- [x] Validar live e draft com o Xano CLI.
- [x] Confirmar compatibilidade do parser com os agregados do endpoint.

## Verificação

- [x] Importar `app.pages.gerenciamento`.
- [x] Renderizar os componentes dos gráficos.
- [x] Executar `python -m unittest tests.test_dashboard_state`.
- [x] Executar `git diff --check` nos arquivos de implementação.
