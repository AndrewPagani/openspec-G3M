# venda-com-fatura-asaas Specification

## Purpose

Define o fluxo vigente de novas vendas com fatura ASAAS e escolha do meio pelo comprador, substituindo as exigências anteriores de forma, desconto e parcelas manuais na criação. Preserva a consulta do histórico LEGADO e distingue geração do link de confirmação do recebimento.

## Requirements

### Requirement: Operador cria venda e gera fatura
O sistema MUST permitir escolher cliente e veículos e/ou peças, calcular valores no backend e criar uma reserva seguida de fatura ASAAS. MUST NOT exigir forma, desconto ou parcelas no formulário inicial. O cliente MUST escolher o meio na fatura. O link MUST ser persistido em asaas_cobranca.invoice_url e poder ser aberto/copiado após reabrir a venda.
#### Scenario: Falha de geração após reserva
- **WHEN** a venda existe e o ASAAS falha
- **THEN** a interface MUST preservar o ID e repetir somente a geração/recuperação da fatura

### Requirement: Cadastro integrado não envia e-mail
O Xano MUST criar ou recuperar o cliente ASAAS, persistir o vínculo na tabela `asaas_cliente` e desabilitar notificações também em clientes reutilizados. MUST NOT disparar e-mail pelo app, Xano ou ASAAS neste fluxo. Falhas ambíguas MUST ser recuperáveis sem exclusão local ou POST externo repetido cegamente.

#### Scenario: Novo cliente cadastrado
- **WHEN** o cadastro de um novo cliente é confirmado
- **THEN** `asaas_cliente` MUST conter um único vínculo entre o `cliente_id` do Xano e o `asaas_customer_id` devolvido pelo ASAAS

#### Scenario: Nova tentativa de cadastro
- **WHEN** existe cliente local ou externo após tentativa incompleta
- **THEN** o backend MUST recuperar e sincronizar esse cadastro sem duplicação

### Requirement: Recebimentos são autoritativos e idempotentes
O backend MUST validar segredo próprio do webhook, deduplicar eventos e consultar estado atual da cobrança antes de atualizar pagamento e venda. MUST NOT confirmar pagamento pelo retorno do navegador ou criação do link. Indicadores MUST considerar apenas recebimentos comprovados e preservar histórico manual separadamente.
#### Scenario: Pagamento confirma a venda de um veículo
- **WHEN** o ASAAS confirma o pagamento de uma venda com veículo reservado, inclusive se a venda também contiver peças
- **THEN** o Xano MUST marcar a venda como Paga e os veículos vinculados como Vendidos na mesma transação, processando os itens de peça sem tratá-los como veículos

#### Scenario: Evento duplicado ou atrasado
- **WHEN** o ASAAS reenvia evento ou entrega evento antigo
- **THEN** o sistema MUST manter o estado autoritativo sem duplicar recebimento nem regredir estado pago

### Requirement: Escopo, histórico e cancelamento são preservados
Vendedores MUST operar somente suas vendas; gerente/admin MUST operar todas. Novas vendas ASAAS MUST NOT aceitar baixa manual. Histórico existente MUST permanecer legível. Cancelamento MUST confirmar que a cobrança não pode mais ser paga antes de liberar recursos, e MUST bloquear venda recebida.
#### Scenario: Vendedor acessa venda de outro
- **WHEN** vendedor informa ID de outra venda
- **THEN** o backend MUST recusar sem alterar cobrança ou estoque
