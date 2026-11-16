## Why
O formulário cria parcelas manuais e exige uma forma de pagamento que o comprador deve escolher no ASAAS. O app bloqueia o link e o webhook está desativado, deixando criação, cobrança e recebimento desconectados.

## What Changes
- Manter seleção visual de veículos e peças; remover desconto, forma e parcelas da criação.
- Criar venda/reserva e depois fatura única ASAAS, permitindo repetir somente a etapa de cobrança.
- Cadastrar/recuperar cliente ASAAS sem notificações e persistir invoice_url em asaas_cobranca.
- Confirmar recebimento por webhook autenticado e consulta autoritativa, preservando histórico manual.
- Permitir vendedor nas próprias vendas e gerente/administrador em todas, conforme resposta expressa do usuário.

## Capabilities
### New Capabilities
- `venda-com-fatura-asaas`: criação e acompanhamento de venda com fatura, sem e-mail.

## Impact
Reflex: vendas, autenticação/perfis, cliente HTTP e testes. Xano: schema de venda/cobrança, funções ASAAS, clientes, vendas, webhook, cancelamento e indicadores. Configuração de ambiente e webhook permanece no Xano. Publicação e testes autenticados devem ser reportados separadamente da implementação local.
