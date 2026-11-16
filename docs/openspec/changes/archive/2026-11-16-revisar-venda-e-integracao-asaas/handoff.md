# Estado da aplicação da change

## Fechamento em 16/11/2026

Change encerrada e destinada ao arquivo
docs/openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/,
com sincronização dos quatro requisitos autorizada pelo usuário. Spec principal
venda-com-fatura-asaas criada e validada; 16 tarefas concluídas. Ver closure.md.
As referências abaixo a não arquivamento descrevem checkpoints anteriores.

## Atualização em 16/11/2026 — limpeza concluída

Usuário confirmou aprovação do estorno no Sandbox. GET remoto confirmou venda
101 com estado externo REFUNDED e estorno DONE de 40,00. Etapa external confirmou
encerramento do cliente ASAAS e das cobranças da rodada. Só então foi executada
a transação local de limpeza, com validação de nome, proprietário e referências.

Removidos cliente 102, usuários 52–55, veículo 27, peça 11, vendas 101/102/105/106
e respectivos itens, parcelas, pagamentos e vínculos ASAAS. Conferência independente
dos 11 registros principais por Metadata API retornou HTTP 404 para todos.
As 6 funções temporárias asaas/test_* foram removidas após conferir seus GUIDs;
nenhuma função da aplicação foi selecionada. Marcadores de eventos processados
foram preservados para reconhecer reenvios tardios.

Evidências: cleanup-status.json (GET externo REFUNDED/DONE), cleanup-final.json
(ausência dos registros e funções) e runtime-validation.md. Script de verificação:
scripts/finalize_asaas_test_cleanup.mjs. A primeira remoção de funções atingiu o
limite Free (429); a retomada confirmou as já ausentes e removeu somente restantes.

Todas as tasks estão concluídas, com limites de cobertura registrados.
A nova leitura remota pós-limpeza retornou 70 documentos em
.codex-tmp/pos-limpeza-asaas-2026-11-16/ e o dry-run do pacote da aplicação retornou
No changes to push. OpenSpec strict e git diff --check passaram.

Change ainda não arquivada; Sandbox não é go-live em produção nem validação exaustiva
de todas as interleavings. Não executar runners de criação ou republicar
xanoscript/asaas-tests por rotina: são evidência histórica e exigem preparação
supervisionada de outra rodada. Não há dados dessa rodada a limpar novamente.
Estado abaixo é histórico superado quando houver conflito.

## Atualização em 15/11/2026 — homologação executada

Usuário solicitou continuidade. Foi executado ciclo real de cliente/venda mista,
fatura, confirmação simulada no ASAAS e webhook automático, com registros novos
identificados como TESTE ASAAS em live (Free recusou datasource separada).
Relatório principal: 22 verificações passaram; seu erro final de indicadores
foi corrigido e revalidado no relatório complementar, com 15 verificações passando.
Não esconder falhas intermediárias registradas nos JSONs.

Corrigidos e publicados: campos opcionais de item no POST /vendas; filtro real
de data de vencimento e preparação antes de SENDING; consultas de indicadores
sem comparação de data com null; limites min/max malformados de venda_parcela.
Preço/estoque, escopo entre vendedores, recebimento automático, evento duplicado
e antigo, cancelamento idempotente, disputa de estoque, legado e totais financeiros
foram verificados. Ver runtime-validation.md para cobertura e limitações.

**Pendência atual (4.6): limpeza.** Estorno de teste de R$ 40,00 da venda 101
está AWAITING_CRITICAL_ACTION_AUTHORIZATION no ASAAS Sandbox. Usuário foi solicitado
a aprovar no painel; token de homologação 000000 se solicitado, conforme docs ASAAS.
Não reenviar POST de estorno, não desativar controles da conta e não remover
vínculos locais antes de REFUNDED. cleanup-status.json contém GET confirmado.
Cliente 102, usuários 52–55, veículo 27, peça 11 e vendas 101/102/105/106 continuam
identificados como teste. Podem aparecer nas listagens/totais até a limpeza.
Nenhum registro preexistente de cliente/estoque/usuário foi reutilizado.

Há 6 funções temporárias em xanoscript/asaas-tests, sem API pública e com guardas
de propriedade/Sandbox. Manter até limpeza, depois remover somente seus GUIDs.
Comandos de continuação e cautelas de limpeza em runtime-validation.md e README.
Não repetir o runner principal: contém criação de registros; apenas retomar ações
específicas desta rodada. Nenhuma chave/senha/token de sessão salvo nos relatórios.

Fatura 106 foi aberta em browser e cancelada: a captura mostra boleto, crédito e
débito; Pix não apareceu e não foi criada chave Pix. O detector textual precoce
foi inconclusivo, não convertido artificialmente em teste automático aprovado.
Histórico anterior abaixo fica superado por esta atualização quando houver conflito.

Atualizado em **14/11/2026**, America/Sao_Paulo. O usuário solicitou a retomada.
Implementação e verificações locais concluídas. Publicação autorizada pelo usuário
e concluída em 147643/v1. Configuração Sandbox/webhook validada; ciclo completo
de venda e pagamento continua pendente.
Não arquivar a change como integração operacional.

## Resultado local

- Tela permite cliente, veículo e/ou peças, com resumo responsivo e total.
  Removidos desconto, forma e número manual de parcelas da criação.
- Criação envia somente cliente/itens. Backend preparado calcula preço e reserva
  sob transação/lock. Veículo e peça com o mesmo ID não colidem na seleção.
- Após reserva, guarda ID e solicita a fatura. Falha do link preserva a venda;
  retry não repete criação. Resultado de criação ambíguo bloqueia repetição cega.
- Link ASAAS HTTPS validado, salvo em asaas_cobranca.invoice_url, pode ser aberto,
  copiado e recuperado ao reabrir. Estados antigos de outra venda são limpos.
- Comprador escolhe meio no ASAAS; não há e-mail. Novos clientes são sincronizados
  pelo backend preparado, com recuperação e verificação de notificações desativadas.
- Backend restringe vendedor à própria venda; gerente/admin podem operar todas.
  Frontend reconhece Administrador e mantém histórico de parcelas legadas.
  Baixa manual é recusada para novas vendas ASAAS no app e no pacote backend.
- Funções preparadas consultam estado atual do ASAAS, deduplicam eventos e
  persistem recebimento por ID externo. Indicadores usam recebimentos efetivos.
- Cancelamento verifica exclusão externa antes de devolver estoque. Locks e
  estados LOOKUP/SENDING protegem disputas com geração/recuperação de cobrança.

Esses itens descrevem código local. A sintaxe aceita na prévia não comprova
execução HTTP, autorização, locks ou transações no Xano.

## Fontes e pacote

Gerador: scripts/prepare_asaas_sales.py. Saída: xanoscript/asaas-sales/.
Nova leitura do workspace 147643, branch v1, em .codex-tmp/resume-venda-asaas/;
as definições afetadas coincidiram com a baseline anterior
.codex-tmp/apply-venda-asaas/. Preservar essas fontes de leitura; não publicar
exports completos nem xanoscript/patch-vendas-datas/.

Ver deployment.md para mudanças, configuração, comandos e cenários pendentes.
A prévia final está salva em xano-dry-run.txt: 1 tabela criada, 3 tabelas alteradas,
3 funções novas e 8 endpoints atualizados, sem bloqueio de parser.
Push efetivo confirmou 15 documentos, seguido de 2 endpoints com descrições
atualizadas. GUIDs atribuídos às 4 definições novas estão salvos no pacote.
O gerador preserva esses GUIDs ao regenerar na mesma saída. Nova leitura final
em .codex-tmp/pos-publicacao-venda-asaas-final/ retornou 68 documentos;
dry-run final: `No changes to push`. Nenhum cadastro/cobrança ASAAS ou alteração
de segredo foi feito. Ver publication.md para evidências e correção sobre Free.

## Evidência de verificação

- `python -m unittest discover -s tests`: **99 testes passaram**. Os novos testes
  cobrem venda mista, validação, URL maliciosa, retry sem nova venda, criação
  ambígua, recuperação por GET, limpeza de estado, baixa ASAAS bloqueada e legado.
- Ruff nos arquivos afetados, isolado E4/E7/E9/F/I: passou. Isto é o passe de
  sintaxe/imports/erros, não aprovação de todas as regras da configuração global.
- `python -m reflex export --frontend-only --no-zip`: produção compilou após
  a última correção visual. Permanecem avisos de configuração/depreciação do
  Reflex (sitemap/Radix) e recomendação Windows/OneDrive, fora deste escopo.
- OpenSpec strict: passou; executar na raiz docs.
- Edge headless, fixtures locais sem chamadas Xano/ASAAS: desktop 1440x1000 e
  celular 390x844; venda mista, falha do link, recuperação, reabertura. Uma criação
  de venda e duas tentativas de link; sem erro JavaScript nem overflow horizontal.
  Scripts em .codex-tmp/sales_ui_server.py e verify_sales_ui.py.
- Capturas válidas: .impeccable/review/desktop.png, mobile.png,
  desktop-error.png e desktop-payment.png. Relatório: interaction-report.json.
  Os dados são fixtures explicitamente identificadas; invoice URL não é real.
- Detector Impeccable executado uma vez, findings em detector.json: tipografia
  Inter e fundo grid preexistentes. Identidade global preservada neste refinamento.
- Revisor Impeccable independente retornou `fix`: contraste do erro e cliente
  desabilitado ilegível. Corrigidos e recapturados; verdict posterior `ship`
  limitado aos dois ajustes, ambos resolvidos e sem regressão visível no lote.
  Sem novo DESIGN.md/PRODUCT.md: ausentes antes do trabalho, sem reparo de setup.

## Próximos passos após publicação

### Estado atual após confirmação de ASAAS_ENV

O usuário salvou ASAAS_ENV=sandbox. Evidências atuais: setup-validation.md e
setup-check.json. HTTP 200 no Sandbox, função asaas/request validada na consulta,
webhook correto ativo, fila liberada, sequencial e 15 eventos. Sonda com token
correto atingiu conciliação e recusou ID fictício sem criar evento/pagamento.
Configuração concluída (4.4); não é teste de baixa.

Catálogos reais revelaram ausência de Reservado/Paga/Expirada; adicionados
idempotentemente preservando status existentes. Reconhecimento de Boleto Bancário
corrigido e publicado na conciliação. Nenhum perfil/usuário criado.
Dry-runs finais dos dois pacotes: No changes to push.

O plano Free recusou datasource isolada (403 exigindo upgrade). Não houve upgrade
ou criação de registros sintéticos em live. 4.5 continua pendente; não substituir
testes financeiros/transacionais por sondas de configuração ou testes Python.

### Histórico anterior à confirmação (superado pelo estado acima)

Atualização: usuário confirmou criação do webhook e da variável
ASAAS_WEBHOOK_TOKEN. Diagnóstico remoto por função asaas/check_setup confirmou
chave ASAAS presente e token com tamanho válido. Sonda HTTP com o token enviado
somente entre Xano e seu próprio endpoint retornou 400 para cobrança fictícia
não vinculada, em vez do 401 das sondas sem token. Nenhum valor secreto foi
exibido/gravado, nem cliente/cobrança/evento criado nessa sondagem.

**Ainda pendente:** o diagnóstico retornou sandbox=false. Não é possível afirmar
se ASAAS_ENV está ausente ou com outro valor; foi solicitado ao usuário ajustar
ASAAS_ENV para o texto sandbox. Não houve chamada ao ASAAS enquanto essa guarda
estava falsa, portanto a chave ainda não foi validada contra o Sandbox e a lista
de webhooks ainda não foi conferida. A tentativa de prévia de workspace com
env={ASAAS_ENV:"sandbox"} retornou No changes to push; isso não alterou a variável.
Não tratar essa sintaxe como procedimento válido de configuração.

Função de diagnóstico publicada isoladamente em xanoscript/asaas-operations/,
1 função nova, sem endpoint público. Execução e limites no README desse pacote;
resultado sanitizado salvo em setup-check.json nesta change. Solicitação de
configuração está pendente; uma resposta anterior sobre criação do token não
comprova que ASAAS_ENV também foi configurada.

O usuário orientou resolver autonomamente as pendências, solicitando sua ação
quando envolver chaves de API/segredos no ambiente Xano. Foi solicitado configurar
ASAAS_ENV=sandbox, ASAAS (chave Sandbox) e ASAAS_WEBHOOK_TOKEN (segredo próprio
de 32–255 caracteres sem espaços). Ele informou que só possui ASAAS e perguntou
como configurar ASAAS_ENV; foi explicado que é uma variável de texto com valor
sandbox. Ainda não houve confirmação de que as três estão prontas. Não deduzir
que a chave existente é Sandbox nem usar produção para substituir essa confirmação.

Nova evidência HTTP real (sem sessão/chaves): scripts/verify_xano_asaas_public.mjs
consulta grupos/OpenAPI via autenticação existente do CLI, sem ler variáveis ou
registros. Relatório public-auth-checks.json: sete cenários retornaram 401,
incluindo cadastro com campos tipados, criação de venda, link, pagamento e webhook
sem cabeçalho/com cabeçalho errado/token no corpo. Chamadas de cadastro com campos
ausentes retornam 400 antes da autenticação; isso é validação de entrada, não
falha de autorização. Os corpos de teste de cadastro são inválidos no domínio e
não criam cliente. Não há confirmação do caminho autenticado bem-sucedido.

URL de webhook confirmada pelo OpenAPI de asaas_webhooks (grupo 435065):
https://x8ki-letl-twmt.n7.xano.io/api:asaas_webhooks/webhooks/asaas/pagamentos
Grupos vendas 435069/Q9GErvvS e cadastros 435067/cadastros também confirmados.
Consulta de datasources retornou somente live; não tratar uma datasource test
como existente nem executar mutações de teste em registros reais silenciosamente.

O campo `Allow Push: false` foi inicialmente interpretado como bloqueio.
Após autorização explícita, a tentativa de habilitação foi recusada porque o
plano Free já permite push sempre. Publicação seguiu sem alterar essa configuração.
O contrato novo agora está no remoto. Não solicitar novamente autorização já dada
para esta publicação nem tentar habilitar a opção indisponível no plano Free.

Configurar Sandbox e segredo próprio de webhook no Xano/ASAAS sem expor valores.
Executar matriz autenticada em deployment.md, incluindo autorização, notificações,
formato real dos headers/envelope HTTP, concorrência, rollback, duplicação e eventos
fora de ordem. Testes Python/browser usam fixtures e não substituem essa matriz.
Não marcar tasks 4.4/4.5 nem integração em produção antes de comprovar os cenários.
