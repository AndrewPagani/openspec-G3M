## Why

O MVP já possui uma aplicação Reflex conectada ao contrato de APIs do Xano, fluxos de login, cadastros, vendas e indicadores. Esses comportamentos foram implementados incrementalmente, mas ainda não estão registrados como uma especificação OpenSpec consolidada; registrar o estado real facilita manutenção e evidencia o que depende de configuração ou validação externa.

## What Changes

- Registrar os comportamentos existentes de autenticação e chamadas autenticadas ao Xano.
- Registrar as listagens e formulários de clientes, veículos e peças, incluindo a identificação de clientes por nome/CPF e a exibição de imagem, ano e preço dos veículos.
- Registrar o fluxo de criação/reserva de venda e solicitação de link de pagamento ASAAS, distinguindo-o da confirmação real de pagamento.
- Registrar o dashboard, os filtros e a apresentação de indicadores por perfil, sem declarar como concluídas integrações ou séries que dependem de contratos publicados e validados no Xano.
- Arquivar esta mudança retrospectiva somente após revisar o registro contra o código, testes e documentação disponíveis.

## Capabilities

### New Capabilities

- `integracao-xano`: cliente HTTP, roteamento por grupo, autenticação Bearer, sessão e tratamento de erros utilizados pela interface.
- `cadastros-e-listagens`: listagem e formulários de clientes, veículos e peças, com resumo Nome - CPF e apresentação de veículo com imagem opcional, ano e valor.
- `vendas-e-link-pagamento`: criação de venda/reserva e solicitação de link hospedado de pagamento ASAAS, sem afirmar confirmação de pagamento não verificada.
- `dashboard-gerencial`: indicadores, filtros e visibilidade por perfil conforme dados fornecidos pelo endpoint do Xano.

### Modified Capabilities

Nenhuma. A mudança registra capacidades implementadas como baseline e não altera requisitos da mudança ativa `definir-nucleo-do-dominio`.

## Impact

- Código existente em `app/`, principalmente páginas, estados e serviços de Xano.
- APIs e dados publicados no workspace Xano, cuja disponibilidade e contrato precisam ser validados no próprio ambiente.
- Testes existentes em `tests/` e documentação funcional em `docs/`.
- Nenhuma dependência ou schema remoto será alterado por esta mudança de documentação.
