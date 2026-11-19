## Why

A navegação no `localhost:3000` pode manter conteúdo da tela anterior enquanto consultas bloqueantes e sequenciais são executadas. A análise encontrou estado de listagem compartilhado entre recursos, carregamento enviado apenas ao final de vários eventos e espera por dados auxiliares antes de mostrar os principais; corrigir esses pontos deve melhorar a resposta da interface sem alterar regras de negócio.

## What Changes

- Isolar resultados, filtros, erros e carregamento por recurso/consulta e identidade autenticada; impedir que uma tela apresente registros de outra ou aceite respostas de uma navegação encerrada.
- Enviar o estado inicial de carregamento antes da espera de rede e executar leituras demoradas sem ocupar a fila interativa do usuário durante toda a consulta.
- Migrar o caminho HTTP da interface para operações não bloqueantes com reaproveitamento de conexões; manter payloads, cabeçalhos, erros e semântica das escritas existentes.
- Apresentar páginas de clientes, veículos e peças progressivamente, identificando resultados parciais e preservando o carregamento integral atualmente exigido para veículos.
- Separar a apresentação dos clientes da consulta auxiliar de vendas, distinguindo indicadores pendentes, completos e indisponíveis.
- Reutilizar temporariamente apenas catálogos de referência, deduplicar leituras iguais em andamento e limitar o paralelismo de consultas independentes.
- Verificar navegação rápida, respostas fora de ordem, troca de conta e regressões de formulários/vendas, com métricas comparáveis de antes/depois no ambiente local.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface-interna`: navegação responsiva, carregamento antecipado e isolamento de conteúdo por rota, consulta e sessão.
- `cadastros-e-listagens`: apresentação progressiva das coleções e independência temporal entre clientes e indicadores auxiliares de vendas, sem apresentar dados parciais como completos.
- `integracao-xano`: leituras concorrentes controladas, reutilização limitada de catálogos e preservação de autenticação/contratos durante a execução não bloqueante.

## Impact

- Áreas previstas: `app/state/resource_state.py`, estados de vendas/detalhes/formulários/autenticação/dashboard/configurações, `app/services/xano_client.py`, registro de eventos em `app/app.py`, shell e páginas afetadas. Testes de serviço, estado e navegação precisarão acompanhar a mudança de execução.
- Nenhuma nova API, publicação Xano, mudança de schema, integração financeira ou nova biblioteca de runtime. Estados visuais seguem Impeccable e o padrão atual; personalizações locais e remoção da Auditoria já implementadas serão preservadas.
- Fora do escopo: redesign, migração de framework, paginação exclusivamente no servidor que suprima a carga integral de veículos, endpoint agregado de atividade de clientes, cache de estoque/preços/vendas, mudança de cálculos financeiros e correção remota dos nomes repetidos em vendas sem diagnóstico autenticado.
- Ganhos em tempo de clique autenticado ainda não foram medidos. A evidência inicial é de código e simulações em memória; os critérios de aceite exigem medição e verificação em navegador durante a implementação.
