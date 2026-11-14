# cadastros-e-listagens Specification

## Purpose
Registra as telas de consulta e criação de clientes, veículos e peças atualmente implementadas e a apresentação resumida usada para identificar clientes e veículos nas listagens.

## Requirements

### Requirement: Falhas auxiliares de vendas não devem impedir a listagem de clientes
Quando a consulta de clientes for bem-sucedida, a tela MUST preservar os clientes mesmo que a consulta auxiliar de vendas falhe em qualquer página ou retorne formato inválido. A tela MUST manter os indicadores derivados exclusivamente de clientes e apresentar última atividade e compras pendentes como indisponíveis, com aviso específico. MUST NOT apresentar zero pendências ou ausência de compras como se fossem dados confirmados quando vendas não puder ser consultada. Uma nova consulta bem-sucedida MUST remover o aviso e restaurar os dados derivados de vendas. Falhas na consulta principal de clientes MUST continuar sendo apresentadas como erro da listagem.

#### Scenario: Clientes disponíveis e vendas indisponíveis
- **WHEN** clientes retorna dados válidos e vendas falha
- **THEN** a lista de clientes MUST permanecer visível, com aviso restrito aos dados derivados de vendas

#### Scenario: Página subsequente de vendas falha
- **WHEN** a primeira página de vendas é carregada e uma página seguinte falha
- **THEN** a tela MUST preservar clientes e MUST NOT apresentar indicadores de vendas parciais como completos

#### Scenario: Vendas volta a responder
- **WHEN** uma nova carga de clientes e vendas é bem-sucedida
- **THEN** o aviso MUST ser removido e os indicadores de vendas MUST voltar a ser apresentados

### Requirement: Listagem de clientes deve identificar nome e CPF
A listagem de clientes MUST apresentar o nome seguido do CPF no formato `Nome - CPF`, usando os campos devolvidos pela API do Xano. A consulta MUST oferecer paginação e busca por nome, CPF, telefone ou e-mail; os detalhes não devem expor identificadores internos ASAAS.

#### Scenario: Cliente possui nome e CPF
- **WHEN** a API devolve um cliente com `CNome` e `CPF`
- **THEN** a linha do cliente MUST exibir `CNome - CPF`

#### Scenario: Busca e paginação de clientes
- **WHEN** um operador consulta clientes com busca e paginação válidas
- **THEN** a API MUST retornar somente a página correspondente de resultados que satisfaçam a busca

### Requirement: Cartão de veículo deve apresentar imagem, nome, ano e preço
A listagem de veículos MUST carregar todas as páginas de resultados disponíveis
e apresentar cartões em três colunas em telas amplas, com menos colunas em
telas menores. Cada cartão MUST apresentar imagem retangular em destaque (ou
um estado substituto quando não houver imagem), marca/modelo, ano,
quilometragem em quilômetros e preço. A consulta de veículos MUST continuar
suportando paginação e filtros de busca, marca, modelo e status.

#### Scenario: Veículo possui imagem e quilometragem
- **WHEN** a API devolve marca, modelo, ano, quilometragem, preço e URL de
  imagem do veículo
- **THEN** a listagem MUST apresentar a imagem, o nome formado por
  marca/modelo, o ano, a quilometragem e o preço formatado em moeda brasileira

#### Scenario: Veículo possui imagem
- **WHEN** a API devolve marca, modelo, ano, preço e URL de imagem do veículo
- **THEN** a listagem MUST apresentar a imagem, o nome formado por
  marca/modelo, o ano e o preço formatado em moeda brasileira

#### Scenario: Veículo não possui imagem ou quilometragem
- **WHEN** a API devolve veículo sem URL de imagem ou sem quilometragem
- **THEN** a listagem MUST manter o nome, ano e preço e MUST exibir estados
  substitutos para imagem ou quilometragem não informadas

#### Scenario: Veículo não possui imagem
- **WHEN** a API devolve veículo sem URL de imagem
- **THEN** a listagem MUST manter nome, ano e preço e MUST informar que não
  há imagem cadastrada

#### Scenario: Existem mais veículos do que cabem em uma página
- **WHEN** a resposta paginada informa mais de uma página de veículos
- **THEN** a aplicação MUST carregar todas as páginas informadas antes de
  apresentar a lista como completa

#### Scenario: Resposta de veículos vem envelopada
- **WHEN** a API retorna os registros em um envelope de resposta contendo
  `items`, `records`, `results` ou `data`
- **THEN** a aplicação MUST extrair e apresentar a lista de veículos e
  preservar os metadados de paginação, inclusive quando o envelope estiver
  aninhado

#### Scenario: Resposta de sucesso não contém lista de veículos
- **WHEN** a API responde com sucesso sem uma lista reconhecida de veículos
- **THEN** a aplicação MUST exibir erro de formato da resposta em vez de
  apresentar a resposta como uma listagem vazia

#### Scenario: Consulta de veículos não encontra registros
- **WHEN** a API retorna uma lista válida sem veículos
- **THEN** a tela MUST informar que nenhum veículo foi retornado pelo Xano e
  orientar a conferência do ambiente conectado

#### Scenario: Busca local de veículos não encontra correspondências
- **WHEN** existem veículos carregados, mas nenhum corresponde ao texto de busca
- **THEN** a tela MUST informar que nenhum veículo corresponde à busca

#### Scenario: Grade de cartões em diferentes larguras
- **WHEN** a listagem é exibida em tela ampla ou estreita
- **THEN** a grade MUST apresentar três colunas em telas amplas e reduzir para
  duas ou uma coluna conforme o viewport

### Requirement: Cadastro de veículo aceita URL opcional de imagem
O schema de veículo MUST persistir a URL de imagem no campo opcional
`imagem_url`. Os endpoints de criação, consulta individual, atualização e
listagem MUST aceitar ou devolver a chave de API `imagem_url`, compatível com
o nome persistido, para que a imagem cadastrada esteja disponível no cartão.
O formulário MUST aceitar somente endereços HTTP ou HTTPS válidos no cliente
e enviar `imagem_url` quando informado; registros sem imagem continuam
válidos.

#### Scenario: Imagem de veículo persistida e consultada
- **WHEN** um veículo é cadastrado ou atualizado com uma URL HTTP ou HTTPS
  válida
- **THEN** os endpoints de consulta individual e listagem MUST devolver
  `imagem_url` para o registro

#### Scenario: Envio de imagem válida
- **WHEN** um operador informa uma URL HTTP ou HTTPS válida e salva um veículo
- **THEN** a requisição de criação MUST incluir o campo `imagem_url`

#### Scenario: URL inválida
- **WHEN** um operador informa valor que não é uma URL HTTP ou HTTPS válida
- **THEN** o formulário MUST rejeitar o envio e exibir um erro de validação

#### Scenario: Veículo com identificador duplicado
- **WHEN** placa ou chassi já informado está associado a outro veículo
- **THEN** o backend MUST rejeitar a criação ou atualização sem alterar o
  registro existente

### Requirement: Formulários de cadastro devem validar campos locais antes do envio
Os formulários existentes de clientes, veículos e peças MUST validar a presença dos campos obrigatórios e os formatos numéricos/URL suportados antes de enviar os dados ao Xano; a validação no cliente não substitui a validação do backend.

#### Scenario: Campo obrigatório ausente
- **WHEN** um formulário é enviado sem um campo obrigatório
- **THEN** a aplicação MUST informar o campo ausente e MUST NOT enviar a requisição de criação

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
