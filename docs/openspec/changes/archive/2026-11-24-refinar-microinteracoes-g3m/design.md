## Context

O CSS compartilhado usa transições pontuais em controles. O Dashboard desativa a animação de desenho das séries e o projeto limita o custo das listagens com carregamento progressivo e paginação visual. A venda alterna o resumo e o painel de pagamento conforme a criação confirmada. O Excel já comunica o progresso por etapa. Esses estados existentes dão pontos de integração para o feedback.

## Goals / Non-Goals

**Metas**

- Concentrar a atenção na área em que o operador atuou.
- Preservar coerência visual nos temas claro e escuro e usabilidade por teclado e toque.
- Manter compatibilidade com carregamento progressivo, navegação concorrente e preferência por movimento reduzido.

**Fora do escopo**

- Redesign de telas, novos fluxos, ajustes de API ou mudanças de regras de negócio.
- Animações de entrada de página inteira, animações contínuas nas listas e redesenho animado dos gráficos.

## Decisions

1. **Referências visuais.** Usar as telas renderizadas atuais como referência da Frontend App Builder. Revisar frames dos controles, do resumo e dos avisos com Impeccable. Usar Ponytail para manter os ajustes nos componentes e nos estados existentes.
2. **Tempos e propriedades.** Adotar 100–150 ms para foco, pressionamento e seleções, e 150–250 ms para confirmações. Priorizar contorno, cor e opacidade. Usar deslocamento pequeno apenas no painel localizado de pagamento, se a mudança puder ser compreendida sem ele. Aplicar alternativa estática em `prefers-reduced-motion`, mantendo ícones, texto e foco. Reutilizar o azul e as cores semânticas existentes nos dois temas.
3. **Vendas como referência.** Ao adicionar ou remover um item, destacar somente a linha afetada ou o resumo após a atualização local. O painel exibido após criação pode entrar uma vez. Calcular o feedback de cobrança com o estado da venda atual. A cópia deve usar o resultado da área de transferência. A recuperação do link deve continuar usando a venda já registrada.
4. **Cadastros e controles.** Reutilizar estados de sucesso, falha e carregamento e distinguir visualmente seu significado. Usar o aviso da listagem após exclusão confirmada, preservando um destino de foco lógico. Aplicar o mesmo vocabulário visual aos campos, ao Login e aos avisos de Configurações.
5. **Dashboard e navegação.** Aproveitar as ações e regiões de status existentes. Mostrar **Download iniciado** no momento em que o arquivo for entregue ao navegador. Manter dimensões do cabeçalho e feedback de navegação independente das respostas pendentes. Conservar a renderização atual dos gráficos. CSS e componentes Reflex existentes atendem ao escopo.

## Risks / Trade-offs

- **Rolagem mais pesada** → Limitar efeitos à região alterada, evitar pintura contínua e comparar fluxos representativos antes e depois com as mesmas fixtures, viewport e condições de CPU.
- **Feedback repetido durante carregamento progressivo** → Disparar o destaque a partir da ação, com vínculo ao registro, rota e sessão atuais, em vez de dispará-lo a cada renderização dos cartões ou resultados.
- **Confirmação ambígua** → Distinguir persistência de venda, emissão de fatura, cópia do link, confirmação de recebimento e início de download. Manter a indicação de erro ou recuperação próxima à ação.
- **Perda de foco** → Conferir menu, diálogos, avisos e pós-exclusão por teclado, sem depender de transições para concluir a mudança.
