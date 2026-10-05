# Design: Parcelas locais com baixa manual

## Contexto

O app Reflex chama o Xano, que já persiste vendas e linhas de pagamento ligadas
ao ASAAS. Não será usado checkout nem processador. A confirmação manual no
Xano é um registro administrativo do que ocorreu externamente; ela não prova
que dinheiro foi liquidado e não pode ser descrita como integração bancária.

## Decisões

1. **Fonte de verdade:** venda, plano, estado de parcela e baixa ficam no Xano.
   O usuário informa a quantidade de parcelas (1–24) na criação da venda.
2. **Cronograma:** dividir `Valor_final` em centavos por parcelas iguais; a
   última parcela recebe qualquer centavo restante. A primeira vence no dia da
   venda no fuso `America/Sao_Paulo`; as seguintes vencem mensalmente no mesmo
   dia local, usando o último dia do mês quando esse dia não existir. Rejeitar
   planos cujo total em centavos seja menor que a quantidade de parcelas, para
   que nenhuma parcela tenha valor zero.
3. **Baixa:** gerente/administrador pode confirmar uma parcela pendente uma
   única vez, pelo valor integral. Exigir forma de pagamento recebida do
   catálogo. Registrar usuário autenticado e timestamp do Xano. Uma repetição
   retorna o estado atual sem duplicar o recebimento.
4. **Estados:** parcela local `PENDENTE`, `RECEBIDA` ou `CANCELADA`. A primeira
   parcela recebida muda `Reservado` para `Paga`; demais parcelas não repetem a
   transição. Venda `Paga` pode ser entregue conforme regra aprovada.
5. **Cancelamento:** só venda `Reservado` sem parcela recebida pode ser
   cancelada. Cancelar parcelas pendentes e restaurar veículo/peças na mesma
   transação local, idempotentemente; nenhuma chamada HTTP externa.
6. **Migração compatível:** introduzir tabela local `venda_parcela` para evitar
   reinterpretar os registros `pagamento` existentes. Manter registros,
   referências, segredos e campos ASAAS legados sem uso pelo novo fluxo. Não
   apagar a rota/tabela de Webhook nem segredos sem plano separado e inspeção
   de uso; a rota antiga deve deixar de produzir efeitos de pagamento.
7. **Contrato:** criação da venda recebe `numero_parcelas`; `GET
   /vendas/{id}/pagamento` lista parcelas locais e totais; nova rota
   `POST /vendas/{id}/parcelas/{parcela_id}/receber` valida cargo e forma real
   recebida. A resposta distingue parcela prevista de baixa manual confirmada.

## Concorrência e integridade

- Criar venda, itens, reservas e todas as parcelas na mesma transação Xano.
- Identificar parcela por chave única `(venda_id, numero_parcela)`.
- Rejeitar baixa para parcelas canceladas e vendas canceladas/expiradas; para
  repetição de baixa já confirmada, devolver o registro persistido sem alterar
  autor, horário ou forma recebida, inclusive após revalidar o estado dentro da
  transação.
- O backend é a autoridade para papel/permissão, datas, valores, estado e
  forma de pagamento. O app nunca escolhe `recebido_por` nem o timestamp.
- No teste de concorrência, duas criações não podem reservar o mesmo veículo
  ou consumir mais peças que o saldo; esta alteração não deve mascarar a
  pendência preexistente de reserva atômica.

## Rollout e compatibilidade

1. Criar a tabela nova sem importar registros nem segredos.
2. Atualizar APIs e app para usar parcelas locais.
3. Desativar efeitos das rotas antigas de criação/conciliação ASAAS e impedir
   que Webhooks antigos alterem vendas após a troca.
4. Comparar a prévia Xano com os arquivos, apresentar ao usuário e só publicar
   após autorização.
5. Manter dados ASAAS antigos acessíveis como histórico legado; não converter
   nem apagar silenciosamente. Contagens e política de exibição de histórico
   devem ser verificadas antes de liberar a versão.

## Riscos

- A baixa manual pode registrar recebimento incorreto; mitigar com controle de
  cargo, autor e horário e deixar explícito que confirmação é administrativa.
- Os endpoints Xano existentes exigem autenticação e os testes cadastrados
  retornam 401 sem uma sessão configurada. Essa validação é bloqueadora e não
  será contornada removendo autenticação.
- A reserva concorrente de estoque e o dashboard escalável permanecem
  pendências separadas até serem corrigidas e testadas.
