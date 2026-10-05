## Purpose

Consolida os requisitos de cadastro, consulta e apresentação de clientes, veículos e peças do MVP no capability existente de cadastros e listagens.

## MODIFIED Requirements

### Requirement: Listagem de clientes deve identificar nome e CPF
A listagem de clientes MUST apresentar o nome seguido do CPF no formato `Nome - CPF`, usando os campos devolvidos pela API do Xano. A consulta MUST oferecer paginação e busca por nome, CPF, telefone ou e-mail; os detalhes não devem expor identificadores internos ASAAS.

#### Scenario: Cliente possui nome e CPF
- **WHEN** a API devolve um cliente com `CNome` e `CPF`
- **THEN** a linha do cliente MUST exibir `CNome - CPF`

#### Scenario: Busca e paginação de clientes
- **WHEN** um operador consulta clientes com busca e paginação válidas
- **THEN** a API MUST retornar somente a página correspondente de resultados que satisfaçam a busca

### Requirement: Cartão de veículo deve apresentar imagem, nome, ano e preço
A listagem de veículos MUST apresentar marca/modelo, ano e preço; quando houver URL de imagem reconhecida na resposta do Xano, MUST apresentar a imagem, e quando não houver MUST exibir um estado substituto sem imagem. A consulta de veículos MUST suportar paginação e filtros de busca, marca, modelo e status.

#### Scenario: Veículo possui imagem
- **WHEN** a API devolve marca, modelo, ano, preço e URL de imagem do veículo
- **THEN** a listagem MUST apresentar a imagem, o nome formado por marca/modelo, o ano e o preço formatado em moeda brasileira

#### Scenario: Veículo não possui imagem
- **WHEN** a API devolve veículo sem URL de imagem
- **THEN** a listagem MUST manter nome, ano e preço e MUST informar que não há imagem cadastrada

### Requirement: Cadastro de veículo aceita URL opcional de imagem
O formulário de criação de veículo MUST oferecer campo opcional para URL da imagem, aceitar somente endereços HTTP ou HTTPS válidos no cliente e enviar o valor como `Imagem_url` quando informado. O cadastro MUST aceitar os campos definidos pelo contrato de API vigente e o backend MUST validar os formatos, valores não negativos e unicidade de placa/chassi quando informados.

#### Scenario: Envio de imagem válida
- **WHEN** um operador informa uma URL HTTP ou HTTPS válida e salva um veículo
- **THEN** a requisição de criação MUST incluir o campo `Imagem_url`

#### Scenario: URL inválida
- **WHEN** um operador informa valor que não é uma URL HTTP ou HTTPS válida
- **THEN** o formulário MUST rejeitar o envio e exibir um erro de validação

#### Scenario: Veículo com identificador duplicado
- **WHEN** placa ou chassi já informado está associado a outro veículo
- **THEN** o backend MUST rejeitar a criação ou atualização sem alterar o registro existente

### Requirement: Formulários de cadastro devem validar campos locais antes do envio
Os formulários existentes de clientes, veículos e peças MUST validar a presença dos campos obrigatórios e os formatos numéricos/URL suportados antes de enviar os dados ao Xano; a validação no cliente não substitui a validação do backend.

#### Scenario: Campo obrigatório ausente
- **WHEN** um formulário é enviado sem um campo obrigatório
- **THEN** a aplicação MUST informar o campo ausente e MUST NOT enviar a requisição de criação

## ADDED Requirements

### Requirement: Cadastro e consulta de clientes, veículos e peças
O backend MUST oferecer as rotas de consulta paginada e criação/atualização descritas no contrato de API do MVP. CPF de cliente e e-mail quando informado MUST ser únicos. Clientes MUST poder ser consultados por nome, CPF, telefone ou e-mail; veículos por texto, marca, modelo e status; peças por texto, área e disponibilidade. A resposta MUST limitar campos ao necessário para a operação e MUST NOT expor dados privados de integração.

#### Scenario: CPF ou e-mail duplicado
- **WHEN** novo cliente ou atualização usa CPF ou e-mail já pertencente a outro cliente
- **THEN** o backend MUST rejeitar a operação com conflito de unicidade

#### Scenario: Consulta paginada de veículos e peças
- **WHEN** operador solicita página e filtros válidos de veículo ou peça
- **THEN** o backend MUST aplicar os filtros antes da paginação e devolver os metadados de paginação

### Requirement: Estoque de peças usa o saldo disponível definido no schema do MVP
O MVP MUST usar `peca.qtd_disp` como saldo disponível e MUST NOT pressupor contadores persistidos separados de quantidade total, reservada ou vendida, nem endpoint de movimentação de estoque. Ajuste de saldo MUST ser permitido somente a gerente/administrador e ser atômico. Reserva de venda MUST reduzir o saldo disponível na mesma operação atômica da criação da venda; cancelamento ou expiração pendente MUST restaurá-lo uma única vez.

#### Scenario: Ajuste autorizado de estoque
- **WHEN** gerente ou administrador envia ajuste de estoque com quantidade não negativa
- **THEN** o backend MUST atualizar `qtd_disp` atomicamente

#### Scenario: Usuário sem permissão ajusta estoque
- **WHEN** vendedor tenta ajustar o estoque
- **THEN** o backend MUST rejeitar a operação sem alterar `qtd_disp`

#### Scenario: Reserva concorrente excede o saldo
- **WHEN** vendas concorrentes tentam reservar unidades além do saldo disponível
- **THEN** no máximo as reservas cobertas pelo saldo MUST ser confirmadas e `qtd_disp` MUST NOT ficar negativo

#### Scenario: Venda pendente é cancelada ou expira
- **WHEN** cancelamento ou expiração libera uma reserva já aplicada
- **THEN** o backend MUST restaurar o saldo exatamente uma vez

### Requirement: Disponibilidade de veículos segue transições permitidas
O backend MUST aceitar somente as transições aprovadas de status de veículo. O fluxo comercial MUST reservar veículo disponível ao criar a venda e MUST marcá-lo como vendido somente ao concluir a entrega de venda paga. Veículos reservados, indisponíveis, em manutenção, revisão ou vendidos MUST NOT ser oferecidos para nova venda.

#### Scenario: Veículo é reservado
- **WHEN** venda válida reserva veículo disponível
- **THEN** o backend MUST marcar o veículo como reservado e impedir uma segunda reserva concorrente

#### Scenario: Veículo reservado é entregue após pagamento
- **WHEN** operador autorizado conclui a entrega de venda paga
- **THEN** o backend MUST concluir a venda e alterar o veículo reservado para vendido

#### Scenario: Transição ou venda não permitida
- **WHEN** é solicitada transição não aprovada ou inclusão de veículo não disponível em venda
- **THEN** o backend MUST rejeitar a operação sem alterar status ou disponibilidade
