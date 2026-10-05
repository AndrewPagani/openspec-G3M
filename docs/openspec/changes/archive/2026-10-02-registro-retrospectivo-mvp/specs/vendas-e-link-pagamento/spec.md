## Purpose

Registra o fluxo de venda disponível na aplicação: preparar itens e desconto, criar a venda/reserva no Xano e solicitar um link hospedado de pagamento ASAAS associado à venda.

## ADDED Requirements

### Requirement: Interface deve validar os dados básicos da venda
A interface MUST exigir cliente, forma de pagamento e ao menos um item; cada item MUST indicar exatamente um veículo ou uma peça, quantidade inteira positiva e identificadores positivos. O desconto informado MUST ser finito e não negativo.

#### Scenario: Itens válidos para venda
- **WHEN** o operador envia uma venda com cliente, forma de pagamento e itens válidos
- **THEN** a aplicação MUST enviar os identificadores, as quantidades e o desconto no contrato esperado pelo endpoint Xano

#### Scenario: Item inválido ou ausente
- **WHEN** um item não identifica exatamente um veículo ou uma peça, possui quantidade inválida, ou a venda não possui itens
- **THEN** a aplicação MUST rejeitar a criação e apresentar uma mensagem de validação

### Requirement: Venda deve ser criada antes de solicitar link de pagamento
A aplicação MUST criar a venda no Xano antes de solicitar o link e MUST exigir um identificador de venda retornado pela API para habilitar a etapa do link.

#### Scenario: Venda criada com identificador
- **WHEN** o Xano cria a venda e devolve seu identificador
- **THEN** a interface MUST apresentar a venda como criada/reservada e permitir solicitar o link de pagamento

### Requirement: Link ASAAS deve ser solicitado para a venda criada
A aplicação MUST solicitar o link no endpoint da venda e MUST apresentar a string não vazia devolvida em um dos campos de link reconhecidos pela integração. Para pagamento selecionado por cartão, MUST enviar o máximo de parcelas informado após validar que seja inteiro positivo.

#### Scenario: Link de pagamento criado
- **WHEN** o Xano devolve uma string de link de pagamento hospedado
- **THEN** a interface MUST mostrar o link como navegação externa e informar a validade prevista de 30 dias conforme o contrato da integração

#### Scenario: Link não é devolvido
- **WHEN** a API não retorna uma string de link não vazia nos campos reconhecidos
- **THEN** a interface MUST exibir erro explícito e MUST NOT apresentar a operação como link criado

### Requirement: Criação do link não deve ser apresentada como confirmação de pagamento
A interface MUST distinguir a criação da reserva e do link de uma confirmação de pagamento, que depende da confirmação do backend/ASAAS.

#### Scenario: Link criado mas pagamento pendente
- **WHEN** o link é criado e ainda não há confirmação de pagamento recebida
- **THEN** a aplicação MUST informar somente que o link foi gerado e MUST NOT afirmar que a venda foi paga
