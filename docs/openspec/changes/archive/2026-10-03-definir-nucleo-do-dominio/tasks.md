# Tarefas da mudança

## 1. Consolidar especificações OpenSpec

- [x] 1.1 Consolidar clientes, veículos, peças/estoque e apresentação de cadastros em `cadastros-e-listagens`.
- [x] 1.2 Consolidar ciclo da venda e fluxo ASAAS em `vendas-e-link-pagamento`.
- [x] 1.3 Consolidar KPIs, filtros e limites de escala em `dashboard-gerencial`.
- [x] 1.4 Manter `usuarios-e-perfis`, `integridade-e-seguranca` e `prontidao-do-mvp` como capabilities separadas.
- [x] 1.5 Remover capabilities duplicadas e ajustar proposal/design ao escopo ASAAS e às regras atuais de cancelamento.
- [x] 1.6 Distinguir requisitos-alvo, contrato documentado, schema local e comportamento remoto ainda não verificado.
- [x] 1.7 Validar os seis deltas/capabilities com o CLI OpenSpec e confirmar que os merges MODIFIED apontam para requisitos existentes.

## 2. Aprovar decisões de negócio ainda abertas

- [x] 2.1 Aprovar campos obrigatórios por entidade, unicidade, inativação e compatibilidade com registros legados; decidir se o `Ano` único atual deve distinguir fabricação e modelo. Regra aprovada conforme `mvp-scope.md.txt`.
- [x] 2.2 Aprovar formalmente a matriz de permissões do `mvp-scope.md.txt`, incluindo leitura/criação/edição por perfil e restrições de venda. Regra aprovada conforme `mvp-scope.md.txt`.
- [x] 2.3 Aprovar a máquina de estados de veículos e vendas, incluindo entrega após confirmação da primeira parcela. Regra aprovada conforme `mvp-scope.md.txt`.
- [x] 2.4 Confirmar o modelo de estoque do MVP (`qtd_disp` como saldo único), regras de reserva, ajuste, cancelamento e expiração; aprovar separadamente eventual expansão para saldos total/reservado/vendido. Regra aprovada; expansão de saldos fora do MVP.
- [x] 2.5 Aprovar política de descontos: valor monetário, faixa de zero até o valor bruto e aplicação positiva somente por gerente/administrador. Regra aprovada conforme `mvp-scope.md.txt`.
- [x] 2.6 Aprovar cancelamento somente de cobrança pendente, motivo obrigatório, idempotência e ausência de estorno de venda paga no MVP. Regra aprovada conforme `mvp-scope.md.txt`.
- [x] 2.7 Definir período máximo de dashboard e limites de consulta; confirmar paginação padrão 20/máximo 100 e filtros por recurso. Contrato aprovado conforme `api-plan-mvp.md.txt`.
- [x] 2.8 Aprovar o risco comercial de considerar a venda paga após o recebimento da primeira parcela, com parcelas subsequentes ainda pendentes. Regra aprovada conforme `mvp-scope.md.txt`.
- [x] 2.9 Definir registros de referência iniciais no Xano e decidir se haverá provedor externo para e-mail/notificações. Escopo aprovado; provedor externo fora do MVP.
- [ ] 2.10 Confirmar ambientes/credenciais ASAAS e segredo de Webhook separado, sem registrar valores secretos nos artefatos.

## 3. Implementar e corrigir contratos no Xano

- [ ] 3.1 Implementar e testar autorização por ação/recurso, derivação do vendedor pela sessão e validação de integridade.
- [ ] 3.2 Implementar unicidade, validação de campos, busca/paginação e respostas limitadas nas APIs de clientes, veículos e peças. Busca por venda (ID, cliente e vendedor) e lookups limitados à página foram publicados em `GET /vendas`; revisar e validar os demais recursos continua pendente.
- [ ] 3.3 Implementar transições de veículo e a regra de que somente entrega de venda paga marca o veículo como vendido.
- [ ] 3.4 Implementar reserva/ajuste de estoque atômicos e concorrência sem saldo negativo.
- [ ] 3.5 Implementar cálculo backend de preços/descontos, ciclo reservado-pago-concluído e cancelamento/expiração idempotentes.
- [ ] 3.6 Corrigir e testar integração ASAAS: ambiente explícito, segredos separados, reconciliação sem sucesso falso, upsert de pagamentos, Webhook deduplicado e cancelamento seguro antes de liberar recursos. Correções parciais publicadas; falta configurar variáveis no Xano e validar eventos/cancelamento em Sandbox.
- [ ] 3.7 Corrigir o endpoint de indicadores para aplicar todos os filtros, retornar séries do contrato e agregar sem carregar tabelas completas na memória.
- [ ] 3.8 Garantir paginação, limites de período, sessão expirada e sanitização de erros/logs sem expor dados sensíveis.

## 4. Validar comportamento antes de arquivar

- [ ] 4.1 Adicionar/rodar testes de API para autenticação, perfis, CRUD, busca, unicidade, filtros e paginação. Revalidado em 05/10/2026: 1 teste aprovado e 20 bloqueados por HTTP 401; `xano unit_test run --help` não oferece opção de fixture/token; configurar teste autenticado sem reduzir proteção.
- [ ] 4.2 Testar transições inválidas, venda sem item, preço congelado, desconto e autorização no backend.
- [ ] 4.3 Testar estoque concorrente, atomicidade e compensação idempotente em cancelamento/expiração.
- [ ] 4.4 Testar Sandbox ASAAS: timeout/reconciliação, primeira e demais parcelas, Webhook duplicado/fora de ordem, cobrança pendente e cancelamento. Nenhuma chamada de pagamento foi feita; credenciais/configuração e teste ponta a ponta pendentes.
- [ ] 4.5 Validar filtros, KPIs, escopo por perfil, séries vazias e desempenho do dashboard com dados representativos.
- [ ] 4.6 Confirmar no workspace publicado que contratos e regras correspondem a estas specs; testes locais do app não substituem essa validação. Em 05/10/2026, o dry-run confirmou os cinco endpoints alterados sincronizados e aceitos sem erro de sintaxe; validar todo o contrato em runtime permanece pendente.
- [ ] 4.7 Revisar que nenhuma capacidade fora do MVP foi incluída e que todas as decisões abertas foram aprovadas.
- [ ] 4.8 Arquivar somente após concluir as tarefas de aprovação, implementação e validação e sincronizar os deltas.
