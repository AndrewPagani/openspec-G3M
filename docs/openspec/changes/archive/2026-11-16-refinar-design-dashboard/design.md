## Context

Ver a motivação em `proposal.md`. A tela está em `app/pages/gerenciamento.py`, com dados em `app/state/dashboard_state.py` e estilos em `assets/styles.css`. Usa Reflex/Recharts, Inter, superfícies escuras e azul principal. Os estilos internos compartilhados excluem o dashboard em vários seletores; copiar regras indiscriminadamente poderia afetar outras telas.

A leitura local encontrou paleta por posição de categoria, tooltips padrão, seis KPIs com ícones de cores diferentes e textos sobre o contrato Xano. Os status de veículo já têm cores semânticas próprias. A inspeção foi estática: contraste, sobreposição e comportamento responsivo ainda precisam de navegador. Specs e implementação local não comprovam o estado atual do endpoint remoto.

Fontes: `docs/contexto-projeto.md`, specs `dashboard-gerencial` e `interface-interna`, arquivos acima e `app/services/vehicle_status.py`. O overview antigo exclui ASAAS, mas a spec vigente e o mapa de contexto registram a integração posterior; não usar esse trecho antigo para redefinir o fluxo financeiro.

## Goals / Non-Goals

**Goals:** facilitar comparação e leitura, manter a identidade existente e isolar o refinamento no dashboard. Usar Impeccable em modo Operate: consistência, densidade útil e estados claros.

**Non-Goals:** redesenhar a navegação global, criar indicadores, alterar cálculos/limiares de estoque, consultar ou publicar Xano, mudar autorização, filtros, CSV ou cobranças. Nenhuma nova biblioteca.

## Decisions

### 1. Refinar o sistema visual existente

Manter Inter, sidebar G3M, fundo escuro, cartões discretos e azul `#3b82f6` como referência inicial. Reutilizar tokens compatíveis e centralizar os tokens específicos restantes sob o escopo do dashboard. Ajustar contraste por medição durante a implementação, sem fixar uma combinação apenas por aparência no código.

Usar neutros para ícones de KPI, azul para ação/seleção e cores semânticas para estados. Evitar arco-íris decorativo, gradientes novos e sombras fortes. A alternativa de adotar outra paleta ou tipografia foi descartada por romper a continuidade solicitada.

### 2. Ordenar a informação pela tarefa

Cabeçalho “Dashboard” com descrição curta; período e atualização como controles principais; CSV secundário. Manter filtros gerenciais identificados e visíveis conforme perfil. KPIs em até três colunas, seguidos pela evolução e distribuições de vendas; agrupar estoque em seção própria, identificando seu escopo temporal real sem afirmar que responde ao período de vendas.

Não esconder filtros em um novo modal. Preservar todas as séries úteis; aproximar gráfico e detalhamento relacionados, evitando títulos repetidos. Validar a ordem visual também na ordem de leitura do documento.

### 3. Aplicar uma gramática comum aos gráficos

Padronizar títulos, unidades, margens, linhas de grade discretas e tooltips com superfície opaca contrastante. Moeda em pt-BR, eixo monetário com abreviação quando necessário e tooltip com valor completo; quantidades sem casas decimais. Sem alterar precisão nos dados, exportação ou agregação.

Comparações de uma série podem usar um único azul. Em distribuições multissérie, a cor acompanha a categoria por identificador estável disponível, nunca por posição após ordenação. Não inventar IDs; sem identificador, usar a chave textual original apenas para apresentação. Preservar o mapeamento semântico existente dos status de veículos e manter rótulos/legendas para que a cor não seja a única informação.

Preferir barras horizontais para marcas/categorias com nomes longos, se a captura confirmar melhor leitura. Nomes completos precisam estar disponíveis em texto ou tooltip; não depender de hover no celular. No gráfico de peças, substituir a série transparente usada para valor monetário por conteúdo explícito no tooltip somente se o mesmo valor estiver presente no payload. Donut de pagamentos pode permanecer com legenda responsiva; não converter quantidade em valor financeiro.

### 4. Revisar a linguagem sem mudar a métrica

Usar “Recebimento líquido” para o KPI de valor líquido recebido, com descrição que não prometa uma regra temporal diferente da resposta. Remover “baixa manual” como explicação do fluxo atual, sem afirmar que todo histórico é ASAAS. Títulos distinguem valor bruto, valor recebido e quantidades.

Estados vazios orientam a revisar período/filtros apenas quando isso se aplica; não atribuem todo vazio a erro no Xano. Erro e resposta incompleta continuam explícitos, sem zeros fabricados. Estados de carregamento usam o padrão existente e evitam apresentar números anteriores como resultado novo.

### 5. Isolar divergências financeiras

O código calcula `ticket_medio` com `valor_bruto_vendido / total_vendas_periodo`; a spec vigente exige recebimentos autoritativos e exclusão de vendas não recebidas/canceladas/vencidas. Esta change não corrige essa fórmula e não declara conformidade financeira.

Na revisão visual, identificar o indicador local como “Valor médio por venda”, com descrição “Valor bruto dividido pelo total de vendas”, enquanto a fórmula persistir. Isso torna o valor exibido explícito, sem substituí-lo por um suposto ticket de recebimentos. Registrar no encerramento a pendência do ticket previsto na spec; uma correção funcional exige comparar contrato remoto e comportamento real antes de definir o cálculo. Não rebaixar o requisito financeiro vigente para acomodar a implementação local.

Também preservar e identificar o corte existente de peças com estoque baixo (até cinco), distinguindo-o de “sem estoque”; não alterar limiar ou deduzir uma contagem ausente.

## Risks / Trade-offs

- CSS compartilhado e camadas duplicadas → limitar seletores ao dashboard e comparar outra página interna antes/depois.
- Tooltips/formatadores dependem das props disponíveis no Reflex instalado → verificar API local antes de implementar; preferir recursos existentes, sem dependência nova.
- Valores extremos e nomes extensos → validar conteúdo longo, muitas categorias, zeros e formatos monetários grandes em navegador.
- Renomear o indicador não resolve a divergência do ticket → manter a limitação explícita na entrega e não marcar o requisito financeiro como validado.
- Fixtures ajudam a verificar aparência, mas não provam autorização nem API → separar evidência visual com dados controlados de qualquer execução autenticada real.

## Migration Plan

Não há migração nem publicação de backend. Após aprovação para aplicar, executar Impeccable conforme as instruções instaladas, ler o craft floor antes de editar e implementar em componentes/estilos locais. Verificar lint/build e revisar capturas em 1920x1080, 1440x900, 1366x768 e largura estreita de 390px, incluindo teclado e zoom de 200%. Executar o detector manual da skill ao concluir a interface e resolver os achados pertinentes. Reversão restrita ao diff desta change, preservando alterações concorrentes.
