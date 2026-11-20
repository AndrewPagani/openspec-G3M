# Associação do cliente na listagem de vendas

Patch do `GET /vendas` preparado a partir da leitura da branch `v1` do workspace `147643`. A tela exibe o `cliente.CNome` devolvido em cada linha. Na amostra do banco, 100 vendas tinham 98 IDs de cliente distintos e o cadastro continha 99 nomes distintos. O histórico de requisições não forneceu o corpo das respostas dessa amostra.

O endpoint passa a nomear explicitamente a venda corrente e a localizar o cliente por `venda.cliente_id` dentro dos clientes já consultados para a página. A alteração mantém a mesma estrutura de resposta, os filtros, a autorização e a paginação. Usa a forma de `find` já usada no endpoint de indicadores da mesma branch.

A prévia do CLI identificou apenas uma atualização, em `GET /vendas`. O patch foi publicado em 20/11/2026 na branch ativa `v1`. Uma nova leitura confirmou a resolução por `cliente_id` no endpoint publicado e identificou somente esse endpoint como diferente da leitura anterior.

Os quatro testes locais de consulta de vendas passaram, incluindo o mapeamento de nomes por linha. O teste remoto `nenhum filtro de data` ficou bloqueado por falta de sessão autenticada (`Unauthorized - Authentication Required`). Para confirmar os dados reais, compare `items[*].cliente.id` e `items[*].cliente.CNome` com os cadastros vinculados. Inclua duas vendas de clientes diferentes e duas vendas do mesmo cliente. Confira também a busca por nome e a visibilidade com um perfil de vendedor e outro de gerente.
