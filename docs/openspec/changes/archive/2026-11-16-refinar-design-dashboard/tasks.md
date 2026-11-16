## 1. Preparação e referência visual

- [x] 1.1 Ler a spec delta, o design e a versão instalada de Impeccable; executar o contexto conforme a skill e ler o craft floor antes da primeira edição. Verificar que a intervenção permanece no dashboard e registrar as instruções aplicáveis.
- [x] 1.2 Capturar a tela atual e uma página interna de referência, verificando superfícies, tipografia, controles e estados para vendedor e gerente/admin. Identificar capturas com dados controlados; elas não comprovam autorização remota.

## 2. Hierarquia, cores e textos

- [x] 2.1 Refinar tokens/seletores do dashboard, cores e hierarquia dos cartões, preservando Inter, tema escuro, azul e shell G3M; verificar o diff e a comparação visual com outra página para evitar efeitos globais.
- [x] 2.2 Organizar cabeçalho, período, filtros, ações, KPIs e seção de estoque conforme o design; verificar até três colunas de KPIs, ordem de leitura e manutenção dos controles por perfil.
- [x] 2.3 Revisar títulos, descrições e estados de feedback, incluindo “Valor médio por venda” com base bruta explícita e distinção entre estoque baixo e sem estoque; verificar correspondência entre cada texto e o valor efetivamente exibido, sem mudar fórmulas ou limiares.

## 3. Gráficos

- [x] 3.1 Padronizar eixos, unidades e tooltips com formatação pt-BR, moeda completa e contagens inteiras; verificar em navegador séries com zero, valores altos e agrupamentos temporais existentes.
- [x] 3.2 Padronizar cores de séries e associação estável de categorias, preservando cores semânticas de status; verificar uma mesma categoria antes/depois de reordenação e identificar séries também por texto.
- [x] 3.3 Ajustar orientação, margens, legendas e nomes longos; remover a série transparente de peças somente após preservar os valores existentes em tooltip explícito. Verificar leitura em toque e payloads com/sem valores monetários opcionais, sem inventar campos.

## 4. Verificação integrada e entrega

- [x] 4.1 Verificar capturas em 1920x1080, 1440x900, 1366x768, 390px e zoom de 200%, com nomes extensos, muitas categorias e estados de carregamento/vazio/erro/resposta incompleta; corrigir cortes, sobreposições e overflow da página.
- [x] 4.2 Verificar contraste medido, foco, nomes acessíveis e operação por teclado; executar o detector manual do Impeccable ao concluir a interface, conforme a skill, e registrar/corrigir achados pertinentes.
- [x] 4.3 Verificar preservação de filtros/IDs, CSV, seleção temporal e visibilidade por perfil; executar lint, build e testes existentes pertinentes. Se houver nova transformação de apresentação, testar apenas seus casos relevantes, sem alegar validação de autorização Xano por testes locais.
- [x] 4.4 Registrar arquivos alterados, evidências visuais, verificações e limitações na entrega; explicitar que o cálculo do ticket médio previsto na spec continua pendente de correção funcional e que esta change não revalidou nem publicou a API.
