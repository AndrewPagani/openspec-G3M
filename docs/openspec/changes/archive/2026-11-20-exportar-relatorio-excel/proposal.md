## Why

O CSV do Dashboard exporta as datas e sete indicadores. A equipe precisa de um arquivo Excel que reúna também as séries do painel e as listagens operacionais, com valores prontos para análise e o mesmo acesso concedido no aplicativo.

## What Changes

- **BREAKING** para consumidores do arquivo anterior. Substituir o botão e o download CSV do Dashboard por **Exportar Excel**, com um único arquivo `.xlsx`.
- Incluir as abas Dashboard, Vendas, Clientes, Veículos e Peças. Incluir Usuários apenas para administradores. Formulários e telas de detalhe fazem parte de suas respectivas áreas. Configurações fica fora do arquivo.
- Registrar o período e os filtros aplicados no painel. A aba Vendas usa o mesmo recorte das métricas de vendas, e os filtros por tipo de item e status do veículo mantêm seu escopo nas séries de itens e estoque. Os cadastros incluem todas as páginas acessíveis ao perfil.
- Disponibilizar os dados dos gráficos em tabelas editáveis e informar o progresso da geração. Liberar o download após validar todas as abas esperadas.

## Capabilities

### New Capabilities

- `exportacao-relatorio-excel` — Conteúdo, filtros, permissões e entrega do relatório Excel.

### Modified Capabilities

- `dashboard-gerencial` — A ação secundária de exportação passa de CSV para Excel.

## Impact

Afeta a interface e o estado do Dashboard, o serviço de leitura e geração do relatório, as dependências Python e os testes de exportação. O desenho parte dos contratos de leitura existentes do Xano e da autenticação do operador. A exportação cobre dados tabulares autorizados. Imagens incorporadas, gráficos nativos do Excel, links de cobrança, dados detalhados de parcelas, Configurações e envio de arquivos por e-mail ficam fora do escopo inicial.
