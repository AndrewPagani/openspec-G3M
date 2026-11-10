# Requisitos da listagem de clientes

## MODIFIED Requirements

### Requirement: Listagem de clientes deve apresentar dados disponíveis e atividade derivada

A listagem de clientes MUST apresentar nome, CPF, e-mail, a última compra
registrada como última atividade e uma ação para abrir o cadastro. Telefone
MAY ser mostrado como informação secundária. A busca MUST aceitar nome, CPF,
telefone ou e-mail e a listagem MUST oferecer paginação. A interface MUST
apresentar total de clientes, novos no mês e compras pendentes somente quando
calculados dos registros da API. Novos no mês MUST usar `created_at`;
compras pendentes MUST contar somente vendas autorizadas com status
`Reservado` ou `Pendente`. A última atividade MUST ser derivada da venda mais
recente autorizada associada ao cliente. A interface MUST NOT inferir ou
inventar status de cliente, nem apresentar esses dados como globais quando o
escopo da API for restrito pelo usuário.

#### Scenario: Cliente possui dados de contato

- **WHEN** a API retorna `CNome`, `CPF`, `Email` e `Telefone`
- **THEN** a linha MUST exibir nome, CPF e e-mail, e MAY exibir telefone como
  informação secundária

#### Scenario: Cliente possui compras

- **WHEN** a API retorna vendas autorizadas associadas ao cliente
- **THEN** a linha MUST exibir a data da venda mais recente como última
  atividade

#### Scenario: Cliente não possui compra disponível

- **WHEN** não há venda autorizada associada ao cliente
- **THEN** a interface MUST exibir “Sem compras” e MUST NOT inventar uma data

#### Scenario: Métricas do período

- **WHEN** a listagem de clientes e as vendas autorizadas estão disponíveis
- **THEN** a interface MUST calcular total de clientes, clientes criados no
  mês atual e contagem de vendas nos status `Reservado` ou `Pendente`

#### Scenario: Status de cliente não existe no contrato

- **WHEN** a API não fornece status de cliente nem regra para calculá-lo
- **THEN** a interface MUST NOT exibir um badge “Ativo” ou “Inativo”

#### Scenario: Busca e paginação

- **WHEN** o operador busca por nome, CPF, telefone ou e-mail
- **THEN** a listagem MUST filtrar os registros carregados e permitir navegar
  pelas páginas resultantes
