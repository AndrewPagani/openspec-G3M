# Homologação executada — 15/11/2026

**Limpeza concluída em 16/11/2026:** após aprovação do usuário, o ASAAS confirmou
REFUNDED/DONE para os 40,00. Cliente externo encerrado; transação local removeu
a rodada e registros associados. Os 11 IDs principais retornaram 404 na conferência
independente. As seis funções temporárias foram removidas pelos próprios GUIDs.
Funções da aplicação e marcadores de eventos processados foram preservados.
Evidências: cleanup-status.json e cleanup-final.json. Dados da rodada não devem
mais afetar listagens/totais. A seção de pendência abaixo é histórico superado.

Workspace 147643, branch explícita v1, ASAAS_ENV=sandbox, chave validada nesse
ambiente. O usuário pediu continuidade e resolução autônoma das pendências,
reservando sua ação para configurações de chaves. Sem datasource de testes no
plano Free, foram usados somente registros novos, identificados como TESTE ASAAS.
Não foram reutilizados cliente, usuário ou estoque existentes.

## Resultados comprovados

- Cadastro pelo POST /clientes sincronizou o cliente ASAAS. Repetição dos mesmos
  dados devolveu o mesmo ID. Notificações consultadas: nenhuma habilitada.
- Venda mista: veículo 25,00 + duas peças 7,50 = 40,00, preço calculado no backend.
  Reserva única e recuperação/reabertura da mesma fatura persistida.
- Vendedor próprio gerou link; outro vendedor e perfil Cliente receberam 403.
  Gerente recuperou o mesmo link. Nenhum perfil Administrador foi criado para
  fingir cobertura de um cargo ausente no catálogo real.
- A confirmação pela API exclusiva do Sandbox resultou em RECEIVED. O webhook
  real, sem baixa manual ou chamada direta de conciliação pelo runner, marcou
  a venda Paga e registrou valor recebido 40,00.
- Reenvios do mesmo evento com corpo antigo PENDING foram aceitos sem regredir
  a venda paga, duplicar o pagamento ou repetir reserva de estoque.
- Cancelamento de venda recebida foi recusado.
- Duas reservas simultâneas disputaram 3 unidades cada quando havia 4: somente
  uma foi criada. A rejeitada não deixou outra venda nem alteração parcial.
- Cobrança pendente foi excluída no ASAAS antes da liberação do estoque. Repetir
  cancelamento não devolveu estoque novamente.
- Indicadores retornaram 200 sem datas, só início, só fim, intervalo e período
  vazio. Escopo do vendedor não foi ampliado ao informar outro vendedor.
- Histórico LEGADO foi lido. Vendedor não pôde baixar manualmente; gerente pôde,
  com repetição idempotente. A venda ASAAS recusou baixa manual.
- Indicadores do vendedor de teste contabilizaram recebimentos ASAAS e LEGADO
  uma vez, ticket médio 23,75 e líquido igual ao líquido externo + 7,50 legado.
  Período vazio isolado retornou zero recebimentos.

Evidência: integration-run.json preserva falhas anteriores e o resultado da rodada
principal. O último erro desse runner foi o indicador, corrigido e revalidado em
integration-followup.json, cuja rodada final passou. Não alterar retroativamente
as falhas do primeiro relatório para aparentar uma execução sem problemas.

## Falhas reais corrigidas e publicadas

1. POST /vendas: `int? peca_id` permitia null, mas ainda exigia a presença do campo.
   Campos de item passaram a `int? peca_id?` e `int? veiculo_id?`, permitindo o
   payload que omite a referência não utilizada. Regra de exatamente um permanece.
2. Link: filtro inexistente epoch_ms_add_days causava 500. Substituído por
   transform_timestamp "+30 days" em America/Sao_Paulo. Cálculo movido para antes
   da marca SENDING, impedindo uma falha de preparação de parecer envio externo.
   Apenas a fixture 101 foi recuperada excepcionalmente: erro ocorrido antes do
   POST foi comprovado e consulta ASAAS por referência não encontrou cobrança.
   Tentativas ambíguas reais não tiveram sua proteção enfraquecida.
3. Indicadores: removidas comparações de timestamp com null em OR. Quatro caminhos
   de consulta e filtros opcionais no banco; itens consultados somente pelos IDs
   das vendas já autorizadas/filtradas e somente quando a lista não está vazia.
4. venda_parcela: filtros remotos malformados `min:"1,max":24` causavam erro ao
   gravar. Corrigidos para `min:1|max:24` em numero_parcela e total_parcelas,
   preservando GUID, campos, índices e registros. Schema remoto foi reconsultado
   e coincidiu com a baseline antes desse patch.

O Free impôs 10 requisições/20 segundos. Um teste de replay retornou 429; o
runner foi espaçado, e replays seguintes passaram. Não atribuir esse 429 à regra
de negócio nem afirmar que a aplicação não tem limite de requisições.

## Fatura hospedada

A captura .impeccable/review/asaas-sandbox-invoice.png foi aberta e inspecionada:
mostrou boleto, cartão de crédito e débito para a cobrança 106. Nenhum formulário
de pagamento foi submetido no navegador; essa cobrança foi cancelada depois.
Pix não apareceu. Não foi criada/alterada chave Pix na conta.

O detector textual do browser foi inconclusivo para cartão e Pix, enquanto a
captura posterior mostrou os botões de cartão. integration-hosted-ui.json mantém
esse resultado, sem converter artificialmente o booleano em aprovação automática.
A escolha entre múltiplos meios foi comprovada visualmente; não se comprovou Pix
nessa fatura nem compra com cartão no browser.

## Histórico da limpeza antes da aprovação (concluída em 16/11)

Rodada: asaas-check-29875dab-6c75-4e1d-b5a8-bccb142f24c5.
Cliente local 102; usuários sintéticos 52–55; veículo 27; peça 11.
Vendas 101 (ASAAS paga 40,00), 102 (ASAAS cancelada 22,50), 105 (LEGADO 7,50)
e 106 (fatura de UI cancelada 7,50). Esses IDs foram retornados pelos serviços;
não são catálogos ou IDs a usar em funcionalidades normais.

O estorno Sandbox de 40,00 foi solicitado para encerrar a fixture. Consulta
confirmou AWAITING_CRITICAL_ACTION_AUTHORIZATION; repetir a solicitação retornou
"O estorno dessa cobrança já está em andamento". Não se trata de conclusão.
O usuário foi solicitado a aprovar a ação no painel Sandbox; conforme a documentação
oficial, o token de teste é 000000 quando solicitado. Não foram desativadas
proteções de segurança, importadas chaves ou enviadas mensagens a terceiros.

cleanup-status.json registra o estado confirmado por GET. Os registros locais e
vínculos foram preservados até conclusão do estorno; a função de limpeza
recusa removê-los antes do encerramento externo. Os registros de teste podem
aparecer nas listagens e totais enquanto essa limpeza estiver pendente.

Comando usado após a aprovação (função temporária removida ao final):

```powershell
xano.cmd function run asaas/test_cleanup --workspace 147643 --branch v1 --data run_id=asaas-check-29875dab-6c75-4e1d-b5a8-bccb142f24c5 --data stage=status
```

Somente com REFUNDED, executar stage=external para encerrar o cliente externo,
aguardar processamento dos eventos e executar stage=local. Conferir ausência dos
registros da rodada, preservar marcadores de eventos processados e remover as
funções temporárias de teste pelos próprios GUIDs, sem apagar funções da aplicação.
Não repetir o runner principal após a limpeza.

## Limites da homologação

Sem teste de Administrador (cargo ausente), timeout de transporte induzido,
criação simultânea de duas cobranças ou cancelamento concorrente com pagamento.
Disputa de estoque, duplicação/reordenação sequencial e demais casos acima foram
executados. Não extrapolar esses resultados para todas as interleavings possíveis.
Sem produção, cartão real, e-mail ao comprador ou movimentação de dinheiro real.

99 testes Python e lint do gerador passaram após os ajustes. Frontend não foi
alterado nesta etapa; o build/checagem responsiva anterior permanece como evidência
da interface, sem alegar que equivale a esta homologação HTTP.
