## Context
Usar as definições lidas do workspace 147643/v1 nesta aplicação, sem reenviar backups antigos. A solicitação de apply autoriza implementar as decisões da exploração; vendedor pode gerar/recuperar links próprios.

## Goals / Non-Goals
Implementar cobrança única com escolha de meio pelo comprador, fatura persistida e confirmação automática. Não implementar parcelamento ASAAS, cartão no app, envio de mensagens, estorno ou migração automática de vendas históricas.

## Decisions
- Interface Operate preserva shell, cores, tipografia e seletores atuais. Layout com seleção à esquerda e resumo/ação à direita; uma coluna no celular. Usar Impeccable como refinamento de superfície existente.
- Forma de pagamento da venda será anulável até recebimento; não criar ID fictício. Novas vendas usam payment_flow=ASAAS; default LEGADO preserva registros existentes.
- Cliente novo tem referência externa estável, recuperação por CPF e vínculo persistido; cadastro existente pode retomar sincronização sem duplicação. Nunca excluir automaticamente cliente local em timeout externo.
- Fatura é criada em etapa independente, com referência estável e estado persistido de tentativa; resultado ambíguo deve ser reconciliado antes de novo POST. Não emitir outra cobrança automaticamente após timeout.
- Configuração explícita ASAAS_ENV e chave ASAAS no Xano, com segredo de webhook separado ASAAS_WEBHOOK_TOKEN. Ambiente Sandbox inicial; não ler nem publicar valores de segredos.
- Webhook valida token do cabeçalho e consulta a cobrança no ASAAS; o estado atual externo é autoritativo, evitando regressão por evento atrasado. Persistir evento único e pagamento por ID externo.
- Cobrança recebida preenche pagamento e venda paga. Atualizações repetidas não repetem baixa de estoque. O estoque já é reservado na criação.
- Cancelamento bloqueia recebidos e operações ambíguas, confirma cancelamento externo antes de liberar estoque e revalida venda em transação.
- Vendas/parcelas legadas permanecem legíveis. Baixa manual fica disponível apenas no histórico LEGADO, nunca em novas vendas ASAAS.

## Risks / Trade-offs
HTTP externo e transação local não são uma transação distribuída. Tentativas ambíguas exigem reconciliação, sem repetição cega. Testes Python usam fixtures e não comprovam execução Xano; validar importação e cenários autenticados Sandbox antes de declarar integração operacional.

## Migration Plan
Preparar pacote isolado com GUIDs das definições atuais, schema aditivo e funções. Executar dry-run e revisar alterações. Não usar --delete/--truncate nem alterar segredos/ambiente remoto implicitamente. Manter os testes de backend/publicação pendentes até execução comprovada.
