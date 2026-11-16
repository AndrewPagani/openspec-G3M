# Publicação e validação do fluxo ASAAS

Atualização de 16/11: limpeza concluída após aprovação do estorno, confirmado
como REFUNDED/DONE. Registros da rodada e seis funções temporárias removidos;
conferência dos 11 IDs principais retornou 404. Nova leitura remota retornou
70 documentos e o pacote da aplicação retornou `No changes to push`.
Todas as tasks concluídas; evidências em cleanup-final.json e handoff.md.

Histórico de 15/11: os cenários principais foram executados em Sandbox, com
correções adicionais publicadas. Ver runtime-validation.md. O catálogo foi
completado e os parâmetros de item/data/limites corrigidos por execução real.
A limpeza aguarda aprovação de estorno de teste pelo painel ASAAS, task 4.6.
As listas abaixo são o plano original; os relatórios atuais distinguem cobertura
executada, limitações e pendências. Não repetir os testes de criação sem revisar
os registros já presentes e a necessidade de limpeza.

## Estado após publicação autorizada

Pacote publicado em **14/11/2026**, workspace `147643`, branch explícita `v1`,
após autorização do usuário. O primeiro push confirmou 15 documentos; um segundo
push atualizou as descrições de webhook/link (2 endpoints) e gravou a formatação
do servidor. Nova leitura retornou 68 documentos; dry-run final: **No changes to push**.
Não foram configurados segredos, criados clientes nem emitidas cobranças externas.

Correção da interpretação anterior: `workspace get` exibia `Allow Push: false`,
mas a tentativa autorizada de habilitar retornou HTTP 500 com a explicação
`Allow Push is not available on the Free plan. Push is always enabled for Free plan workspaces.`
Portanto, esse campo não bloqueia o push neste workspace Free. Nenhuma alteração
de plano ou configuração foi necessária para publicar.

O próprio Xano CLI 1.3.4, na descrição de `workspace edit --allow-push`, exige
confirmação explícita do usuário: "NEVER enable without explicit user confirmation".
Confirmado no código instalado `@xano/cli/dist/commands/workspace/edit/index.js`.
O usuário autorizou explicitamente habilitação e publicação. A opção de habilitação
não foi alterada, pelo comportamento Free acima; os pushes foram confirmados na CLI,
sem `--force`, `--delete`, `--truncate`, importação de registros ou segredos.

O backend remoto agora contém o contrato novo. A operação ASAAS ainda precisa de
configuração Sandbox/webhook e testes autenticados; publicação não comprova o fluxo.

## Pacote revisado

Destino explícito: workspace `147643`, branch `v1`.
Baseline de leitura: `.codex-tmp/resume-venda-asaas/`, nova consulta de definições,
sem registros/segredos. Os endpoints e schemas afetados coincidiram com a
baseline anterior `.codex-tmp/apply-venda-asaas/` antes da geração.

Publicar somente `xanoscript/asaas-sales/`, preservando GUIDs existentes.
Não publicar o export inteiro nem `xanoscript/patch-vendas-datas/`.
Não usar `--delete` ou `--truncate`.

Prévia final: [xano-dry-run.txt](xano-dry-run.txt). Previsão: 1 tabela criada,
3 tabelas atualizadas, 3 funções criadas e 8 endpoints atualizados. Sem bloqueios
de parser. A prévia não comprova permissões, transações ou chamadas HTTP reais.

O pacote adiciona discriminador LEGADO/ASAAS e campos de sincronização,
permite forma nula antes do pagamento e cria deduplicação de eventos. Preserva
identificadores e índices das tabelas existentes. O default LEGADO e a leitura
de valores antigos nulos precisam ser conferidos com registros de homologação.

## Configuração sem expor credenciais

`ASAAS_ENV` é texto de configuração, não uma chave emitida pelo ASAAS. No mesmo
local onde foi cadastrada `ASAAS`, adicionar variável de nome exato `ASAAS_ENV`
e valor de texto `sandbox`, sem aspas. O usuário informou possuir apenas ASAAS;
aguarda-se confirmação das configurações abaixo, sem solicitar seus valores no chat.

Configurar no Xano `ASAAS_ENV=sandbox`, chave `ASAAS` e segredo separado
`ASAAS_WEBHOOK_TOKEN` com pelo menos 32 caracteres. Usar o mesmo segredo na
configuração autenticada do webhook ASAAS. Não colocar valores no frontend,
repositório, captura ou log. Não reutilizar a chave de API como token de webhook.

Configurar entrega de eventos de pagamento para o endpoint
`POST /webhooks/asaas/pagamentos` da branch escolhida. Confirmar a URL no Xano;
não deduzi-la de outro grupo/API. Habilitar os eventos de pagamento necessários
à confirmação e atualização (incluindo exclusão/estorno), sem envio de e-mail.
O cliente define `notificationDisabled=true`; a função também desativa e
verifica todas as notificações retornadas antes de gerar cobranças.

OpenAPI remoto consultado após publicação confirmou o grupo asaas_webhooks,
ID 435065, branch v1, base https://x8ki-letl-twmt.n7.xano.io/api:asaas_webhooks.
Logo a URL de entrega é
https://x8ki-letl-twmt.n7.xano.io/api:asaas_webhooks/webhooks/asaas/pagamentos.
Sete sondas públicas de autenticação passaram (HTTP 401), registradas em
public-auth-checks.json. Elas não testam token correto, recebimento ou autorização
por vendedor. Somente a datasource live foi encontrada na consulta remota.

A cobrança preparada usa `billingType=UNDEFINED`, referência estável `venda-ID`
e vencimento em 30 dias, calculado em America/Sao_Paulo. Os 30 dias são uma
decisão da implementação, não uma preferência expressamente dada pelo usuário.
Não há criação de parcelas manuais nem parcelamento ASAAS neste escopo.

## Comandos após liberação

Reconsultar o remoto e comparar qualquer alteração antes de regenerar.
O gerador prepara arquivos; não realiza publicação ou cobrança:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_asaas_sales.py --source .codex-tmp/resume-venda-asaas --output xanoscript/asaas-sales
xano.cmd workspace push --workspace 147643 --branch v1 --directory xanoscript/asaas-sales --dry-run
```

Após liberação do push e revisão da prévia atual, usar o mesmo comando sem
`--dry-run`. Publicar o frontend somente junto ao contrato compatível e depois
da validação Sandbox. Conservar a baseline para rollback de definições; não
apagar tabelas/recebimentos nem reclassificar vendas ASAAS como LEGADO ao reverter.

## Testes autenticados pendentes (não comprovados pelos testes Python)

1. Conferir catálogos reais de cargos/status/formas; testar vendedor próprio,
   outro vendedor e gerente/admin. Verificar baixa manual recusada para ASAAS.
2. Cadastrar cliente, simular timeout e repetir os mesmos dados. Verificar um
   vínculo local/ASAAS e notificações realmente desativadas, inclusive reutilização.
3. Criar venda mista e disputar a última unidade/veículo em chamadas concorrentes.
   Confirmar reserva única, preço autoritativo e ausência de parcelas manuais.
4. Simular falha antes/depois do POST de cobrança; executar geração concorrente.
   Deve existir uma cobrança; SENDING ambíguo só admite recuperação por consulta.
   LOOKUP/SENDING bloqueiam cancelamento até recuperação; não apagar esses estados
   manualmente para liberar tentativa sem conferir o ASAAS.
5. Reabrir venda e recuperar a mesma URL. Confirmar escolha de meio pelo comprador
   no Sandbox, sem abrir uma URL fixture como se fosse cobrança real.
6. Testar webhook sem token, token incorreto e token correto no cabeçalho.
   Validar formato efetivo de `$env.$http_headers` e envelope de `api.request`.
   Corpo JSON não pode substituir a autenticação do cabeçalho.
7. Pagar no Sandbox, reenviar evento e entregar evento antigo. Conferir uma
   entrada por ID externo, data autoritativa, venda paga e nenhum estoque duplicado.
   Testar rollback/locks entre funções e transações, não só a sintaxe.
8. Concorrer cancelamento, geração de link e confirmação de pagamento. Liberar
   estoque somente com exclusão ASAAS confirmada; recibos bloqueiam cancelamento.
9. Conferir histórico legado, indicadores por data efetiva de recebimento,
   filtros/perfil e registros nulos anteriores. Estorno/chargeback atualiza o
   estado financeiro; não existe neste escopo automação para estornar a venda
   ou devolver estoque, nem deve haver liberação automática nesses eventos.

Somente depois da configuração e desses cenários marcar 4.4/4.5 e arquivar a change.
