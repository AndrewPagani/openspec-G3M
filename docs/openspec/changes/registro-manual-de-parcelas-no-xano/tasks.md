# Tarefas

## 1. Especificar e validar o novo fluxo

- [x] 1.1 Registrar no Xano como única fonte de verdade operacional, sem gateway.
- [x] 1.2 Fixar 1–24 parcelas iguais, vencimento inicial no dia local da venda
  (`America/Sao_Paulo`), vencimentos mensais e resto de centavos na última.
- [x] 1.3 Restringir baixas integrais a gerente/administrador e registrar
  usuário, horário e forma realmente recebida.
- [x] 1.4 Preservar a regra aprovada de venda paga após recebimento da primeira
  parcela e não apagar histórico ASAAS.

## 2. Schema e APIs Xano

- [x] 2.1 Adicionar tabela `venda_parcela` com venda, número, total, valor,
  vencimento, estado local, timestamp/autor da baixa e forma recebida; incluir
  índices/uniquidade.
- [x] 2.2 Estender `POST /vendas` para receber `numero_parcelas` e gravar
  venda/itens/reservas/parcelas atomicamente, com divisão exata em centavos.
- [x] 2.3 Atualizar `GET /vendas/{id}/pagamento` para retornar o cronograma
  local e somatórios, preservando claramente qualquer histórico ASAAS legado.
- [x] 2.4 Criar `POST /vendas/{id}/parcelas/{parcela_id}/receber`, exigindo
  gerente/administrador, parcela pendente e forma de pagamento existente;
  registrar baixa autoritativa no servidor, idempotente e integral.
- [x] 2.5 Atualizar cancelamento para encerrar parcelas pendentes e restaurar
  estoque dentro da mesma transação, sem chamadas externas, e impedir
  cancelamento de venda com parcela recebida.
- [x] 2.6 Neutralizar sem perda de dados a geração de link, reconciliação e
  processamento de Webhook ASAAS para impedir efeitos no novo fluxo.
- [x] 2.7 Atualizar indicadores para contar baixa manual por data de
  recebimento e nunca tratar parcela pendente ou registro legado ambíguo como
  dinheiro recebido.

## 3. Aplicação e documentação

- [x] 3.1 Trocar campo de máximo de parcelas por número de parcelas escolhido
  em toda venda, com cronograma e valores apresentados ao usuário.
- [x] 3.2 Remover ação/URL “Gerar link ASAAS”; mostrar cronograma local e baixa
  de parcela somente a gerente/administrador.
- [x] 3.3 Mostrar estado, vencimento, valor, forma recebida, data e ID do
  usuário que registrou a baixa, sem expor IDs de integração.
- [x] 3.4 Atualizar contrato API, instruções de execução e checklist de
  prontidão, identificando claramente as funções sem integração bancária.

## 4. Verificação e publicação

- [ ] 4.1 Testar divisão/resto em centavos, valor insuficiente, limites de
  parcelas e datas locais incluindo fim de mês/ano bissexto.
- [ ] 4.2 Testar gerente/administrador versus vendedor, forma inválida, baixa
  repetida, parcela cancelada, pagamento integral e primeira parcela.
- [ ] 4.3 Testar transação de cancelamento/liberação e concorrência de estoque.
- [x] 4.4 Confirmar que nenhum endpoint/app inicia chamadas ASAAS e que dados
  históricos permanecem preservados.
- [ ] 4.5 Resolver configuração de autenticação dos testes Xano e rodar os
  cenários protegidos; executar `unittest` local e `openspec validate --all`.
- [x] 4.6 Gerar `workspace push --dry-run`, mostrar as mudanças ao usuário e
  aguardar autorização explícita antes de publicar qualquer objeto Xano.
