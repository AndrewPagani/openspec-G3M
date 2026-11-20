# Implementação e verificação da exportação Excel

## Contratos do Xano

Em 20/11/2026, o CLI consultou o workspace `147643` na branch `v1`, que
`xano branch list` identificou como ativa. A revisão verificou as definições
dos seis endpoints.

| Leitura | Formato e escopo na definição |
| --- | --- |
| `GET /gerenciamento/indicadores` | Objeto com `kpis`, séries de vendas e indicadores gerenciais. O vendedor é limitado às próprias vendas. |
| `GET /vendas` | `items` e `pagination`, com totais e registros ordenados por ID decrescente. O filtro de vendedor é imposto pelo Xano para o perfil Vendedor. |
| `GET /clientes` | `items` e `pagination` com totais. A resposta seleciona campos cadastrais e omite o identificador ASAAS. |
| `GET /veiculos` | `items` e `pagination` com totais. O parâmetro opcional `somente_disponiveis` fica ausente. |
| `GET /pecas` | `items` e `pagination` com totais. Com `somente_disponiveis` ausente, a consulta inclui saldo zero. |
| `GET /usuarios` | Lista com autorização remota exclusiva para Administrador. A exportação seleciona os campos cadastrais e de perfil. |

Indicadores e Vendas interpretam datas sem hora como `00:00:00Z` e
`23:59:59Z`, com ambas as comparações inclusivas. A fixture cobriu o início do
dia, o último segundo exato, 1 ms depois desse segundo e a meia-noite
seguinte. Ambos os endpoints aplicam status, vendedor e forma de pagamento à
população de vendas. Tipo de item atua em `venda_item`. Status do veículo
altera o recorte dos indicadores de disponibilidade. O valor líquido recebido
usa a data do recebimento, enquanto as linhas da aba Vendas usam a data da venda.

A revisão também encontrou o bloqueio de Administrador em Indicadores.
A prévia do CLI mostrou apenas `UPDATE query indicadores GET`. A publicação
atualizou um documento e a leitura posterior confirmou a autorização para
Administrador no ramo gerencial. A definição de Vendas permaneceu com seu
filtro de vendedor autenticado. O patch está em
[`patch-dashboard-admin`](../../../../../xanoscript/patch-dashboard-admin/api/gerenciamento/indicadores_GET.xs).

O teste existente de Indicadores executado pelo CLI retornou
`Unauthorized - Authentication Required`. A publicação e as regras
descritas acima foram verificadas na definição. O download autenticado com
registros reais permanece pendente de uma sessão de aplicação.

## Execução local

Playwright e Edge testaram os três perfis com respostas controladas do Xano.
Os relatórios incluíram entre 104 e 106 vendas, 1.001 clientes em 11 páginas,
um veículo reservado e uma peça de saldo zero. A aba Usuários apareceu
somente para Administrador. O leitor OpenPyXL conferiu a presença das abas,
valores monetários, percentuais, datas e preservação de texto, incluindo
CPF com zero inicial. Campos sem permissão de exportação foram verificados
com valores sentinela na resposta.

Os arquivos ficaram entre 37 e 39 kB e os downloads levaram de 1 a 4 segundos
nas execuções locais observadas. A navegação funcionou durante a exportação.
Falha em página posterior, falha de tempo simulada e troca de conta foram
exercitadas, assim como nova tentativa após falha e execução via teclado.
O relatório tem limites de 20.000 linhas por coleção ou série, 1 MB de
arquivo e 90 segundos por tentativa. A entrega usa o evento de download
da sessão e o arquivo é montado em memória.

Para repetir a verificação, inicie `tests/browser/navigation_fixture.py` e o
frontend local na porta 3000. Os cenários executáveis estão em
[`excel_browser.py`](../../../../../tests/browser/excel_browser.py) e
[`navigation_browser.py`](../../../../../tests/browser/navigation_browser.py).
O primeiro requer Playwright, Edge e OpenPyXL instalados no ambiente de teste.

Os 126 testes Python, o lint dos arquivos novos e da interface alterada, o
build de produção do Reflex e a validação estrita do OpenSpec passaram.
As 58 ocorrências do lint global em `app/` são preexistentes. O Impeccable
apontou a fonte e o fundo gráfico já presentes no CSS compartilhado. A revisão
visual do novo botão e do aviso de exportação cobriu desktop, viewport de
390 px e os temas claro e escuro.

## Revisão do recorte histórico

Para o filtro com início em 01/11/2000, a Metadata API retornou 101 vendas
desde essa data, três com `cliente_id = 0`. O Dashboard conta vendas
diretamente e a listagem usava uma junção com clientes. O patch
[`patch-vendas-historico`](../../../../../xanoscript/patch-vendas-historico/api/vendas/vendas_GET.xs)
consulta as vendas sem exigir a correspondência, resolve a busca por cliente
separadamente e prioriza `itemsTotal` na paginação. No Excel, a coluna
Cliente fica em branco quando o vínculo está ausente. O teste local gerou
o arquivo com 101 vendas em duas páginas, incluindo as três vendas sem
cliente. A validação em sessão autenticada continua necessária para
conferir o resultado com o perfil e os filtros do operador.
