## Context

Ver `proposal.md` para objetivo e escopo. A investigação de 19/11/2026 observou Reflex 0.10.1 e HTTPX 0.28.1 instalados. O problema foi relatado no ambiente local, não em produção.

### Evidência disponível

- `ResourceState.load` em `app/state/resource_state.py` compartilha `records`, `endpoint`, busca e erros entre recursos; troca o endpoint antes da rede, mas substitui a lista apenas ao final.
- Dezoito métodos `async` dos estados chamam HTTP síncrono. `app/services/xano_client.py` usa `httpx.request` no caminho síncrono e cria um `AsyncClient` por requisição no caminho assíncrono.
- Clientes percorre todas as páginas de clientes e depois todas as páginas de vendas antes de publicar os registros. Veículos e peças também percorrem todas as páginas sequencialmente. Vendas espera formas de pagamento antes da listagem; Nova venda consulta quatro referências em sequência.
- A maioria desses handlers não emite atualização intermediária. O dashboard é uma exceção: já limpa indicadores e usa `yield`, mas continua precisando respeitar a identidade da consulta ao retornar da rede.
- Simulação com handlers reais e processador de eventos instalado, substituindo a rede por esperas de 40 ms: três páginas de peças levaram cerca de 163 ms; três páginas de clientes mais cinco de vendas, 341 ms. Houve uma única emissão final, com `loading=False`, e registros antigos ainda existiam na primeira chamada. São medidas sintéticas de mecanismo, não latência do Xano nem medição de clique autenticado.
- Filtragem/ordenação local de clientes sintéticos: aproximadamente 0,6 ms/100 registros, 5,8 ms/mil e 66 ms/dez mil; a lista de dez mil normalizados ocupou cerca de 4 MB em JSON. Isso não mede o payload WebSocket real.
- O modo padrão de estado consultado é DISK e o projeto está no OneDrive; os arquivos observados eram pequenos. Não há evidência de que disco ou OneDrive sejam a causa principal. O build disponível em `.web/build` era de 16/11 e não serve como comparação atual de produção.

Fontes locais: mapa de contexto; specs principais afetadas; `app/pages/resource.py`, `sales.py`, detalhes, formulários e shell; estados correspondentes; testes de recursos, vendas, HTTP e parâmetros. As changes `personalizar-painel-local` e `remover-auditoria-e-atalhos-dashboard` estão implementadas e devem ser preservadas. Documentos gerais antigos que excluem ASAAS não substituem sua spec vigente.

## Goals / Non-Goals

**Goals:** mostrar a transição antes de a rede terminar; impedir mistura entre telas/contas; liberar a interação durante leituras; publicar a primeira página antes das seguintes; reutilizar conexões e referências estáveis; medir o resultado sem confundir fixtures com execução remota.

**Non-Goals:** novo backend ou endpoint agregado, publicação Xano, mudança de regras financeiras/estoque, substituir a carga integral de veículos por uma página fixa, cache de vendas/preços/disponibilidade, redesign, atualização de dependências, mudança do modo de persistência ou do diretório OneDrive. Também não ampliar nesta change os seletores hoje limitados à primeira página de referências de Nova venda nem corrigir nomes repetidos remotamente sem diagnóstico do payload.

## Decisions

### 1. Estados de apresentação separados por recurso

Separar os namespaces de listagem de clientes, veículos, peças e usuários; compartilhar helpers puros de consulta/normalização, não uma variável pública `endpoint` que decide o tipo de cartão de todas as páginas. Não basta herdar um estado Reflex com os campos no pai: os dados devem pertencer efetivamente ao namespace do recurso.

Cada recurso mantém sua busca, paginação visual, erro, progresso e registros; buscas podem ser mantidas ao retornar ao mesmo recurso, mas não atravessam recursos ou contas. Separar também o carregamento/erro da lista de vendas, dos detalhes e das referências de criação, preservando os dados de confirmação da venda.

Alternativa rejeitada: limpar globalmente todos os estados a cada clique. Isso pode apagar rascunhos e informações de recuperação de uma venda. Diálogos de edição devem ser adaptados ao estado correspondente e continuam atualizando a mesma entidade/ID.

### 2. Transição curta e leitura em background

O evento de entrada registra a consulta atual, prepara o estado visual e agenda a leitura. A apresentação não aguarda o HTTP para remover dados incompatíveis. Usar os recursos de eventos de rota do Reflex quando apropriado, com workers de leitura `@rx.event(background=True)`; manter rede e processamento demorado fora de `async with self`, usando esse contexto apenas para capturar ou publicar estado.

Três mecanismos têm responsabilidades distintas: `await` HTTP libera o loop; `yield`/contexto publica a atualização; background libera a fila interativa daquela sessão. Um só deles não substitui os demais. Não decorar o código bloqueante existente como background sem migrar a rede.

Cada carga captura uma chave imutável `(contexto autenticado, recurso, ID quando houver, filtros/período)` e uma geração. Antes de publicar resultado, progresso ou erro, conferir geração, contexto e rota atuais. A transição de rota invalida a geração anterior mesmo se o worker antigo terminar antes de o novo worker começar. Cancelar leituras sem consumidores quando possível; a checagem antes do commit é obrigatória mesmo quando o cancelamento falha.

Mudança de filtro, navegação para outro ID, logout e nova autenticação invalidam cargas anteriores. O encerramento de uma carga antiga não pode desligar o indicador da nova. Eventos de escrita não são cancelados nem repetidos automaticamente por navegação; preservam o fluxo atual de confirmação e resultado incerto.

### 3. Transporte assíncrono com ciclo de vida explícito

Administrar `httpx.AsyncClient` no serviço Xano, criado no loop de inicialização do backend e fechado no encerramento. A versão instalada dispõe de `app.register_lifespan_task`; usar esse mecanismo, sem criar o cliente em importação de módulo ou encerrar o pool após cada chamada. Configurar limites de conexão e preservar o timeout existente.

Migrar todos os caminhos HTTP acionados pela interface, inclusive login, leitura e ações existentes, para o transporte assíncrono. Cabeçalhos Bearer são montados por chamada; nunca gravar o token de um usuário nos headers globais do pool. Preservar grupos, caminhos, parâmetros e JSON, inclusive `sales_query_params`, tratamento de 401/403 e mensagens de falha.

O método síncrono pode permanecer para compatibilidade de utilitários, mas não será usado pelos handlers de interface. Não adicionar retries de POST/PATCH/DELETE, conciliar novamente cobranças ou paralelizar escritas. Timeouts/cancelamentos continuam liberando os recursos do transporte.

### 4. Coleções progressivas e trabalho auxiliar independente

Publicar a primeira página válida do recurso e continuar a carga completa em background. Exibir “Carregando mais registros” e a quantidade efetivamente carregada; somente remover a indicação parcial após a última página válida. Continuar usando os parâmetros/metadados existentes e preservar a exigência de todos os veículos. Não inventar totais com base na quantidade da primeira página.

Se uma página posterior falhar, manter apenas os registros válidos identificados como incompletos, com erro e ação explícita de nova consulta. Busca sem correspondências enquanto há páginas pendentes não é uma confirmação de lista vazia. Evitar republicar cópias completas por registro; acumular/normalizar por página e emitir progresso por lote.

Clientes apresenta registros antes de esperar vendas. Indicadores dependentes de toda a coleção de clientes só ficam completos depois da carga principal completa. A atividade e as pendências têm status independente: pendente durante a consulta, disponível somente com todas as páginas de vendas válidas, indisponível em falha. Nunca publicar uma soma parcial como total confirmado. A falha auxiliar não limpa os clientes nem a busca/posição da lista.

Manter a consulta atual de todas as vendas para essa análise, mas fora do caminho crítico de apresentação. Um endpoint agregado reduziria transferência, porém exige outro escopo/backend e não faz parte desta proposta.

### 5. Catálogos reutilizados e concorrência limitada

Cache somente de `/formas-pagamento`, `/status-veiculos` e `/veiculo-areas`, no serviço de referências, por contexto autenticado e ambiente/grupo. Escolha inicial: TTL de 300 segundos, não deslizante, a partir de resposta completa válida; limite de 128 chaves com remoção de entradas expiradas/antigas. Token e dados do cache permanecem fora dos estados públicos.

Requisições iguais em andamento compartilham um resultado; devolver cópias para impedir que uma alteração em estado modifique o cache. Um consumidor abandonando a tela não deve cancelar a requisição ainda usada por outro. Logout/troca de credencial invalida o contexto, inclusive impedindo que uma requisição antiga repovoe o cache. Falhas e respostas inválidas não são armazenadas, e não há fallback silencioso para catálogo expirado.

Uma atualização explícita força consulta nova e substitui o catálogo somente se válida. Mudança local confirmada em um catálogo invalida a chave correspondente. Preços, estoque, clientes, veículos, vendas, pagamentos e indicadores não recebem esse cache. O Xano continua validando a operação comercial.

Leituras independentes podem ocorrer em paralelo, com no máximo três requisições de leitura simultâneas por processo, independentemente de serem novas ou auxiliares; a tarefa de catálogo compartilhada conta uma vez. As páginas de uma mesma coleção seguem ordem para simplificar progresso e completude. Escritas conservam a ordem existente. A lista de vendas pode aparecer antes de formas de pagamento; esse filtro fica indisponível enquanto suas opções estão pendentes, sem impedir as outras ações.

### 6. Consistência de sessão, rascunhos e alterações

No logout invalidar dados de consulta e caches da identidade anterior, além dos campos de autenticação pertinentes. Preservar preferências locais por conta conforme `personalizar-painel-local`; não apagar todo o LocalStorage. Uma nova conta nunca recebe dados/erros do estado anterior.

Escritas confirmadas invalidam as cargas de listagem afetadas, impedindo que um GET iniciado antes da escrita restaure dados antigos. Atualizar a entidade/lista conforme o fluxo existente. Preservar a venda criada e seu ID em falha de geração de link; navegação não dispara nova criação nem repete reserva/cobrança. Rascunhos podem sobreviver dentro da mesma conta; não são reutilizados em outra identidade.

### 7. Apresentação e integração com mudanças recentes

Impeccable em modo Operate: manter temas, controles e estrutura existentes. Usar placeholders, texto de progresso e estados de erro/vazio distintos, sem sobreposição de dados da tela anterior. Revisar teclado, foco e o comportamento durante troca rápida. Na aplicação, ler o craft floor antes de editar UI e seguir a revisão/detector da skill instalada.

Preservar o título configurável, ordem/visibilidade de widgets, tema e nome local; preferências continuam sem escrever no Xano. Evitar a carga duplicada de preferências pelo shell e pelo dashboard, mantendo sua aplicação na primeira entrada, na troca de conta e ao salvar. Nenhuma Auditoria genérica ou atalho removido será reintroduzido.

### 8. Medição e aceite

Preparar baseline e comparação com o mesmo dataset, máquina e versão de runtime, separando primeira visita de visitas repetidas no `localhost:3000`. Medir clique/rota, primeiro feedback, primeiros registros, completude, atividade auxiliar, quantidade de requisições e bloqueio do loop. Registrar tamanho das mensagens/quantidade de nós quando a ferramenta permitir, sem supor que JSON sintético equivale ao payload real.

Critérios determinísticos têm prioridade sobre números frágeis: com uma resposta HTTP deliberadamente retida, a rota/feedback de destino aparece e outro evento da sessão é processado; nenhum dado incompatível aparece. Primeira página aparece antes de liberar as seguintes; clientes aparecem antes de liberar vendas. Uma resposta antiga liberada por último não altera a tela nova. Não prometer percentual de ganho antes da comparação.

Testar atraso, timeout, falha de página posterior, ordem invertida, conta diferente, mutação durante leitura, saída de rota e leitura compartilhada com dois consumidores. Testes locais com fixtures não validam autorização ou transação remota. Não criar cobranças ou dados reais apenas para medir navegação.

## Risks / Trade-offs

- Workers concorrentes podem sobrescrever mudanças recentes → geração por consulta, conferência antes de todo commit e invalidação após escrita.
- Separar estados afeta referências em componentes e testes → atualizar consumidores por recurso e testar edição/exclusão, não apenas abertura da lista.
- Coleção progressiva pode parecer completa → sinalização de parcialidade em lista, busca e indicadores; manter erro de página posterior visível.
- Carga integral ainda cresce com a base → a melhora inicial não elimina o custo total; registrar essa limitação e deixar paginação exclusivamente remota para outra proposta.
- Cache pode servir referência antiga por até cinco minutos → somente catálogos, bypass explícito e validação autoritativa no Xano; nenhuma disponibilidade/preço em cache.
- Pool e tarefas têm ciclo de vida por processo/loop → criar/fechar no lifespan, limpar requisições em andamento e testar inicialização/encerramento repetidos.
- Modo dev e OneDrive podem distorcer resultados → comparar frio/quente separadamente e não regenerar `.web` enquanto se mede o servidor dev.

## Migration Plan

Sem migração de dados ou deploy remoto. Na aplicação: registrar baseline, implementar serviço HTTP/referências, isolar estados, adaptar ciclo de leitura e progressão, migrar consumidores e validar fluxos existentes. Mudanças em produção somente após verificação local e revisão. Reversão por diff desta change, sem apagar arquivos gerados, preferências ou estados do usuário indiscriminadamente.

## Referências técnicas

- [Reflex: atualizações com yield](https://reflex.dev/docs/events/yield-events/).
- [Reflex: background, bloqueios e tarefas duplicadas](https://reflex.dev/docs/events/background-events/).
- [HTTPX: cliente assíncrono e reaproveitamento de conexões](https://www.python-httpx.org/async/).
- APIs do processador de eventos e do lifespan conferidas na instalação local; não tratar a documentação online como prova de que uma opção existe nesta versão.
