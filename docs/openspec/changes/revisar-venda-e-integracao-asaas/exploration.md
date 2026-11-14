# Exploração: criação de venda com cobrança ASAAS

Data: 14/11/2026. Estado: exploração; não representa implementação ou publicação.

## Objetivo solicitado

Manter a seleção visual de veículos e/ou peças na tela de nova venda,
remover os campos sem utilidade para o fluxo desejado e integrar cadastro
de cliente e geração de cobrança hospedada no ASAAS.

Decisões expressas pelo usuário nesta exploração:

- Recebimentos confirmados automaticamente pelo ASAAS, substituindo a baixa manual.
- O cliente escolhe a forma de pagamento ao abrir o link.
- Não haverá envio de e-mail neste fluxo, pelo app, pelo Xano ou por notificações automáticas do ASAAS.
- O link será persistido em `asaas_cobranca.invoice_url`, na tabela existente de cobranças ASAAS, associado à venda por `venda_id` e à cobrança por `asaas_payment_id`.

## Evidências consultadas

Código local: `app/pages/sales.py`, `app/state/vendas_state.py`,
`app/services/xano_client.py`, `app/state/form_state.py`, `app/state/auth_state.py`.
Specs relacionadas: vendas/pagamento, usuários/perfis e integração Xano.

Nova leitura pelo CLI: workspace `147643`, branch `v1`, sem registros,
variáveis de ambiente ou drafts. As 11 definições relevantes e seus hashes
estão em `docs/contexto/xano-2026-11-14-exploracao-asaas/`.
Leitura de definição não comprova sucesso de chamadas autenticadas ou ASAAS.

| Ponto | Comportamento observado |
| --- | --- |
| Dois campos abaixo da forma | `Desconto` e `numero_parcelas` (1–24) |
| POST /vendas | Exige forma_pagamento_id e numero_parcelas; calcula preço no Xano, cria reserva e parcelas manuais |
| Estado inicial da venda | Busca e grava status `Reservado` |
| POST /vendas/{id}/link-pagamento | Exige status `Pendente`, gerente/administrador; cria cobrança única Sandbox com billingType UNDEFINED e devolve invoice_url |
| POST /clientes | Já tenta criar cliente no ASAAS Sandbox após gravar cliente local; persiste vínculo em asaas_cliente |
| Falha no cadastro ASAAS | Em resposta HTTP inválida, tenta apagar cliente local; não há tratamento explícito de timeout ambíguo ou de falha ao persistir vínculo após criação externa |
| App | Não chama geração de link e bloqueia a rota no cliente HTTP |
| Webhook ASAAS | Desativado por precondition(false) |
| Forma de pagamento | Catálogo local possui apenas Metodo; venda.forma_pagamento_id é obrigatória no schema consultado |
| Histórico de cobrança | asaas_cobranca vincula venda, payment_id, invoice_url, status e vencimento; venda_id é único |

Há incompatibilidade objetiva entre o status criado e o exigido para o link.
O parâmetro de parcelas manuais não é enviado ao ASAAS. O endpoint de link
retorna uma **fatura de cobrança individual (invoiceUrl)**, não um recurso
genérico `/paymentLinks`. Essa fatura atende ao cliente previamente selecionado.

## Direção proposta para a tela

### Skill de interface definida pelo usuário

Usar a skill **Impeccable** (`impeccable`) no planejamento, implementação e
revisão da interface desta change. Ler o `SKILL.md` instalado e seguir o
fluxo correspondente à tarefa: definição da experiência, layout, hierarquia,
textos, responsividade, acessibilidade e estados de carregamento, erro e sucesso.

Preservar a seleção visual de veículos/peças e as decisões de negócio registradas
nesta exploração. O uso da skill não autoriza alterar contratos Xano/ASAAS,
permissões, schema ou regras de pagamento por critérios visuais. A integração
de backend deve continuar baseada nas specs e nas definições remotas verificadas.

Levar essa orientação aos artefatos de design e às tarefas de implementação
quando a exploração for transformada em proposta. A instalação da skill, por si
só, não representa execução de uma revisão ou aprovação do design.

1. Selecionar cliente existente, com acesso ao cadastro de novo cliente.
2. Selecionar veículo disponível e/ou peça com estoque, mantendo os seletores
   visuais atuais e o controle de quantidade das peças.
3. Revisar itens, quantidades e total. Cada item continua identificando veículo
   ou peça, nunca os dois no mesmo item. A mesma venda pode misturar os tipos.
4. Exibir a indicação “O cliente escolhe como pagar no link do ASAAS”.
5. Remover do formulário inicial os inputs de desconto e cronograma manual;
   ausência de desconto resulta em zero, com cálculo autoritativo no Xano.
   Um eventual recurso futuro de desconto gerencial exige regra e apresentação
   próprias; não inferir que o pedido atual autoriza excluir dados históricos.
6. Ação principal proposta: “Criar venda e gerar link”.
7. Após criar: apresentar número da venda, total, estado da cobrança e ações
   de abrir/copiar link. Se a segunda etapa falhar, permitir repetir somente
   a geração do link, preservando a venda e evitando nova reserva.

O link deve ser salvo em `asaas_cobranca.invoice_url` antes de a interface
confirmar a geração concluída. Ao reabrir a venda, recuperar o link persistido
em vez de criar outra cobrança. O operador poderá abrir ou copiar esse link;
não haverá ação de enviar/reenviar e-mail nem disparo automático de e-mail.

O formulário não deve pedir dados de cartão. A criação de link não confirma
pagamento. O retorno do navegador também não deve marcar a venda como paga.

## Fluxo de cadastro de cliente

O Xano deve coordenar o cadastro local e no ASAAS e persistir o vínculo em
`asaas_cliente`. Confirmar o cadastro integrado somente após obter o customer ID
e salvar o vínculo. Credenciais permanecem no backend.

O e-mail cadastral pode continuar sendo coletado e enviado ao ASAAS como dado
do cliente; isso não autoriza envio de mensagens. Manter as notificações
automáticas desabilitadas no cadastro e verificar essa configuração também
ao reutilizar clientes legados. Não adicionar etapas de envio de e-mail à
criação do cliente, à geração da cobrança ou à confirmação de pagamento.

A API já contém essa integração, portanto a mudança deve completar e validar
o comportamento existente, não criar uma segunda integração no app.
Usar referência estável do cliente local em externalReference e recuperar o
vínculo antes de repetir a criação. A referência não deve ser tratada como
garantia automática de unicidade: a documentação ASAAS permite duplicatas.

Timeout após criação externa e falha de persistência do vínculo devem permitir
recuperação/reconciliação. Uma transação Xano não desfaz uma criação remota no
ASAAS. Não apagar registros ou repetir POST cegamente quando o resultado externo
for desconhecido. Clientes legados sem vínculo também precisam de recuperação
antes da geração de cobrança.

## Mudanças de contrato necessárias

- POST /vendas não deve exigir do operador forma efetiva de pagamento antes
  da escolha no checkout. Definir em proposta a representação de “a definir”:
  FK anulável até a confirmação ou catálogo explicitamente aprovado. Não usar
  IDs fictícios, escolher a primeira forma ou gravar Pix/cartão arbitrariamente.
- Remover a criação obrigatória de cronograma manual nas novas vendas ASAAS;
  preservar dados e leitura de vendas manuais/legadas. Atualizar os consumidores
  que hoje esperam parcelas locais e o dashboard que calcula baixas manuais.
- Alinhar o status inicial da venda com a geração de cobrança. Recomendação:
  manter `Reservado` como estado da venda com recursos reservados e tratar
  `PENDING` como estado externo da cobrança; confirmar isso na proposta.
- Geração da fatura com billingType UNDEFINED e valor final da venda. Reutilizar
  cobrança existente e referência estável para recuperação; índice local único
  não elimina sozinho duplicação externa em concorrência ou timeout.
- Persistir e recuperar o link no campo existente `asaas_cobranca.invoice_url`;
  não criar outra tabela de links nem usar a tabela de parcelas manuais para isso.
  Se a persistência falhar após a criação externa, recuperar a cobrança antes
  de repetir a operação, sem confirmar geração concluída ao operador.
- Não implementar envio/reenvio de e-mail pelo app ou Xano. Verificar em
  Sandbox que as notificações ASAAS permanecem desabilitadas, inclusive para
  clientes legados reutilizados; não presumir isso apenas pelo payload de criação.
- Separar ambiente/configuração de Sandbox e Produção explicitamente. O código
  consultado aponta para Sandbox; não houve solicitação de migração para Produção.
- Habilitar webhook autenticado, com deduplicação e tratamento de eventos fora
  de ordem. Acompanhar o estado externo e preencher a forma efetiva quando
  disponível; não presumir ID de forma local a partir do texto da UI.
- Revisar cancelamento para cancelar/reconciliar cobrança pendente no ASAAS
  antes de liberar recursos, evitando link pagável com estoque já liberado.
- Revisar permissões: hoje todos podem criar venda, mas só gerente/administrador
  podem gerar link; o app local também desativa is_admin. A experiência desejada
  precisa de matriz coerente antes de expor a ação a vendedores.

O schema de eventos, a idempotência e a representação do meio de pagamento
devem ser especificados a partir das tabelas realmente presentes. Não presumir
que `pagamento_evento` local exista no remoto.

## Parcelamento: limite desta exploração

A escolha do meio de pagamento no link não define sozinha um parcelamento.
O endpoint atual cria cobrança única e não envia installmentCount, totalValue
ou installmentValue. Retirar o cronograma manual não significa prometer
parcelamento no checkout. Se parcelamento for necessário, esclarecer as
modalidades e o contrato do ASAAS antes de definir campo e regras.

## Consistência da venda

O código consultado cria parcelas manuais dentro do laço de itens. Há risco
de repetir o mesmo número de parcela em uma venda com mais de um item,
conflitando com o índice único da tabela. A troca de fluxo deve cobrir a criação
de venda mista, além de disponibilidade/estoque concorrentes. A leitura de
estoque anterior à transação não comprova exclusão de concorrência.

## Próximo artefato OpenSpec

Transformar esta exploração em proposal/design/specs/tasks com:

- Cadastro integrado recuperável e tratamento de clientes legados.
- Tela de venda e contrato revisado de criação + fatura.
- Matriz de permissões, status e meios de pagamento.
- Webhook/consulta de estado, cancelamento e métricas ASAAS.
- Compatibilidade com vendas/parcelas manuais existentes.
- Persistência/recuperação do link em asaas_cobranca e ausência de envio de e-mail.
- Validação em Sandbox: cadastro, repetição após timeout, venda mista,
  geração repetida, falha de cobrança após reserva, evento duplicado/fora de
  ordem, pagamento, cancelamento e isolamento por vendedor.

Nesta exploração não foram alterados app, schema ou endpoints; não foram
executados cadastros, cobranças, baixas, publicação ou leitura de segredos.

## Referências oficiais consultadas

- https://docs.asaas.com/docs/criando-um-cliente
- https://docs.asaas.com/reference/criar-novo-cliente
- https://docs.asaas.com/reference/criar-nova-cobranca
- https://docs.asaas.com/docs/cobrancas-via-cartao-de-credito
- https://docs.asaas.com/docs/criar-uma-cobranca-parcelada
