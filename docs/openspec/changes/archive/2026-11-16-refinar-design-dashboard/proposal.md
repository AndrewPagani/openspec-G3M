## Why

O dashboard mantém a identidade escura do sistema, mas apresenta cores avulsas, gráficos com formatação genérica e textos técnicos que dificultam a leitura dos indicadores. O refinamento deve tornar a tela profissional, organizada e coerente com as demais páginas, preservando os dados e os fluxos existentes.

## What Changes

- Organizar cabeçalho, período, filtros e ações; distinguir indicadores de vendas no período de informações de estoque atual.
- Padronizar hierarquia tipográfica, espaçamentos, superfícies e cores com a identidade existente: Inter, tema escuro, azul principal e marca G3M.
- Refinar gráficos com unidades explícitas, reais em formato brasileiro, contagens inteiras, tooltips legíveis, categorias identificáveis e cores estáveis.
- Revisar títulos, descrições e estados vazios com linguagem voltada ao usuário, preservando a distinção entre erro, resposta incompleta e ausência de registros.
- Validar a leitura, acessibilidade e organização nas resoluções previstas e em telas estreitas.
- Registrar a divergência do ticket médio entre cálculo local e spec. Sua correção financeira não será incluída silenciosamente no trabalho visual.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `dashboard-gerencial`: acrescentar critérios verificáveis de identidade visual, organização, legibilidade dos gráficos e clareza dos textos, preservando os requisitos atuais de dados e autorização.

## Impact

- Implementação prevista em `app/pages/gerenciamento.py` e estilos específicos do dashboard em `assets/styles.css`; adaptações de apresentação em `app/state/dashboard_state.py` somente se necessárias à formatação e às cores.
- Nenhuma nova dependência, endpoint, publicação Xano, migração de banco ou alteração da integração ASAAS.
- Preservar filtros e IDs originais, exportação CSV, agrupamentos temporais, visibilidade por perfil e valores financeiros. A API remota não foi revalidada nesta exploração; os achados são de código e documentação locais.
- A interface e a API permanecem sem alterações nesta etapa. Impeccable deverá orientar a implementação e a revisão visual futuras.
