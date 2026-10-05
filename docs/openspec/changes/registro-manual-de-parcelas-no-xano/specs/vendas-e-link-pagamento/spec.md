## MODIFIED Requirements

### Requirement: Interface deve validar os dados básicos da venda
A interface MUST exigir cliente, forma de pagamento, quantidade de parcelas entre 1 e 24 e ao menos um item; cada item MUST indicar exatamente um veículo ou uma peça, quantidade inteira positiva e identificadores positivos. O desconto informado MUST ser finito e não negativo.

#### Scenario: Itens válidos para venda
- **WHEN** o operador envia uma venda com cliente, forma de pagamento, número de parcelas e itens válidos
- **THEN** a aplicação MUST enviar os identificadores, quantidades, desconto e quantidade de parcelas no contrato esperado pelo endpoint Xano

#### Scenario: Item inválido ou ausente
- **WHEN** um item não identifica exatamente um veículo ou uma peça, possui quantidade inválida, ou a venda não possui itens
- **THEN** a aplicação MUST rejeitar a criação e apresentar uma mensagem de validação

#### Scenario: Desconto inválido ou não autorizado
- **WHEN** desconto é negativo, excede o valor bruto, ou vendedor tenta aplicar desconto maior que zero
- **THEN** a aplicação MUST rejeitar a entrada e o backend MUST rejeitar qualquer requisição que contorne a validação local

#### Scenario: Quantidade de parcelas inválida
- **WHEN** a quantidade de parcelas não é um inteiro entre 1 e 24
- **THEN** a aplicação MUST rejeitar a entrada e o backend MUST rejeitar requisição equivalente sem reservar recursos

## ADDED Requirements

### Requirement: Venda e parcelas seguem os estados do contrato MVP
O backend MUST controlar `Reservado -> Paga -> Concluída` e `Reservado -> Cancelada` ou `Reservado -> Expirada`. O recebimento manual integral da primeira parcela pode marcar a venda como paga e habilitar a entrega conforme decisão comercial aprovada; parcelas subsequentes permanecem separadas e pendentes até cada baixa. `POST /vendas/:id/entregar` exige venda paga e conclui a venda. Cada plano MUST ser criado no Xano com a venda e as reservas, em uma transação, para 1–24 parcelas positivas em centavos, distribuindo qualquer resto de centavos na última parcela. O valor final da venda MUST ter precisão máxima de centavos; o backend MUST rejeitar valores não representáveis em centavos e planos cujo total em centavos seja menor que a quantidade de parcelas. A primeira vence na data local da venda em `America/Sao_Paulo`; parcelas seguintes vencem mensalmente no mesmo dia local, usando o último dia do mês quando necessário. Somente gerente/administrador MUST poder baixar parcela pendente pelo valor integral, escolhendo a forma realmente recebida; o Xano MUST registrar usuário e horário da baixa. Baixa repetida MUST ser idempotente, inclusive diante de pedidos concorrentes. Cancelamento de venda Reservado sem parcela recebida MUST cancelar parcelas pendentes e liberar recursos uma única vez, sem serviço externo. Cancelamento de venda paga MUST ser rejeitado no MVP.

#### Scenario: Plano de parcelas criado
- **WHEN** uma venda válida é criada com quantidade de parcelas entre 1 e 24
- **THEN** o Xano MUST gravar venda, itens, reserva e parcelas atomicamente, distribuir o total exato em centavos e retornar valores/vencimentos persistidos

#### Scenario: Primeiro vencimento é no dia da venda
- **WHEN** o Xano gera parcelas de uma venda
- **THEN** a primeira parcela MUST vencer na data local da venda em `America/Sao_Paulo` e parcelas seguintes MUST vencer mensalmente no mesmo dia local, usando o último dia do mês quando necessário

#### Scenario: Valor insuficiente para o plano
- **WHEN** o total da venda em centavos é menor que a quantidade de parcelas
- **THEN** o backend MUST rejeitar a criação antes de reservar itens ou gravar a venda

#### Scenario: Valor contém fração de centavo
- **WHEN** o valor final calculado da venda possui mais de duas casas decimais
- **THEN** o backend MUST rejeitar a criação antes de reservar itens ou gravar a venda

#### Scenario: Gerente baixa parcela integral
- **WHEN** gerente ou administrador confirma parcela pendente, informando uma forma de pagamento existente
- **THEN** o Xano MUST marcar a parcela como recebida e gravar forma, horário do servidor e usuário autenticado

#### Scenario: Vendedor tenta baixar parcela
- **WHEN** vendedor solicita confirmar recebimento
- **THEN** o backend MUST responder sem autorização e MUST NOT alterar parcela ou venda

#### Scenario: Parcela já baixada
- **WHEN** o mesmo comando de baixa é repetido para uma parcela recebida
- **THEN** o Xano MUST retornar o estado persistido sem registrar segundo recebimento

#### Scenario: Baixas concorrentes
- **WHEN** dois operadores autorizados tentam confirmar a mesma parcela ao mesmo tempo
- **THEN** o Xano MUST persistir somente a primeira baixa e devolver o estado confirmado ao segundo pedido sem substituir a auditoria

#### Scenario: Cancelamento sem parcelas recebidas
- **WHEN** gerente ou administrador cancela venda Reservado com motivo obrigatório
- **THEN** parcelas pendentes MUST ser canceladas e veículo/peças MUST ser liberados atomica e idempotentemente no Xano, sem chamadas externas

## REMOVED Requirements

### Requirement: Ciclo de vida da venda segue os estados do contrato MVP

### Requirement: Venda deve ser criada antes de solicitar link de pagamento

### Requirement: Link ASAAS deve ser solicitado para a venda criada

### Requirement: Criação do link não deve ser apresentada como confirmação de pagamento
