## Context

O MVP usa Python/Reflex na interface e Xano para autenticação, regras de negócio, persistência e APIs. As fontes consultadas incluem o app e seus testes, o contrato de API, o escopo operacional, a verificação de prontidão do Xano e os scripts de schema. Elas não são equivalentes: scripts locais descrevem schema; contratos descrevem comportamento desejado; testes locais cobrem somente lógica do app; a verificação de prontidão registra falhas observadas no workspace em uma data específica.

## Goals / Non-Goals

**Goals:**

- Consolidar requisitos duplicados em capabilities OpenSpec existentes.
- Alinhar ciclo de venda, desconto, autorização e estoque ao contrato de API registrado.
- Marcar requisitos ainda não aprovados ou validados sem declará-los concluídos.
- Manter o uso de ASAAS hospedado, com confirmação autoritativa e segredos somente no Xano.

**Non-Goals:**

- Implementar ou publicar APIs, regras, schema ou segredos no Xano.
- Considerar testes unitários locais como prova de autorização, atomicidade ou conciliação remota.
- Implementar gateways diferentes do ASAAS, CRUD de permissões, auditoria genérica persistida, histórico de estoque, multiunidade, leads, oficina ou relatórios avançados.
- Arquivar a mudança antes da aprovação das decisões e da validação das tarefas de implementação.

## Decisions

- Tratar `docs/mvp-scope.md.txt` e `docs/api-plan-mvp.md.txt` como as fontes atuais para o contrato planejado, sem confundi-las com o estado efetivamente publicado.
- Consolidar clientes, veículos e peças na capability `cadastros-e-listagens`; vendas/ASAAS em `vendas-e-link-pagamento`; métricas em `dashboard-gerencial`. Manter usuários/perfis, integridade/segurança e prontidão como capabilities próprias.
- Usar o campo existente `peca.qtd_disp` como saldo disponível único no MVP. A reserva reduz esse saldo; cancelamento/expiração pendente o restaura uma vez. Contadores total/reservado/vendido exigem uma decisão e mudança de schema próprias.
- Considerar o fluxo local registrado `Reservado -> Paga -> Concluída`, ou `Reservado -> Cancelada/Expirada`. Veículo passa a vendido na entrega de venda paga, não ao criar a reserva.
- Cancelamento e expiração liberam apenas cobrança pendente, depois de confirmar que ela não pode mais ser paga. Estorno de venda paga fica fora do MVP.
- Não exigir auditoria genérica nem metadados não presentes no schema atual. O pagamento usa eventos de pagamento; cancelamento usa os campos próprios da venda. Proteção de dados e autorização permanecem requisitos do backend.
- A semântica de permitir entrega após a primeira parcela recebida está documentada como proposta do escopo, mas requer aprovação explícita por seu risco comercial antes da implementação.
- Descrever filtros, séries e cálculos do dashboard como contrato-alvo; a auditoria do workspace registrou filtros sem efeito, séries ausentes e agregação não escalável.

## Risks / Trade-offs

- [Documentação pode divergir do runtime do Xano] → validar rotas autenticadas e comportamento publicado antes do archive.
- [Cancelamento externo pode deixar uma cobrança pagável] → manter reserva se cancelamento/reconciliação ASAAS for inconclusivo.
- [A primeira parcela recebida não quita uma venda parcelada] → aprovação comercial explícita e registro separado de cada cobrança/parcela.
- [Modelo de saldo único oferece menos rastreabilidade que movimentos] → manter o escopo atual e abrir mudança separada se a operação exigir livro de estoque.
- [Indicadores podem crescer com o volume] → exigir filtros aplicados, agregações no backend, paginação e limite de período aprovado.

## Migration Plan

1. Aprovar campos, permissões, status, saldo, desconto, cancelamento, política de parcela e limites operacionais.
2. Implementar correções e contratos nas APIs Xano e na integração ASAAS.
3. Executar testes de API/workflow no Sandbox e testes de concorrência, idempotência, privacidade e desempenho.
4. Confirmar os resultados contra o workspace publicado, atualizar as tarefas e revisar os deltas.
5. Arquivar somente após os passos anteriores estarem concluídos; o archive sincronizará os três deltas existentes e criará as três capabilities novas.

Rollback: se a implementação divergir do contrato ou um teste falhar, manter a mudança ativa, corrigir a especificação/implementação e repetir a validação; não arquivar nem marcar tarefas como concluídas por evidência apenas local.
