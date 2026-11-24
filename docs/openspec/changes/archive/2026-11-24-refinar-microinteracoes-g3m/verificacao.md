# Verificação da implementação

## Referências

As capturas de Nova venda, Detalhe do cliente e Dashboard foram feitas no Microsoft Edge em 1440 × 900 e 390 × 900. As referências, a comparação e os estados de interação estão em `.impeccable/review/microinteracoes/`, diretório local ignorado pelo Git.

A revisão comparou o resumo da venda, o menu ativo e o cartão de cliente. O cartão e o seletor de cliente passaram a usar as cores de superfície e texto do tema escuro. Os rótulos do cartão apresentaram contraste de 6,96:1 no tema escuro e 7,58:1 no claro. O movimento reduzido preserva as mensagens de mudança de item, registro da venda e confirmação de pagamento. Esses estados apareceram sem animação no teste com a preferência ativa.

## Cenários verificados

- **Venda:** adição e remoção de veículo e peça, repetição de seleção, total, falha na geração da cobrança, recuperação do link com um único pedido de criação, cópia aceita e recusada, consulta com status igual e confirmação de pagamento.
- **Cadastros e navegação:** validação de campos, rejeição e confirmação de cadastro, edição de cliente durante carga progressiva, exclusão com retorno de foco, personalização salva, troca de rota com consulta pendente e troca de conta.
- **Dashboard:** confirmação dos filtros, progresso, falha e início do download. A suíte do Excel verificou os arquivos e permissões de Vendedor, Gerente e Administrador.

## Desempenho

Comparação alternada com o commit de referência `574827e`, no Edge local a 1440 × 900, com atraso de 350 ms nas respostas simuladas. A navegação foi medida do clique em **Clientes** no Dashboard até a primeira linha da lista ficar visível. A rolagem percorreu o Dashboard com gráficos preenchidos por 48 quadros, usando o percentil 94 dos intervalos entre quadros. As medianas desconsideram a primeira passagem de cada série.

| Cenário | Amostras por versão | Navegação antes | Navegação depois | Rolagem antes | Rolagem depois |
| --- | ---: | ---: | ---: | ---: | ---: |
| Navegação sem limitação de CPU e rolagem com CPU 4× mais lenta | 5 | 963,5 ms | 1.007,0 ms | 27,4 ms | 31,2 ms |
| Navegação e rolagem com CPU 4× mais lenta | 6 | 1.884,5 ms | 2.402,7 ms | 42,0 ms | 44,2 ms |

A primeira linha de Clientes variou entre 137 e 990 ms na referência, com passagens em que o navegador mostrou o dado da visita anterior à rota. A suíte funcional também navegou durante consultas pendentes e verificou o conteúdo da rota ativa. As séries tiveram amostras sobrepostas, com medianas maiores após a mudança. A medição inclui o servidor de desenvolvimento e o atraso simulado, e registra o custo observado nesse ambiente.

## Verificações técnicas

- `python -m unittest discover -s tests` passou com 127 testes.
- As suítes de navegador usaram o backend de teste, que substitui as chamadas ao Xano e ao ASAAS por respostas controladas.
- O Ruff encontrou os mesmos 44 apontamentos nos arquivos alterados em comparação com `HEAD`.
- O detector do Impeccable sinalizou três ocorrências preexistentes no CSS. São duas declarações da fonte Inter e a grade decorativa.
- O build de produção do Reflex e a validação estrita do OpenSpec passaram.
