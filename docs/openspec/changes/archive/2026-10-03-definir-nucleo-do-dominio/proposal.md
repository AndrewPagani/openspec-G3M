# Proposta: Definir núcleo do domínio do MVP

## Why

O projeto possui domínio documentado, aplicativo Reflex, schema Xano local/publicado e contratos planejados, mas as regras estão espalhadas e alguns documentos divergem sobre estoque, estados, pagamentos e capacidades operacionais. A consolidação cria requisitos verificáveis, separa decisões registradas de validações ainda pendentes e evita arquivar como concluídas regras não comprovadas no Xano.

## What Changes

- Consolidar cadastro, listagem, disponibilidade de veículos e saldo de peças na capacidade existente `cadastros-e-listagens`.
- Consolidar o ciclo de vendas, reserva, link hospedado ASAAS, confirmação, entrega, cancelamento e expiração em `vendas-e-link-pagamento`.
- Consolidar métricas, filtros, escopo por perfil e limites operacionais em `dashboard-gerencial`.
- Definir separadamente usuários/perfis, integridade/segurança e prontidão operacional do MVP.
- Alinhar requisitos ao schema e ao contrato de API atuais, identificando regras cuja aprovação ou validação publicada ainda está pendente.
- Não declarar como implementados comportamentos de backend, ASAAS ou Xano que ainda não foram testados no ambiente publicado.

## Capabilities

### Modified Capabilities

- `cadastros-e-listagens`: incorporar requisitos de clientes, veículos, peças, disponibilidade e saldo de estoque.
- `dashboard-gerencial`: incorporar métricas de MVP, segurança por perfil, filtros efetivos e agregação escalável.
- `vendas-e-link-pagamento`: incorporar estados, preço/desconto no backend, confirmação ASAAS, entrega e cancelamento pendente idempotente.

### New Capabilities

- `usuarios-e-perfis`: definir autorização do MVP por perfil, ação e recurso.
- `integridade-e-seguranca`: definir atomicidade, idempotência, integridade e proteção de dados.
- `prontidao-do-mvp`: registrar limites do schema, dependências, validação e critérios de conclusão.

## Impact

- Especificações principais em `docs/openspec/specs/` serão atualizadas pelo archive após aprovações, implementação e validação.
- A mudança não implementa nem modifica código do app, APIs Xano, dados, segredos ou schema remoto.
- As decisões e bloqueios pendentes permanecem como tarefas não concluídas; a mudança não deve ser arquivada enquanto seu critério de conclusão não for atendido.

## Referências

- Escopo, pendências e critérios de aceite: [mvp-scope.md.txt](../../../../mvp-scope.md.txt).
- Contrato de rotas e regras planejadas: [api-plan-mvp.md.txt](../../../../api-plan-mvp.md.txt).
- Riscos observados no Xano: [xano-api-readiness-check.md](../../../../xano-api-readiness-check.md).
- Schema base: [mvp-schema.xs](../../../../xanoscript/mvp-schema.xs).
- Migração de pagamento: [asaas-payment-migration.xs](../../../../xanoscript/asaas-payment-migration.xs).
