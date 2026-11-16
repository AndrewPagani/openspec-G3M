# Contexto verificado do projeto

## Limpeza de arquivos locais em 16/11/2026

A pedido do usuário, temporários, capturas locais, caches e ferramentas pontuais
da homologação encerrada foram selecionados para exclusão. As referências desses
arquivos nos relatórios arquivados são históricas; não indicam ferramentas ainda
disponíveis. Testes unitários, geradores, pacotes da aplicação e evidências
documentais em docs foram preservados.

Antes da remoção de .codex-tmp, foram comparados os 14 arquivos necessários a
scripts/prepare_asaas_sales.py: todos coincidem com os arquivos preservados em
docs/contexto/xano-2026-11-13/. Esse snapshot serve como baseline histórica para
reproduzir esta migração, não como definição atual para publicar sem comparação.
A confirmação se limita a esses 14 arquivos; não reclassifica todo o snapshot
de 13/11 como consulta da branch v1. Exemplo de reprodução local:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_asaas_sales.py --source docs/contexto/xano-2026-11-13 --output <diretorio-de-revisao>
```

Ambiente .venv, execução .web, estado .states e configuração .env foram preservados.

## Change arquivada em 16/11/2026

`revisar-venda-e-integracao-asaas` foi encerrada a pedido do usuário. Os quatro
requisitos foram sincronizados na [spec vigente de venda com fatura ASAAS](openspec/specs/venda-com-fatura-asaas/spec.md).
As 16 tarefas e evidências foram preservadas no
[arquivo da change](openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/closure.md).
Para novas vendas ASAAS, essa spec define o fluxo vigente em lugar das exigências
manuais anteriores; histórico LEGADO permanece preservado.

## Limpeza da homologação concluída em 16/11/2026

Após aprovação do usuário, o estorno Sandbox de 40,00 foi confirmado como
REFUNDED/DONE. Cliente externo encerrado e transação local removeu a rodada
TESTE ASAAS e vínculos. Os 11 registros principais retornaram 404 na conferência
independente. As seis funções temporárias asaas/test_* foram removidas pelos
próprios GUIDs; funções da aplicação foram preservadas. Marcadores de eventos
processados foram mantidos para deduplicação.
Evidência: [cleanup-final.json](openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/cleanup-final.json).

## Homologação real da change em 15/11/2026

Executado no ASAAS Sandbox o ciclo de cliente, venda mista, fatura persistida,
pagamento simulado e webhook automático. Verificados escopo entre vendedores,
repetição de eventos, disputa de estoque, cancelamento idempotente, legado e
indicadores por recebimento. Falhas de execução encontradas foram corrigidas
e publicadas em 147643/v1: opcionais de item, filtro de vencimento, datas nulas
nos indicadores e limites da tabela venda_parcela. Evidências e limites:
[runtime-validation.md](openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/runtime-validation.md).

**Limpeza concluída em 16/11:** aprovação confirmada, estorno concluído e dados
de teste removidos, conforme evidência acima. A change foi arquivada em 16/11/2026
com a spec sincronizada; Sandbox não equivale a go-live em produção.

## Change de venda e ASAAS — implementação local em 14/11/2026

A change `revisar-venda-e-integracao-asaas` foi aplicada localmente e verificada
com 99 testes, lint, build e navegador com fixtures. O pacote isolado
`xanoscript/asaas-sales/` foi preparado a partir de nova consulta de `147643/v1`
e passou no dry-run (1 tabela nova, 3 alteradas, 3 funções novas, 8 endpoints
alterados). **Publicado em 147643/v1 após autorização explícita**, com confirmação
de 15 documentos e ajuste posterior das descrições de 2 endpoints. A leitura
posterior retornou 68 documentos e o dry-run final `No changes to push`.
`Allow Push: false` não impedia publicação neste plano Free: a própria API
explicou que nele o push já fica habilitado. Sandbox/webhook já conferidos por
HTTP 200 e sondas autenticadas; o ciclo completo de venda/pagamento segue pendente.
Catálogos reais foram lidos: Reservado, Paga e Expirada estavam ausentes e foram
adicionados sem mudar IDs/status existentes. Conciliação agora reconhece Boleto
Bancário. Evidências em
[setup-validation.md](openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/setup-validation.md).
Estado, decisões e pendências autenticadas estão no
[handoff da change](openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/handoff.md)
e no [roteiro de publicação](openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/deployment.md).
Essa implementação não sincroniza automaticamente os demais arquivos de
`workspace_current` nem substitui as evidências históricas abaixo.

Consulta realizada em **13/11/2026**, no fuso `America/Sao_Paulo`.

## Atualização de GET /vendas em 14/11/2026

Uma nova leitura explícita do workspace `147643`, branch `v1`, confirmou e
sincronizou [a definição local de GET /vendas](../xanoscript/workspace_current/api/vendas/vendas_GET.xs).
As datas agora seguem quatro caminhos de consulta; o filtro de vendedor
é aplicado no banco antes da paginação. As consultas de referência de clientes
e vendedores usam `campo in lista` e são ignoradas quando a lista está vazia.
Status e formas de pagamento são consultados como catálogos completos.
A resposta inclui `items`, `pagination` e informações resumidas de cobrança
ASAAS; isso não adiciona chamadas de pagamento ao app.

A prévia CLI restrita a esse único endpoint retornou **`No changes to push`**.
Isso comprova a sincronização da definição, não o sucesso de execução com uma
sessão autenticada. O app já lê os campos retornados e mantém os filtros vazios
omitidos. Nenhuma publicação remota foi realizada nesta sincronização.

O [snapshot e manifesto de 14/11](contexto/xano-2026-11-14/README.md) registram
a versão e seu SHA-256. O restante deste documento e o snapshot de 13/11
registram a análise anterior; suas divergências de GET /vendas foram
superadas pela definição consultada agora. Os demais arquivos de
`workspace_current` não foram sincronizados nesta tarefa e continuam
exigindo comparação remota antes de publicação. O patch experimental em
`xanoscript/patch-vendas-datas/` tornou-se obsoleto e não deve ser publicado.

Este documento registra evidências, divergências e limites da análise. Não substitui decisões de negócio nem resolve conflitos entre specs e implementação. Revalidar os arquivos afetados antes de cada alteração; o snapshot remoto representa uma consulta pontual.

## Fontes e grau de confirmação

| Fonte | O que permite afirmar | Limite |
| --- | --- | --- |
| `app/`, `rxconfig.py`, `requirements.txt` | Comportamento implementado no app local | Não comprova comportamento da instalação em execução |
| `docs/openspec/specs/` | Requisitos registrados | Há requisitos divergentes do código e do remoto |
| `docs/openspec/changes/archive/` | Histórico e estado de encerramento das mudanças | `abandoned` não equivale a especificação concluída/aprovada |
| `xanoscript/workspace_current/` | Definições locais do backend | A leitura remota confirmou desatualização |
| [Snapshot consultado pelo CLI](contexto/xano-2026-11-13/README.md) | Schema e definições de API retornados pelo workspace `147643` | Branch selecionada pelo perfil, nome não confirmado; sem teste de execução autenticada |
| Testes Python executados nesta análise | 83 testes locais passaram | Não validam autorização, concorrência ou transações no Xano |

Não foram consultados registros de clientes, usuários, vendas ou catálogos. Não foram solicitadas variáveis de ambiente nem executadas funções seed, baixas, cobranças, migrações ou publicação. Valores de IDs de perfis/status não devem ser deduzidos do schema.

## Arquitetura e navegação

Aplicação de concessionária em Python + Reflex; Xano fornece autenticação, persistência e APIs. `httpx` realiza as chamadas. Não há banco próprio da aplicação Python.

- [Registro das páginas](../app/app.py): gerenciamento, login, clientes, veículos, peças, vendas, usuários, auditoria e configurações. Registro de rota não comprova funcionalidade completa.
- [Shell](../app/components/app_shell.py): navegação e visibilidade conforme sessão/perfil.
- [AuthState](../app/state/auth_state.py): login/logout; token, nome e perfil usam `rx.LocalStorage`. `authenticated` verifica presença do token; validade efetiva é responsabilidade do Xano.
- [ResourceState](../app/state/resource_state.py): listagens, busca/ordenação/paginação local de clientes e diálogos de edição; carrega todas as páginas informadas de clientes, veículos e peças. Na tela de clientes, também consulta vendas para última atividade e pendências.

  Falhas dessa consulta auxiliar agora preservam os clientes e os indicadores derivados de clientes. Última atividade e compras pendentes ficam indisponíveis com aviso próprio; não são apresentadas como ausência confirmada de compras. A consulta principal de clientes mantém seu tratamento separado de erro.
- [FormState](../app/state/form_state.py): criação de cliente, veículo e peça, com validação local. Detalhes complementares do veículo são enviados em uma segunda requisição, depois da criação do veículo; isso não constitui uma transação única entre as duas chamadas.
- [Detalhe de cliente](../app/state/client_detail_state.py) e [detalhe de veículo](../app/state/vehicle_detail_state.py): leitura por ID de rota e normalização da resposta.
- [VendasState](../app/state/vendas_state.py): lista/filtros, seleção de itens, criação de venda com 1–24 parcelas, leitura do cronograma e baixa manual.
- [DashboardState](../app/state/dashboard_state.py): consulta assíncrona de indicadores, validação de datas/filtros, adaptação de KPIs/séries e exportação CSV.

O [cliente Xano](../app/services/xano_client.py) usa por padrão o host `https://x8ki-letl-twmt.n7.xano.io`, grupos `autenticacao`, `cadastros`, `Q9GErvvS` (vendas) e `gerenciamento`, com overrides por ambiente. Estes são defaults do código, não a confirmação dos valores efetivos de um processo iniciado. `rxconfig.py` usa `http://127.0.0.1:8001` como API Reflex padrão; essa é a conexão da interface com o servidor Reflex, diferente do host Xano.

## Banco consultado pelo CLI

A consulta remota retornou **64 documentos XanoScript, 16 tabelas e 39 endpoints**. O snapshot preserva 60 documentos de tabelas e APIs, incluindo definições dos grupos. As definições de workspace, função seed e objetos de AI não foram copiadas. A exportação local contém 61 documentos, 15 tabelas e 38 endpoints.

| Domínio | Tabelas remotas | Relações principais |
| --- | --- | --- |
| Acesso | `user`, `perfil` | `user.perfil_id → perfil.id`; somente `user` declara `auth = true` |
| Clientes | `cliente` | Referenciado por vendas e vínculo ASAAS |
| Veículos | `veiculo`, `status_veiculo`, `veiculo_detalhe` | Status no veículo; detalhe ligado por `veiculo_id` único |
| Peças | `peca`, `veiculo_area` | `peca.area_id → veiculo_area.id`; saldo em `qtd_disp` |
| Vendas | `venda`, `venda_item`, `status_venda`, `forma_pagamento` | Venda referencia cliente, vendedor, forma e status; item referencia venda e veículo/peça |
| Recebimento local | `venda_parcela` | Venda, forma recebida e usuário da baixa; unicidade de venda/número da parcela |
| Integração externa | `pagamento`, `asaas_cliente`, `asaas_cobranca` | Pagamento/cobrança por venda; vínculo de cliente com ASAAS |

Consulte o [inventário completo](contexto/xano-2026-11-13/README.md) para campos, tipos, relações e as definições originais com índices/defaults. As chaves físicas usam `id` minúsculo; preservar capitalização de campos como `CNome`, `UNome`, `PCvalor`, `Valor_final` e `Desconto`.

Diferenças concretas de schema:

- `asaas_cliente` e `asaas_cobranca` existem no remoto consultado e não na exportação local.
- `pagamento_evento` está na exportação local, mas não foi retornada pela consulta remota.
- `cliente.asaas_customer_id` e os campos de link ASAAS de `venda` presentes localmente não constam nas respectivas tabelas remotas consultadas; o remoto usa tabelas de vínculo separadas.
- `peca.imagem_url` existe no remoto e está ausente na tabela local.
- Há diferenças adicionais de índices, ordem de campos e representação de filtros/defaults. O inventário distingue diferença textual de interpretação semântica.

## Contratos de operação observados

### Autenticação e autorização

`POST /auth/login` recebe `email` e `senha`; a definição retorna `authToken` e usuário/perfil e configura expiração de 86.400 segundos. Chamadas autenticadas do app usam Bearer. O app trata HTTP 401 e 403, mas a leitura remota não executou login nem chamadas com sessão.

As specs preveem Vendedor, Gerente e Administrador. O código local implementa `is_admin = False` e considera gerente apenas o cargo `Gerente`. A baixa de parcelas também exige exatamente `Gerente` no código remoto. A consulta administrativa de usuários, por outro lado, exige `Administrador` no Xano. Não presumir uma matriz uniforme de autorização.

### Listagem de vendas

O app compartilha [sales_query_params](../app/services/sales_query.py) entre a tela de vendas e a consulta auxiliar da tela de clientes. Envia `page`/`per_page` como strings, `busca` vazia ou preenchida e somente os filtros opcionais preenchidos, em query parameters de GET; não há corpo JSON. O endpoint declara paginação inteira opcional, busca textual e filtros JSON opcionais. Após relato de HTTP 500 `Input is not scalar` nas duas telas, foi removido o envio de `{}` nos filtros vazios: esse texto pode ser decodificado como objeto e é incompatível com o tratamento escalar do endpoint. A atribuição dessa falha ao tratamento dos filtros é uma hipótese baseada no request e no código remoto consultado, ainda sem trace de execução autenticada que identifique a instrução exata.

**Divergência relevante de filtragem/paginação:** no [GET remoto](contexto/xano-2026-11-13/api/vendas/vendas_GET.xs), o `where` de `db.query venda` não utiliza vendedor. Após paginar, o código filtra `$visible_items` pelo usuário autenticado quando o perfil é Vendedor, ou pelo vendedor selecionado na consulta gerencial. Portanto, existe restrição dos itens retornados no código, mas ela acontece depois da paginação. A exportação local filtra no banco, antes de paginar. O remoto pode retornar páginas com poucos ou nenhum item e metadados calculados sobre o conjunto anterior ao filtro; o efeito concreto exige teste autenticado. Não foi demonstrado retorno de registros de outros vendedores. A busca remota também não contém as condições de nome/e-mail do vendedor existentes localmente.

### Criação, parcelas e estoque

O [POST remoto de vendas](contexto/xano-2026-11-13/api/vendas/vendas_POST.xs) recebe cliente, forma, `numero_parcelas`, `Desconto` e itens. Deriva vendedor de `$auth.id`, verifica contatos do cliente, consulta preços do catálogo, exige exatamente veículo ou peça por item, veículo com quantidade 1, saldo de peças suficiente e bloqueia desconto de vendedor. Grava venda/itens/reserva/parcelas em `db.transaction`.

**Risco identificado no código local e remoto:** o laço de criação de parcelas está dentro do laço de itens processados. Com vários itens, ele tenta gerar novamente os mesmos números de parcela da venda. Como o schema declara índice único de venda/número, a expectativa é conflito e rollback, não parcelas válidas por item. Esta é uma inferência da estrutura do código e do índice; não foi criada venda de teste para reproduzir.

A leitura/validação de estoque ocorre antes das gravações da transação, usando saldo previamente lido. A presença de `db.transaction` e o comentário “contra concorrência” não comprovam proteção contra reservas concorrentes. Isso continua pendente de teste e análise do mecanismo de escrita.

### Baixa, entrega e cancelamento

A [baixa remota](contexto/xano-2026-11-13/api/vendas/vendas/id/parcelas/parcela_id/receber_POST.xs) verifica gerente, venda, vínculo da parcela e forma recebida; grava status `RECEBIDA`, usuário e horário. Possui tratamento para parcela já recebida e releitura dentro da transação. A transição para `Paga` depende especificamente de `numero_parcela == 1`; receber outra parcela primeiro não tem a mesma transição. A regra “primeira parcela recebida” precisa ser distinguida da “parcela número 1”.

Entrega exige venda paga e atualiza veículo para vendido. O cancelamento verifica perfil gerencial, motivo e ausência de parcela recebida, cancela parcelas pendentes e libera recursos em transação. A aplicação observada concentra a interface em criação e baixa; existência dessas rotas no backend não significa que todas tenham ações disponíveis na tela.

### ASAAS e indicadores

O app bloqueia rotas de link, atualização/notificação de pagamento e webhooks. Isso não equivale à desativação do backend.

**Divergência remota confirmada:** o [link de pagamento remoto](contexto/xano-2026-11-13/api/vendas/vendas/id/link_pagamento_POST.xs) contém chamadas para clientes/cobranças do ASAAS Sandbox e usa `$env.ASAAS`; exige gerente/administrador e venda com status `Pendente`. A exportação local dessa rota a desativa. Não foram lidos valores de segredo nem executada a rota; não se confirmou que ela consegue gerar uma cobrança.

O remoto também possui `GET /auditoria_parcelas` no grupo gerenciamento, ausente localmente. Isso não é uma tabela genérica de auditoria. O dashboard remoto usa `venda_parcela`, inclui consultas de diagnóstico e difere do arquivo local. A data/filtro usados em cada KPI devem ser conferidos na expressão específica, sem assumir uma única semântica para todos os indicadores. A suíte Python testa transformação/apresentação, não a exatidão da agregação remota.

## Documentação divergente e referências antigas

1. `README.md` e `xano-api-readiness-check.md` apontam uma mudança ativa de parcelas cujo caminho não existe. A mudança está no [arquivo histórico](openspec/changes/archive/2026-11-09-abandoned-registro-manual-de-parcelas-no-xano/.openspec.yaml), marcada `closure: abandoned`, com testes pendentes. Isso não implica remoção da implementação.
2. As specs de vendas/dashboard/integridade ainda contêm regras ASAAS; o app usa baixa manual. A visão geral também mistura exclusão de ASAAS do escopo com funcionalidades de cobrança. Não escolher silenciosamente uma dessas versões como decisão vigente.
3. A indicação de 11 tabelas em documentos antigos descreve a base original, não as 16 tabelas retornadas agora.
4. `workspace_full`, `backup-before-real-mvp`, `workspace`, bundles e migrações não são intercambiáveis com `workspace_current` nem com o snapshot remoto desta consulta.
5. Rotas de auditoria/configurações estão registradas no app, mas o cliente HTTP local rejeita `/auditoria` e `/configuracoes-dashboard` por ausência de grupo reconhecido. O endpoint remoto `auditoria_parcelas` tem outro caminho. O formulário genérico não implementa cadastro de usuários.
6. Caminhos de seed e mudanças citados no README devem ser conferidos antes de uso; não inferir existência de arquivos a partir de links antigos.

## Verificações realizadas e limites

- `python -m unittest discover -s tests`, usando `.venv/Scripts/python.exe`: **83 testes passaram** nesta consulta.
- O shim `xano.ps1` falhou pela política de execução; `xano.cmd` no sandbox falhou em `uv_os_get_passwd`. A execução permitida fora do sandbox funcionou.
- `xano workspace get -w 147643` confirmou `Andrew's Workspace` e informou `Allow Push: false`.
- `workspace pull -w 147643 -b live` retornou 404. Sem forçar a branch, usando a configurada no perfil, o pull retornou 64 documentos. O nome da branch não foi exibido: não chamar esse resultado de produção/live sem confirmação.
- Snapshot obtido sem opções de registros, variáveis de ambiente ou drafts. O [manifesto](contexto/xano-2026-11-13/manifest.json) registra GUID e SHA-256 das definições preservadas.
- Nenhum push ou alteração remota foi realizado. Nenhum teste autenticado de backend foi executado. Não houve build visual nesta análise documental.

## Procedimento para próximas tarefas

Consultar primeiro este mapa, a spec do recurso, a implementação afetada e o inventário. Para comportamento remoto, conferir branch e definição atual antes de concluir que o snapshot permanece válido. Distinguir requisito, implementação local, definição remota e resultado de execução. Citar as fontes ao apontar uma divergência; explicitar quando a conclusão é inferência ou falta verificação.

Não inventar nomes de tabelas, campos, valores de catálogo, IDs, respostas de API ou funcionalidades a partir do layout. Teste local aprovado não comprova autorização/atomicidade no servidor. Corrigir conflitos de negócio em mudança própria, respeitando o escopo autorizado pelo usuário. Este levantamento não alterou os comportamentos divergentes listados.
