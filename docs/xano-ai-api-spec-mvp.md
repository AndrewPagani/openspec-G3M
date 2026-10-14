# Especificação histórica de APIs — MVP Reflex + Xano + ASAAS

> **OBSOLETA: não executar nem enviar este documento à IA do Xano.** O projeto
> não usa mais ASAAS nem processador externo. O contrato atual está na mudança
> ativa `openspec/changes/registro-manual-de-parcelas-no-xano/`; aguarde sua
> validação e aprovação antes de publicar alterações no workspace.

> **Instrução para a IA do Xano:** crie os grupos, endpoints e funções descritos
> neste documento no workspace atual. O schema necessário já existe; não apague,
> renomeie ou recrie tabelas/campos e não adicione módulos fora do MVP. Antes de
> implementar, inspecione os nomes e tipos reais das tabelas. Configure a chave
> privada ASAAS a partir da variável de ambiente/segredo já existente no Xano:
> use-a somente em chamadas server-side e nunca revele seu valor, devolva-o ao
> frontend ou grave-o em logs. Não faça chamadas de Produção durante a
> configuração.

## 1. Objetivo e limites

Criar APIs REST do MVP de uma concessionária para login, clientes, veículos,
peças/estoque, vendas, pagamento ASAAS por Link de Pagamento hospedado e
indicadores gerenciais.

O checkout ASAAS coleta os dados de pagamento diretamente. **Não implementar
formulário próprio de cartão nem tokenização explícita**, e nunca armazenar
PAN, CVV ou token de cartão. O vendedor configura o máximo de parcelas
permitido; o pagador pode escolher menos parcelas.

Fora do escopo: cadastro público de usuários, CRUD de permissões, multiunidade,
leads, oficina, emissão fiscal, estorno automático, cobrança automática de
parcelas atrasadas, contabilidade avançada e alterações no frontend.

## 2. Schema existente

Workspace: `147643`.

### Tabelas-base

- `perfil`: `id`, `Cargo`.
- `user`: `id`, `UNome`, `Email`, `perfil_id`, `Senha`, `created_at`.
- `cliente`: `id`, `CNome`, `CPF`, `Telefone`, `Email`, `asaas_customer_id`,
  `created_at`.
- `status_veiculo`: `id`, `Descricao`.
- `veiculo`: `id`, `Marca`, `Modelo`, `Cor`, `Ano`, `Placa`, `Chassi`,
  `Quilometragem`, `Preco`, `status_id`, `created_at`.
- `veiculo_area`: `id`, `Secao`.
- `peca`: `id`, `PCNome`, `PCvalor`, `qtd_disp`, `area_id`.
- `forma_pagamento`: `id`, `Metodo`.
- `status_venda`: `id`, `Descricao_venda`.
- `venda`: `id`, `cliente_id`, `vendedor_id`, `forma_pagamento_id`, `status_id`,
  `Valor_bruto`, `Desconto`, `Valor_final`, `data_venda`, `asaas_payment_link_id`,
  `asaas_payment_link_url`, `payment_link_expires_at`,
  `payment_installment_limit`, `cancel_reason`, `cancelled_at`,
  `payment_email_status`, `payment_email_requested_at`.
- `venda_item`: `id`, `venda_id`, `veiculo_id`, `peca_id`, `qtd`, `preco_unit`.

### Tabelas de pagamento ASAAS

- `pagamento`: `id`, `venda_id`, `asaas_payment_id`, `asaas_customer_id`,
  `asaas_installment_id`, `status_asaas`, `billing_type`, `valor`,
  `valor_liquido`, `taxa`, `numero_parcela`, `total_parcelas`, `vencimento`,
  `recebido_em`, `updated_at`.
- `pagamento_evento`: `id`, `asaas_event_id`, `asaas_payment_id`, `evento`,
  `recebido_em`, `processado_em`, `status_processamento`, `erro_resumido`.

No Xano, a chave primária física é `id`. Verifique o schema publicado; não
assuma nomes de coluna diferentes nem dependa de valores fixos de IDs.

### Registros de referência

Resolver IDs consultando as tabelas pelo texto, nunca por números hard-coded:

- cargos: `Vendedor`, `Gerente`, `Administrador`;
- status de venda: `Reservado`, `Paga`, `Concluída`, `Cancelada`, `Expirada`;
- status de veículo: no mínimo `Disponível`, `Reservado`, `Vendido`;
- formas de pagamento: `Pix`, `Boleto`, `Cartão de crédito`.

Se os registros não existirem, retornar erro interno configuracional claro e
registrável sem segredo. Não criar seeds automaticamente em cada requisição.
Somente itens de referência preexistentes podem ser retornados pela API.

## 3. Grupos de API

Criar estes grupos, com prefixos e nomes legíveis:

1. `autenticacao`
2. `cadastros`
3. `vendas`
4. `gerenciamento`
5. `asaas_webhooks`

Todos os endpoints, exceto `POST /auth/login` e o Webhook ASAAS, exigem
autenticação de usuário Xano. O Webhook usa somente o segredo configurado para
ele e não aceita token de sessão do app. Restringir autorização no backend; não
confiar em cargo, `vendedor_id`, status ou valores enviados pelo cliente.

## 4. Convenções HTTP

- JSON UTF-8; datas ISO-8601 em UTC nas respostas.
- Valores monetários em decimal; não usar ponto flutuante para cálculos
  financeiros.
- Paginação de coleções: `page` (padrão 1), `per_page` (padrão 20, máximo 100).
- Resposta de coleção:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 0,
    "total_pages": 0
  }
}
```

- Erro uniforme:

```json
{
  "code": "validation_error",
  "message": "Descrição segura e legível",
  "details": {}
}
```

- Usar códigos HTTP: `400` entrada inválida/transição impossível; `401`
  autenticação ausente/inválida; `403` sem permissão ou sem acesso ao registro;
  `404` inexistente; `409` unicidade, estoque, estado ou concorrência; `422`
  regra de negócio; `429` limite de requisições; `500` falha inesperada sem
  detalhes internos.
- Nunca retornar `Senha`, chave ASAAS, segredo do Webhook, tokens internos,
  stack traces ou payloads sensíveis. Sanitizar logs.

## 5. Autenticação

### `POST /auth/login` — público

Entrada:

```json
{ "email": "vendedor@exemplo.com", "senha": "segredo" }
```

Autenticar contra a tabela auth `user`; normalizar e-mail; retornar o token
nativo de autenticação Xano e o usuário sem `Senha`.

Sucesso `200`:

```json
{
  "authToken": "<token Xano>",
  "user": {
    "id": 7,
    "UNome": "Nome",
    "Email": "vendedor@exemplo.com",
    "perfil_id": 1,
    "perfil": { "id": 1, "Cargo": "Vendedor" }
  }
}
```

Credencial inválida retorna `401` com mensagem genérica, sem revelar se o
usuário existe. Não há signup nem recuperação de senha via API do app.

### `GET /auth/me`

Retornar usuário e perfil associados ao token atual, sem senha. Para token
inválido/expirado, retornar `401`.

Não criar logout server-side se a autenticação nativa não fornecer revogação;
nesse caso o frontend descarta o token.

## 6. Dados de referência (`cadastros`)

Rotas autenticadas, somente leitura:

- `GET /perfis`
- `GET /status-veiculos`
- `GET /veiculo-areas`
- `GET /formas-pagamento`
- `GET /status-vendas`

Retornar apenas `id` e o campo de descrição/nome correspondente. Não oferecer
criação, edição ou exclusão destas referências pela API do MVP.

## 7. Clientes (`cadastros`)

### `GET /clientes`

Query: `page`, `per_page`, `busca` (nome, CPF, telefone ou e-mail). Ordenar por
`CNome`; busca parcial sem expor dados de ASAAS.

### `GET /clientes/{id}`

Retornar dados locais (`id`, `CNome`, `CPF`, `Telefone`, `Email`, `created_at`).
Não retornar `asaas_customer_id` ao app.

### `POST /clientes`

Entrada:

```json
{
  "CNome": "Cliente Exemplo",
  "CPF": "000.000.000-00",
  "Telefone": "(11) 99999-9999",
  "Email": "cliente@exemplo.com"
}
```

Validar nome, CPF brasileiro, telefone e e-mail; normalizar CPF para comparação
e e-mail em minúsculas. Email é anulável apenas para compatibilidade dos dados
antigos: exigir nas novas criações. `CPF` e `Email` únicos; conflito `409`.

### `PATCH /clientes/{id}`

Aceitar os mesmos campos editáveis, validar regras de unicidade e retornar a
entidade sem `asaas_customer_id`. Não permitir editar ID, criação, usuário
ASAAS ou campos internos de venda/pagamento.

## 8. Veículos (`cadastros`)

### `GET /veiculos`

Query: `page`, `per_page`, `busca`, `marca`, `modelo`, `status_id`,
`somente_disponiveis`. A busca inclui marca, modelo, placa e chassi. Para
`somente_disponiveis=true`, usar o status cuja descrição é `Disponível`.
Retornar `Imagem_url` quando cadastrada, além da descrição do status.

### `GET /veiculos/{id}`

Retornar dados do veículo, `Imagem_url` quando cadastrada e descrição do status.

### `POST /veiculos`

Entrada: `Marca`, `Modelo`, `Cor`, `Ano`, `Placa` opcional, `Chassi`
opcional, `Quilometragem`, `Preco`, `Imagem_url` opcional e `status_id`
opcional. A URL de imagem deve usar HTTP ou HTTPS. Sem `status_id`, o backend
mantém o padrão legado `Disponível`; quando informado, deve existir na tabela
de status, e somente `Gerente` ou `Administrador` pode escolher o status
inicial. O app mostra as opções atuais do Xano e pré-seleciona `Disponível`.
Validar campos obrigatórios, ano razoável, placa/chassi únicos quando
preenchidos, preço e quilometragem não negativos.

### `PATCH /veiculos/{id}`

Atualizar atributos cadastrais. Não permitir mudar status para `Disponível` ou
`Vendido` por esta rota, nem alterar veículo associado a venda ativa. Status
possui endpoint específico.

### `POST /veiculos/{id}/status`

Entrada: `{ "status_id": 2 }`. Somente `Gerente` e `Administrador`.
Validar transição pelo estado atual; não permitir alteração manual enquanto o
veículo estiver reservado por uma venda ativa ou já vendido. `Vendedor` não
altera status.

## 9. Peças e estoque (`cadastros`)

### `GET /pecas`

Query: `page`, `per_page`, `busca`, `area_id`, `somente_disponiveis`.
Disponibilidade significa `qtd_disp > 0`.

### `GET /pecas/{id}`

Retornar dados da peça e seção/área se definida.

### `POST /pecas`

Entrada: `PCNome`, `PCvalor`, `qtd_disp` (padrão 0), `area_id` opcional.
Validar preço e quantidade não negativos; validar área se enviada.

### `PATCH /pecas/{id}`

Atualizar nome, preço e área. Não aceitar alteração de `qtd_disp` aqui;
alterações de estoque usam endpoint de ajuste.

### `POST /pecas/{id}/ajuste-estoque`

Entrada: `{ "qtd_disp": 25 }` (nova quantidade absoluta, não delta).
Somente `Gerente` ou `Administrador`. Validar inteiro não negativo e impedir
redução abaixo das quantidades reservadas em vendas ativas. Atualizar de forma
atômica. Não criar tabela/histórico de movimentação no MVP.

## 10. Vendas e autorização (`vendas`)

### Matriz

| Ação | Vendedor | Gerente | Administrador |
|---|---:|---:|---:|
| Criar venda e link | Sim | Sim | Sim |
| Ver suas vendas e pagamentos | Sim | Sim | Sim |
| Ver vendas de toda a equipe | Não | Sim | Sim |
| Desconto maior que zero | Não | Sim | Sim |
| Ajustar estoque / status veículo | Não | Sim | Sim |
| Cancelar venda ainda reservada | Não | Sim | Sim |
| Marcar pagamento manualmente | Nunca | Nunca | Nunca |

`vendedor_id` sempre vem do usuário autenticado. Para vendedor, limitar todas
as listagens, detalhes, atualizações e ações às suas vendas; retornar `404` ou
`403` de forma consistente sem revelar vendas de outros.

### `GET /vendas`

Query: `page`, `per_page`, `busca`, `cliente_id`, `vendedor_id`, `status_id`,
`forma_pagamento_id`, `data_inicio`, `data_fim`.

Vendedor ignora/rejeita filtro de outro `vendedor_id` e vê apenas seus dados.
Gerente/administrador podem filtrar equipe. Resumo deve incluir cliente,
vendedor, itens resumidos, valores, forma, status local e indicação agregada
de pagamentos.

### `GET /vendas/{id}`

Retornar venda autorizada, cliente, vendedor, itens com preço congelado,
subtotal/desconto/total, status, link/expiração e lista de pagamentos com
status ASAAS, valores, número da parcela e vencimento. Não retornar IDs
internos de segredo nem dados de cartão.

### `POST /vendas` — criar e reservar

Entrada:

```json
{
  "cliente_id": 15,
  "forma_pagamento_id": 3,
  "Desconto": 0,
  "itens": [
    { "veiculo_id": 24, "qtd": 1 },
    { "peca_id": 8, "qtd": 2 }
  ]
}
```

Regras:

1. Exigir cliente existente, forma de pagamento válida e ao menos um item.
2. Cada item possui exatamente um `veiculo_id` ou `peca_id`, não ambos.
3. Veículo deve estar disponível, quantidade deve ser `1`, e um veículo só
   pode aparecer uma vez na venda. Peça exige quantidade inteira positiva,
   preço não negativo e estoque suficiente.
4. Rejeitar duplicatas inconsistentes; consolidar ou rejeitar linhas
   duplicadas de uma mesma peça de maneira consistente.
5. O cliente nunca envia `vendedor_id`, `status_id`, `preco_unit`,
   `Valor_bruto` ou `Valor_final` como fonte confiável. Resolver vendedor pela
   sessão, preços por catálogo e status inicial `Reservado` por tabela.
6. Somar `preco_unit * qtd` usando decimal, salvar o preço unitário congelado
   em `venda_item`, calcular `Valor_bruto`, validar desconto e calcular
   `Valor_final = Valor_bruto - Desconto`.
7. Desconto padrão zero; não negativo, nem superior ao subtotal. Vendedor só
   pode usar desconto zero; gerente/administrador podem aplicar desconto não
   zero. Se houver limite máximo configurado da conta, aplicá-lo no backend.
8. Validar CPF/e-mail/telefone do cliente já cadastrado antes do fluxo ASAAS.
9. Criar venda e itens, reservar veículo (status `Reservado`) e subtrair peças
   do estoque na mesma operação atômica/transacional. Em qualquer falha,
   reverter tudo.
10. Retornar venda `Reservado`; ainda não chamar ASAAS nesta rota.

Resposta `201`: objeto da venda com itens/valores/status calculados.
Concorrência de venda/estoque retorna `409`.

### `POST /vendas/{id}/link-pagamento`

Somente venda do usuário ou acesso gerencial autorizado, status `Reservado`,
sem link já criado e sem link expirado. Entrada:

```json
{ "max_parcelas": 6 }
```

`max_parcelas` é obrigatório apenas para cartão parcelado; inteiro mínimo 1,
máximo permitido pela conta ASAAS e configuração de negócio. Para Pix e boleto,
não aceitar parcelamento.

O backend deve:

1. Buscar a venda e seu cliente/itens no Xano; nunca aceitar valor, descrição
   arbitrária, vencimento, status ou referência externa enviados pelo app.
2. Mapear forma local para ASAAS: Pix `PIX`, boleto `BOLETO`, cartão
   `CREDIT_CARD`. Não oferecer débito sem validação da conta. Para pagamento
   único usar `chargeType=DETACHED`; para cartão parcelado usar
   `chargeType=INSTALLMENT` e `maxInstallmentCount=max_parcelas`. Confirmar
   combinação no Sandbox.
3. Criar Link de Pagamento ASAAS por venda com `value=Valor_final`,
   `endDate` na data correspondente a 30 dias corridos, `externalReference`
   estável `venda-{id}`, notificações habilitadas e URL/base API Sandbox ou
   Produção de acordo com configuração segura do ambiente.
4. Chamar ASAAS somente no servidor usando a chave da variável segura já
   configurada. Nunca revelar o valor da variável em resposta, documentação ou
   logs.
5. Persistir `asaas_payment_link_id`, URL, expiração e máximo de parcelas
   retornados. Repetições não podem criar links duplicados: se houve timeout,
   reconciliar com ASAAS pela referência externa ou registrar erro de
   conciliação e impedir retry cego. Não marcar sucesso se a chamada não foi
   confirmada.
6. Responder que o link foi criado e a venda continua `Reservado`, aguardando
   pagamento. Link criado não significa cobrança criada nem pagamento.

Resposta `201`:

```json
{
  "venda_id": 123,
  "status_venda": "Reservado",
  "estado_link": "LINK_CREATED",
  "asaas_payment_link_id": "link-id",
  "valor": 1250.00,
  "parcelas_maximas": 6,
  "expira_em": "2026-10-28",
  "url": "https://www.asaas.com/c/..."
}
```

Exemplo do corpo enviado pelo servidor ao endpoint `POST /v3/paymentLinks`
para cartão parcelado (gerar valores e datas no Xano; nunca aceitar esses
valores calculados do frontend):

```json
{
  "name": "Venda Reflex 123",
  "description": "Venda 123",
  "value": 85000.00,
  "billingType": "CREDIT_CARD",
  "chargeType": "INSTALLMENT",
  "endDate": "2026-10-28",
  "maxInstallmentCount": 6,
  "notificationEnabled": true,
  "externalReference": "venda-123"
}
```

Para Pix ou boleto, usar respectivamente `billingType: "PIX"` ou
`billingType: "BOLETO"` e não enviar `maxInstallmentCount`. Para cartão em
pagamento único, usar `billingType: "CREDIT_CARD"` e `chargeType: "DETACHED"`.
Não habilitar `UNDEFINED` (múltiplos meios no mesmo link) enquanto o fluxo
exigir método escolhido previamente na venda.

Se já houver link, retornar o link existente quando ainda ativo, ou `409`
quando a venda não puder ser reaberta. Não recriar silenciosamente.

### `GET /vendas/{id}/pagamento`

Retornar status local, link, validade, total da venda, valor recebido, parcelas
pagas/pendentes e estados recentes. Não chamar ASAAS em cada carregamento de
tela; permitir consulta local imediata.

### `POST /vendas/{id}/pagamento/atualizar`

Somente usuário autorizado. Para venda/pagamento inconclusivo, consultar
ASAAS por IDs locais de pagamento e atualizar status de modo idempotente.
Aplicar limitação de frequência. Não criar cobrança/link nem repetir
transação. Se link existe mas nenhum pagamento foi associado, consultar o
estado do link quando necessário. Divergência deve ser registrada para
conciliação.

### `POST /vendas/{id}/entregar`

Vendedor pode entregar somente as próprias vendas; gerente/administrador
podem entregar vendas da equipe. Exigir venda local `Paga`, que só pode ser
definida após a primeira cobrança `RECEIVED`. Não aceitar mudança de estado de
pagamento no corpo. Registrar `Concluída` e marcar veículo como `Vendido`
atomicamente; para venda somente de peças, concluir venda sem veículo.
Idempotente: se já concluída, devolver estado atual sem repetir efeitos.

### `POST /vendas/{id}/cancelar`

Somente gerente/administrador; entrada `{ "motivo": "..." }`, motivo
obrigatório. Permitido somente antes de qualquer pagamento recebido e enquanto
a venda está `Reservado`. Desativar link ASAAS e cancelar as cobranças
pendentes associadas antes de liberar estoque/disponibilidade. Se a chamada
externa falhar ou estado for inconclusivo, manter reserva e retornar erro
reconciliável; não liberar item que ainda possa ser pago. Após cancelamento
confirmado, marcar `Cancelada`, guardar motivo/data, liberar veículo e devolver
peças uma única vez. Repetição é idempotente.

Não cancelar nem estornar pagamentos recebidos pelo app.

## 11. Webhook ASAAS (`asaas_webhooks`)

### `POST /webhooks/asaas/pagamentos` — público para ASAAS

- Sem autenticação de sessão Xano.
- Exigir cabeçalho `asaas-access-token` e comparar em tempo constante com o
  segredo do Webhook em variável segura de ambiente. Não imprimir nem incluir
  o token em erros/logs.
- Rejeitar segredo inválido com `401`.
- Receber evento ASAAS e extrair ID de evento, tipo, pagamento, valor, status,
  cliente, link e referência externa quando presentes. Validar formato,
  campos mínimos e coerência com venda local.
- Deduplicar por `asaas_event_id` com unicidade em `pagamento_evento`. Se
  duplicado já processado, responder `200` idempotente sem repetir efeitos.
- Associar venda pelo `payment.paymentLink` comparado a
  `venda.asaas_payment_link_id` e verificar `externalReference` (`venda-{id}`)
  quando disponível. Se não houver associação inequívoca, registrar falha
  resumida e não alterar venda/estoque.
- Comparar CPF/e-mail do pagador recebido pelo ASAAS com o cliente local antes
  de associar/atualizar `cliente.asaas_customer_id`. Em divergência, não
  sobrescrever o vínculo nem reatribuir a venda; salvar ocorrência resumida em
  `pagamento_evento.erro_resumido` para conciliação gerencial.
- Criar/atualizar `pagamento` idempotentemente por `asaas_payment_id`. Guardar
  estado ASAAS original, valor, valor líquido/taxa quando retornados, cliente
  ASAAS, vencimento e dados de parcela disponíveis. Atualizar apenas os campos
  confirmados pelo payload/consulta.
- Validar os eventos consultando estado oficial: só `PAYMENT_RECEIVED`/
  status `RECEIVED` marca a parcela recebida. `CONFIRMED`, análise de risco,
  criado, vencido, recusado, cancelado, estornado e chargeback não equivalem a
  recebido.
- Na primeira cobrança recebida, transicionar venda `Reservado -> Paga`.
  Recebimentos de parcelas futuras atualizam somente a parcela; não duplicam
  venda, e-mail ou ações de estoque.
- Evento de estorno/chargeback posterior deve atualizar estado da cobrança e
  sinalizar atenção, sem inventar reembolso automático nem apagar histórico.
- Persistir evento antes do processamento, marcar `processado_em` e
  `status_processamento` ao final. Em falha, guardar mensagem resumida sem
  PII/secreto e permitir reconciliação.
- Responder rapidamente com `200` após registrar evento. Não enviar e-mail
  síncrono nem executar tarefas pesadas dentro da requisição do Webhook;
  delegar processamento quando a plataforma permitir.

## 12. Expiração e tarefas agendadas

Criar tarefa interna Xano, não endpoint público, executada periodicamente e
segura para reexecução:

1. Buscar vendas `Reservado` com `payment_link_expires_at <= agora`.
2. Reconciliar estado do link e cobranças com ASAAS antes de alterar venda.
3. Se alguma cobrança da venda já estiver `RECEIVED`, não expirar nem liberar.
4. Desativar link e cancelar todas cobranças ainda pendentes no ASAAS.
5. Somente após confirmação de cancelamento/indisponibilidade do link,
   transicionar venda para `Expirada`, liberar veículo e devolver estoque de
   peças uma única vez.
6. Se ASAAS estiver indisponível ou o estado for inconclusivo, manter reserva,
   registrar falha segura e tentar novamente; nunca liberar enquanto houver
   risco de pagamento tardio.
7. Proteger concorrência entre Webhook, cancelamento e expiração com
   transições condicionais/atômicas. Pagamento recebido prevalece sobre
   expiração ainda não confirmada.

`endDate` é data do Link ASAAS; calcular fuso/localidade comercial
explicitamente. O prazo de validade da venda é 30 dias corridos. Testar links e
cobranças criados perto do limite no Sandbox.

## 13. E-mail e notificações

- Na criação do Link, habilitar notificações ASAAS conforme suporte do link.
  Isso não comprova entrega do e-mail e não garante, por si só, envio de um
  recibo personalizado após o primeiro pagamento.
- No `PAYMENT_RECEIVED`, atualizar venda/parcela e exibir confirmação no app.
- Não afirmar “e-mail enviado” sem confirmação do provedor.
- `POST /vendas/{id}/pagamento/notificar` só deve ser criado se existir uma
  integração de e-mail/notification suportada e configurada com segredo de
  servidor. Deve validar acesso, status da venda, destinatário e rate limit;
  registrar resultado em `payment_email_status` e
  `payment_email_requested_at`. Se nenhum provedor estiver configurado,
  retornar erro explícito `501 notification_provider_not_configured` ou
  deixar a rota desativada — não simular sucesso.
- Falha de notificação não reverte pagamento confirmado.

## 14. Gerenciamento (`gerenciamento`)

### `GET /gerenciamento/indicadores`

Query opcional: `data_inicio`, `data_fim`, `status_id`, `vendedor_id`,
`forma_pagamento_id`, `tipo_item`, `status_veiculo_id`.

Indicadores:

- `valor_liquido_recebido_periodo`: soma `pagamento.valor_liquido` das parcelas
  recebidas no período; quando o valor líquido não estiver disponível, expor
  ausência/null ou adotar fallback documentado por regra financeira, sem
  chamar valor bruto de líquido.
- `vendas_pagas`: contagem de vendas com ao menos uma parcela `RECEIVED`.
- `ticket_medio_vendas_pagas`: média do `Valor_final` de cada venda paga,
  contando uma vez por venda.
- `descontos`: soma dos descontos da população de vendas definida pelo filtro.
- `veiculos_disponiveis`: contagem do status `Disponível`.
- `pecas_qtd_disponivel`: soma atual de `qtd_disp`.
- `vendas_por_periodo`, `vendas_por_status_pagamento`,
  `vendas_por_forma_pagamento`, `vendas_por_vendedor` (último apenas
  gerente/administrador), `mix_itens`, `veiculos_por_status`,
  `valor_veiculos_disponiveis`, `valor_estoque_pecas`,
  `pecas_sem_estoque`.

Agregações no Xano, sem retornar registros pessoais desnecessários. Vendedor
fica restrito às próprias vendas e não recebe ranking/equipe nem totalizações
gerenciais de outros vendedores. `valor_estoque_pecas` é
`PCvalor * qtd_disp`; `pecas_sem_estoque` significa quantidade zero.

## 15. Usuários administrativos

Opcional, somente se a tela de consulta administrativa for mantida:

- `GET /usuarios`
- `GET /usuarios/{id}`

Somente Administrador. Retornar nome, e-mail, cargo e criação, sem senha ou
tokens. Não criar POST/PATCH/inativação, signup ou CRUD de permissão.

## 16. Eventos externos ASAAS e chamadas server-side

Operações necessárias:

- `POST /v3/paymentLinks` — criar link com valor fixo, `billingType`,
  `chargeType`, `endDate`, `maxInstallmentCount` quando aplicável,
  `notificationEnabled` e `externalReference`.
- `GET /v3/paymentLinks/{id}` — consultar/reconciliar link.
- `PUT /v3/paymentLinks/{id}` com `active=false` — desativar link.
- `GET /v3/payments/{id}` — reconciliar cobrança.
- `DELETE /v3/payments/{id}` — cancelar cobrança pendente, somente após
  validar comportamento no Sandbox.

Enviar credencial no cabeçalho de autenticação ASAAS somente do servidor. Usar
base URL Sandbox/Produção e chaves distintas por ambiente. A chave da API e o
segredo `asaas-access-token` do Webhook são segredos diferentes.

## 17. Critérios de aceite obrigatórios

1. Login retorna token e perfil sem senha; credenciais inválidas não revelam
   existência de usuário.
2. Rotas protegidas rejeitam token inválido; toda autorização é server-side.
3. Vendedor não acessa vendas/pagamentos de outros vendedores.
4. Cliente CPF/e-mail, placa/chassi duplicados retornam `409`.
5. Criação de venda calcula preço no servidor e reserva estoque atomicamente.
6. Venda concorrente do mesmo veículo/estoque insuficiente retorna `409` sem
   gravações parciais.
7. Link usa o total local calculado, expira em 30 dias e respeita máximo de
   parcelas; pagador pode selecionar menos parcelas.
8. Retry/timeout não cria links ou reservas duplicadas.
9. Link criado ou retorno do navegador jamais marca pagamento como recebido.
10. Webhook inválido é rejeitado; Webhook duplicado não repete efeitos;
    recebimento de parcela atualiza só aquela parcela.
11. Primeira parcela `RECEIVED` muda venda para `Paga`; parcelas subsequentes
    não contam o total integral como caixa recebido.
12. Somente venda paga pode ser entregue; entrega é idempotente.
13. Expiração/cancelamento só libera estoque após invalidar link e cobranças
    pendentes de modo confirmado; falha externa mantém a reserva.
14. Dados de cartão, credenciais e segredos não são recebidos, guardados,
    enviados ao frontend ou registrados em logs.
15. Falha de e-mail não reverte pagamento e nunca é apresentada como envio
    confirmado.
16. Indicadores aplicam filtros/permissões e somam recebimentos líquidos por
    parcela, sem dupla contagem da venda.

## 18. Dependências que não devem ser presumidas

- Confirmar a variável já existente com a chave ASAAS sem ler/exibir seu valor;
  identificar apenas o nome interno da variável e usar referência segura no
  Xano.
- Configurar separadamente a URL pública HTTPS e o segredo do Webhook ASAAS.
- Configurar no ASAAS os eventos de cobrança necessários (criação/atualização,
  recebimento, vencimento, cancelamento, estorno e chargeback) e validar o
  formato efetivo de cada evento no Sandbox antes de ativar Produção.
- Confirmar Sandbox/Produção, meios habilitados, juros/tarifas e limite de
  parcelas com a conta ASAAS.
- Confirmar se o ASAAS envia o recibo pós-pagamento requerido; se não enviar,
  selecionar/configurar provedor transacional antes de ativar a rota de e-mail.
- Sem esses segredos/configurações, criar as APIs e responder com erro
  explícito de configuração ausente; nunca usar credencial de exemplo em
  Produção.

## 19. Instruções finais para a IA do Xano

Implemente em etapas pequenas: primeiro grupos, autenticação, referências e
cadastros; em seguida vendas/estoque; depois chamadas ASAAS, Webhook e tarefa
de expiração; por fim indicadores. Após cada etapa, liste os endpoints e
valide chamadas de teste sem pagamentos reais. Não modifique o schema existente
sem apontar primeiro a discrepância e obter aprovação. Não configure nem
execute pagamentos de Produção automaticamente.

## 20. Protocolo obrigatório para erros e pendências

Se qualquer endpoint, função, integração, credencial, variável de ambiente,
WebHook, tabela/campo, permissão ou teste apresentar erro ou estiver faltando:

1. Não simular sucesso, não ignorar o erro e não exibir credenciais, tokens ou
   valores de segredos.
2. Informar o endpoint/função afetado, erro observado sem segredos, causa
   provável, impacto e configuração/alteração necessária.
3. Gerar um script/instrução de correção copiável para a IA do Xano. A
   correção deve ser específica ao erro observado, mínima e segura; preservar
   schema/dados existentes, não alterar outras APIs e incluir como validar a
   correção sem executar pagamento real.
4. Se o erro for de configuração que somente o proprietário pode resolver,
   dizer exatamente qual configuração falta e fornecer instrução segura para
   corrigi-la. Nunca pedir que o usuário cole chave ASAAS ou segredo no chat.
5. Após corrigir, repetir o teste que falhou e informar claramente o resultado.

Modelo de pedido de correção para a IA do Xano (preencher com o caso concreto):

```text
Corrija somente o erro abaixo no workspace Xano atual. Primeiro inspecione o
endpoint/função, os campos existentes e as dependências; não recrie nem apague
tabelas, não altere dados ou APIs não relacionadas e não substitua valores por
sucesso fictício.

Endpoint/função: [nome e rota]
Erro observado: [mensagem sanitizada, sem credenciais ou dados pessoais]
Comportamento esperado: [regra/contrato aplicável]
Contexto e passos para reproduzir: [requisição de teste sem dados reais]

Implemente a menor correção compatível com o schema atual. Se depender de uma
variável/segredo ausente, não imprima seu valor: identifique apenas o nome da
variável e indique onde configurá-la com segurança. Não execute operações de
pagamento em Produção.

Ao terminar, informe arquivos/endpoints alterados, causa raiz, correção e
resultado de um teste não destrutivo que reproduza o cenário.
```

Quando o assistente identificar ou receber um erro de API ou uma pendência,
deve entregar ao usuário esse pedido já preenchido para o problema específico,
em vez de apenas sugerir que “verifique no Xano”.
