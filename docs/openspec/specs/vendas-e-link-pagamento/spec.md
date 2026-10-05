# vendas-e-link-pagamento Specification

## Purpose
Registra o fluxo de venda disponível na aplicação: preparar itens e desconto, criar a venda/reserva no Xano e solicitar um link hospedado de pagamento ASAAS associado à venda.

## Requirements

### Requirement: Interface deve validar os dados básicos da venda
A interface MUST exigir cliente, forma de pagamento e ao menos um item; cada item MUST indicar exatamente um veículo ou uma peça, quantidade inteira positiva e identificadores positivos. O desconto informado MUST ser finito, não negativo e não superior ao valor bruto. O vendedor MUST NOT poder aplicar desconto maior que zero; a autorização MUST ser repetida no backend para todos os perfis.

#### Scenario: Itens válidos para venda
- **WHEN** o operador envia uma venda com cliente, forma de pagamento e itens válidos
- **THEN** a aplicação MUST enviar os identificadores, as quantidades e o desconto no contrato esperado pelo endpoint Xano

#### Scenario: Item inválido ou ausente
- **WHEN** um item não identifica exatamente um veículo ou uma peça, possui quantidade inválida, ou a venda não possui itens
- **THEN** a aplicação MUST rejeitar a criação e apresentar uma mensagem de validação

#### Scenario: Desconto inválido ou não autorizado
- **WHEN** desconto é negativo, excede o valor bruto, ou vendedor tenta aplicar desconto maior que zero
- **THEN** a aplicação MUST rejeitar a entrada e o backend MUST rejeitar qualquer requisição que contorne a validação local

### Requirement: Venda deve ser criada antes de solicitar link de pagamento
A aplicação MUST criar a venda/reserva no Xano antes de solicitar o link e MUST exigir o identificador retornado pela API. O preço unitário, bruto, desconto e valor final MUST ser calculados/congelados no backend; o `vendedor_id` MUST ser derivado da sessão, nunca confiado ao cliente.

#### Scenario: Venda criada com identificador
- **WHEN** o Xano cria a venda e devolve seu identificador
- **THEN** a interface MUST apresentar a venda como criada/reservada e permitir solicitar o link de pagamento

#### Scenario: Venda sem cliente, forma de pagamento ou item
- **WHEN** requisição de venda não tem cliente, forma de pagamento ou ao menos um item válido
- **THEN** o backend MUST rejeitar a criação sem reservar veículo ou estoque

#### Scenario: Preço do item é alterado depois da venda
- **WHEN** o preço cadastral do veículo ou peça muda após a criação da venda
- **THEN** o preço e os valores calculados da venda já registrada MUST permanecer inalterados

### Requirement: Link ASAAS deve ser solicitado para a venda criada
A aplicação MUST solicitar o link no endpoint da venda e MUST apresentar a string não vazia devolvida em um dos campos de link reconhecidos pela integração. Para pagamento selecionado por cartão, MUST enviar o máximo de parcelas informado após validar que seja inteiro positivo. O backend MUST usar configuração explícita de ambiente e credenciais secretas, nunca expor segredos ao app e persistir a referência da cobrança/link de forma idempotente.

#### Scenario: Link de pagamento criado
- **WHEN** o Xano devolve uma string de link de pagamento hospedado
- **THEN** a interface MUST mostrar o link como navegação externa e informar a validade prevista de 30 dias conforme o contrato da integração

#### Scenario: Link não é devolvido
- **WHEN** a API não retorna uma string de link não vazia nos campos reconhecidos
- **THEN** a interface MUST exibir erro explícito e MUST NOT apresentar a operação como link criado

#### Scenario: Configuração de pagamento ausente ou falha do ASAAS
- **WHEN** ambiente/segredo necessário não está configurado ou o ASAAS falha
- **THEN** o backend MUST retornar falha explícita e sanitizada sem reportar sucesso nem descartar a reserva

### Requirement: Criação do link não deve ser apresentada como confirmação de pagamento
A interface MUST distinguir a criação da reserva e do link de uma confirmação de pagamento. A venda somente pode ser marcada paga por Webhook autenticado ou conciliação com estado autoritativo do ASAAS; redirecionamento do navegador ou resposta de criação do link MUST NOT confirmar pagamento.

#### Scenario: Link criado mas pagamento pendente
- **WHEN** o link é criado e ainda não há confirmação de pagamento recebida
- **THEN** a aplicação MUST informar somente que o link foi gerado e MUST NOT afirmar que a venda foi paga

#### Scenario: Confirmação chega por Webhook duplicado
- **WHEN** o ASAAS reenvia um evento já processado
- **THEN** o backend MUST deduplicar o evento e MUST NOT duplicar pagamento, baixa de estoque ou mudança de status

### Requirement: Ciclo de vida da venda segue os estados do contrato MVP
O backend MUST controlar as transições `Reservado -> Paga -> Concluída` e `Reservado -> Cancelada` ou `Reservado -> Expirada`. A primeira parcela confirmada como recebida pelo ASAAS pode marcar a venda como paga e habilitar a entrega conforme decisão comercial registrada; `POST /vendas/:id/entregar` exige venda paga e conclui a venda. Cobranças/parcelas subsequentes permanecem registradas separadamente. Reserva expira após 30 dias sem pagamento conforme o contrato atual. Cancelamento e expiração aplicam-se a cobranças pendentes e MUST registrar motivo quando solicitados pelo operador; estorno de venda paga não faz parte do MVP. Reserva, cancelamento e expiração MUST ser atômicos/idempotentes e não liberar estoque enquanto cobranças pendentes ainda possam ser pagas. Falha de notificação por e-mail MUST NOT reverter pagamento confirmado.

#### Scenario: Primeira parcela é recebida
- **WHEN** o ASAAS confirma a primeira parcela da venda como recebida
- **THEN** o backend MUST marcar a venda como paga sem tratar parcelas subsequentes como recebidas

#### Scenario: Entrega de venda paga
- **WHEN** operador autorizado entrega venda paga
- **THEN** o backend MUST concluir a venda e marcar o veículo associado como vendido

#### Scenario: Cancelamento ou expiração de cobrança pendente
- **WHEN** gerente ou administrador cancela cobrança pendente ou a reserva expira
- **THEN** o backend MUST cancelar ou reconciliar cobranças externas pendentes antes de marcar cancelada/expirada e liberar recursos uma única vez

#### Scenario: Cancelamento sem motivo
- **WHEN** operador autorizado solicita cancelamento sem informar motivo
- **THEN** o backend MUST rejeitar a solicitação sem alterar venda, cobrança ou recursos reservados

#### Scenario: Tentativa de estorno de venda paga
- **WHEN** é solicitada a operação de cancelamento para uma venda já paga
- **THEN** o backend MUST rejeitar o estorno no MVP e MUST preservar o estado confirmado

#### Scenario: Falha na notificação após pagamento
- **WHEN** notificação por e-mail falha depois da confirmação autoritativa do pagamento
- **THEN** o pagamento MUST permanecer confirmado e a falha de notificação MUST ser reportada separadamente
