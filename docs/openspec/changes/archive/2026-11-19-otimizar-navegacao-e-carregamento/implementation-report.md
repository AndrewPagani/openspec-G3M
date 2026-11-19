# Implementação e validação — 19/11/2026

Change `otimizar-navegacao-e-carregamento`. Aplicada localmente, sem publicação ou revalidação autenticada do Xano/ASAAS. O backend simulado recusa endpoints desconhecidos e chamadas síncronas. Nenhuma cobrança foi criada nestes testes.

## Resultado

- Clientes, veículos, peças e usuários têm namespaces Reflex independentes, criados a partir de um mixin. Buscas, registros, paginação, erros e diálogos não atravessam os recursos.
- Leituras usam snapshots separados, eventos em background e bloqueios curtos para captura/publicação. Cada publicação confere geração de rota/worker, token, conta, ambiente/grupos e parâmetros. Outra rota cancela consumidores antigos; resultados, erros e finalizadores obsoletos não são publicados. Detalhes associam inclusive erros ao ID consultado.
- Todo HTTP dos estados de interface foi migrado para `async_request`. O lifespan cria/fecha um pool HTTPX; headers pertencem a cada chamada e leituras têm limite de três por processo. Escritas preservam sua ordem, sem retry automático.
- Clientes, veículos e peças publicam páginas progressivamente, mantendo a carga integral. Falhas posteriores preservam os registros válidos e indicam lista incompleta, com nova consulta manual. Busca parcial e totais ainda não confirmados têm rótulos próprios.
- Clientes aparece antes da consulta auxiliar de vendas. A atividade e as compras pendentes só são confirmadas após ler todas as páginas de vendas. Falha nessa consulta não substitui a listagem por erro de outra tela.
- Apenas `/formas-pagamento`, `/status-veiculos` e `/veiculo-areas` usam cache: TTL fixo de 300 s, até 128 entradas, chave por URL/grupo e credencial normalizada em hash, cópias independentes, bypass explícito e deduplicação em andamento. Cancelar um consumidor preserva os demais. Invalidação e atualização forçada impedem repopulação por respostas antigas. Estoque/preço/vendas/pagamentos e clientes não usam esse cache.
- Logout/login invalidam leituras e limpam dados operacionais/rascunhos da conta anterior. Preferências locais por conta são retidas. Escritas confirmadas invalidam coleções afetadas. O detalhe de pagamento tem namespace separado e não sobrescreve o ID de recuperação de uma venda criada.
- Preferências são aplicadas uma vez pelo evento de entrada de rota, com tema automático, nome, título e widgets preservados. Auditoria e atalhos não foram reintroduzidos. Alterar filtros invalida a leitura antiga e libera o loading, sem aplicar resultados do filtro anterior.

## Navegador no localhost

Edge headless, Reflex 0.10.1, HTTP simulado com espera de 350 ms por chamada; duas páginas com um registro cada. Mesmos dados e atraso da reprodução inicial. Baseline comprova veículos na tela de peças e clientes na de veículos. Após a mudança, o destino mostra seu carregamento sem esses registros incompatíveis.

| Rota | Antes: dados completos observados | Depois: feedback | Depois: primeira página | Depois: coleção completa |
|---|---:|---:|---:|---:|
| `/pecas` | 1676 ms | 206 ms | 578 ms | 935 ms |
| `/clientes` | 1714 ms | 284 ms | 656 ms | 1001 ms |
| `/veiculos` | 2071 ms | 92 ms | 446 ms | 806 ms |

A comparação anterior usa polling do Playwright; a final registra mutações do DOM para separar primeira página e completude. Os valores incluem trabalho do navegador e do runtime local, não só a espera HTTP. A lista completa de clientes pode aparecer enquanto seus indicadores auxiliares ainda estão pendentes.

Primeira visita a veículos: 16443 ms na reprodução inicial e 5874 ms na final. **Não atribuir essa diferença à otimização:** o primeiro ensaio incluiu transpilações iniciais do Vite e o cache de módulos não foi controlado. As linhas da tabela são navegações posteriores à primeira visita. Não foi medido desempenho de produção ou latência real do Xano.

Na janela de navegação registrada, foram 20 chamadas no baseline e 9 na execução final, incluindo abandono de consulta auxiliar na final. A carga duplicada por montagem foi removida; esses números não são uma comparação de consultas auxiliares concluídas, pois navegar agora pode cancelá-las.

No cenário com mil clientes (10 páginas, 120 ms/chamada), os primeiros clientes apareceram em 342 ms e a coleção foi completada em 1761 ms. Navegar durante HTTP de 1.200 ms levou 406 ms, antes de a rede terminar.

Foram percorridos: interação/teclado durante rede pendente; vendas antes dos catálogos; filtros fora de ordem; detalhe A/B e erros antigos; ID/link do pagamento; falha auxiliar isolada; falha da segunda página e retry; edição com GET antigo pendente; timeout; vazio final; coleção grande; logout/login em outra conta. Também houve salvamento de nome/título, tema automático acompanhando a preferência do sistema e download CSV. Nenhum erro JavaScript foi registrado.

## Mecanismo de carregamento e loop

`tests/performance_loading.py` lê o handler histórico do commit `970758fbd1ecf109000b6f8ec8dbe2c9dec9f07a` sem substituir a árvore de trabalho. Mil clientes, 10 páginas e uma consulta auxiliar vazia, espera de 40 ms por chamada, 11 chamadas nos dois casos:

| Medida sintética | Antes | Depois |
|---|---:|---:|
| Primeiro feedback publicado | 452.6 ms | 0.3 ms |
| Primeiros dados publicados | 452.6 ms | 51.5 ms |
| Carga completa | 452.6 ms | 540.3 ms |
| Maior intervalo do heartbeat | 452.7 ms | 18.1 ms |
| Atualizações observadas | 1 | 12 |

A carga completa sintética pode demorar mais devido às publicações intermediárias. O ganho comprovado está na resposta inicial e na disponibilidade do loop. Paginação sequencial e agregação local de vendas continuam tendo custo proporcional à coleção. Este benchmark não mede pintura do navegador nem banco remoto; os cenários do navegador complementam essa evidência.

## Qualidade e contratos

- Baseline: 107 testes aprovados, sem falhas preexistentes. Final: **122 testes aprovados** com `python -B -m unittest discover -s tests`.
- Contratos de grupos, bearer por chamada, parâmetros GET de vendas, erros de autenticação, payloads e resultado incerto de criação foram preservados. Recuperar link não repete criação/reserva; os testes de escrita usam apenas respostas simuladas.
- Ruff crítico (`E9,F63,F7,F82`) aprovado. Novos módulos/testes também passam na configuração completa. Comparação da árvore histórica com a final: 70 apontamentos gerais antes, 63 depois e **nenhum apontamento novo**; restam principalmente defaults mutáveis usados pelo modelo de estado Reflex e sugestões em código anterior. Não converter essas variáveis de sessão em `ClassVar`.
- Build `reflex export --frontend-only --no-zip` aprovado. Avisos existentes: Sitemap implícito, Radix implícito, recomendação de WSL/OneDrive e uso de `router.page` legado em leituras de ID. Esses avisos não comprovam que OneDrive seja a causa da lentidão.
- `git diff --check` aprovado. Os arquivos `reflex.lock/package*.json` já estavam modificados antes desta aplicação e foram preservados.

## Revisão com Impeccable

Craft floor consultado antes das edições. Revisados desktop 1440 px, intermediário 768 px e estreito 390 px; temas claro/escuro e comportamento automático, foco por teclado e ausência de overflow horizontal da página. Progresso/retry usam tokens da interface. Os totais incompletos não são apresentados como finais; a camada padrão do Radix que cobria o fundo dos indicadores de clientes foi tornada transparente para preservar sua superfície existente e a legibilidade.

Detector manual executado uma vez: dois avisos de fonte Inter e um advisory de grid decorativo, todos preexistentes no CSS. Mantidos intencionalmente por esta ser uma otimização que preserva a identidade do site; não foram adicionadas exceções globais ou trocadas fontes/fundos. Capturas locais ficam em `.impeccable/review/navigation/`; JSONs sem credenciais reais estão em `evidence/`.

## Reproduzir

Use a `.venv` existente. Para os cenários de navegador, pare os servidores normais antes de usar as portas locais; execute `python -B tests/browser/navigation_fixture.py`, depois o Vite em `.web` (`node node_modules/@react-router/dev/bin.cjs dev --host --port 3000`) e `python -B tests/browser/navigation_browser.py`. Playwright/Edge são ferramentas locais já instaladas, não novas dependências do app. Ao terminar, pare os dois servidores de teste e execute novamente o Reflex normal. **Não use o backend de fixture para operar o sistema.**

Benchmark sem servidor: `python -B tests/performance_loading.py`. Lint: `ruff check app tests --select E9,F63,F7,F82`. Compile o export com o servidor de desenvolvimento parado para evitar observação de um manifesto parcial de rotas.

## Entrega local

OpenSpec validado com `--strict`, progresso 20/20 e estado `all_done`; specs sincronizadas e change arquivada em 19/11/2026. Ver [encerramento](closure.md).
Após a validação, os processos de fixture foram encerrados e o Reflex normal foi
restabelecido em `localhost:3000` (backend `8001`). Clientes, veículos, peças e
vendas foram abertas em uma sessão nova sem credenciais: todas renderizaram o
login esperado, com HTTP 200 e sem a página Not Found. Esse smoke test não chamou
as APIs autenticadas nem revalidou os dados remotos.
