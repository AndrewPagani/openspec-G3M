## MODIFIED Requirements

### Requirement: Falhas auxiliares de vendas não devem impedir a listagem de clientes

Quando a consulta de clientes for bem-sucedida, a tela MUST preservar os clientes mesmo que a consulta auxiliar de vendas falhe em qualquer página ou retorne formato inválido. A tela MUST manter os indicadores derivados exclusivamente de clientes e apresentar última atividade e compras pendentes como indisponíveis, com aviso específico. MUST NOT apresentar zero pendências ou ausência de compras como se fossem dados confirmados quando vendas não puder ser consultada. Uma nova consulta bem-sucedida MUST remover o aviso e restaurar os dados derivados de vendas. Falhas na consulta principal de clientes MUST continuar sendo apresentadas como erro da listagem. Os clientes válidos MUST ser apresentados sem aguardar a conclusão da consulta auxiliar de vendas. Enquanto essa consulta estiver em andamento, seus indicadores MUST ser identificados como pendentes; resultados parciais de vendas MUST NOT ser apresentados como indicadores completos.

#### Scenario: Clientes disponíveis e vendas indisponíveis
- **WHEN** clientes retorna dados válidos e vendas falha
- **THEN** a lista de clientes MUST permanecer visível, com aviso restrito aos dados derivados de vendas

#### Scenario: Página subsequente de vendas falha
- **WHEN** a primeira página de vendas é carregada e uma página seguinte falha
- **THEN** a tela MUST preservar clientes e MUST NOT apresentar indicadores de vendas parciais como completos

#### Scenario: Vendas volta a responder
- **WHEN** uma nova carga de clientes e vendas é bem-sucedida
- **THEN** o aviso MUST ser removido e os indicadores de vendas MUST voltar a ser apresentados

#### Scenario: Clientes carregados antes das vendas auxiliares
- **WHEN** clientes retorna registros válidos e a consulta auxiliar de vendas permanece pendente
- **THEN** os clientes MUST estar disponíveis para leitura e interação, com seus indicadores auxiliares identificados como pendentes e sem zero ou ausência de compras presumidos

## ADDED Requirements

### Requirement: Coleções apresentam progresso sem declarar carga parcial como completa

As listagens de clientes, veículos e peças MUST apresentar a primeira página válida antes da conclusão das demais páginas informadas e MUST continuar a carga integral prevista para cada listagem. Enquanto houver páginas pendentes, MUST informar que os dados estão parciais. Totais, indicadores e resultados de busca que dependem da coleção completa MUST NOT ser apresentados como completos durante essa etapa. Uma resposta obrigatória inválida MUST ser diferenciada de uma lista válida vazia.

#### Scenario: Primeira página de veículos disponível
- **WHEN** a API retorna a primeira página de veículos e informa páginas adicionais ainda pendentes
- **THEN** os veículos dessa página MUST aparecer com identificação de carga em andamento e a aplicação MUST continuar buscando as demais páginas antes de apresentar a lista como completa

#### Scenario: Falha em página posterior da coleção principal
- **WHEN** uma página posterior de clientes, veículos ou peças falha após registros válidos já terem sido apresentados
- **THEN** a tela MUST manter esses registros identificados como incompletos, informar a falha e permitir nova consulta explícita, sem anunciar sucesso da carga integral

#### Scenario: Busca não encontra registros enquanto há páginas pendentes
- **WHEN** o texto de busca não corresponde aos registros carregados e ainda existem páginas pendentes
- **THEN** a tela MUST informar que a busca está sendo aplicada a uma coleção ainda incompleta e MUST NOT declarar ausência definitiva de correspondências

#### Scenario: Coleção terminou de carregar
- **WHEN** todas as páginas informadas retornam registros válidos
- **THEN** a tela MUST remover a indicação de parcialidade e apresentar busca, ordenação, paginação visual e indicadores locais sobre a coleção completa

#### Scenario: Primeira página válida vazia
- **WHEN** a API devolve uma coleção válida sem registros e sem páginas adicionais
- **THEN** a tela MUST apresentar o estado vazio final, sem conservar registros de outra consulta ou manter carregamento indefinido
