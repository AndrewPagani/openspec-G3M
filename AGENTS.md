# Contexto para trabalhar neste repositório

Antes de propor mudanças, consulte [o mapa de contexto verificado](docs/contexto-projeto.md), a spec relacionada em `docs/openspec/specs/` e os arquivos efetivamente afetados. As orientações operacionais existentes estão em [docs/AGENTS.md.txt](docs/AGENTS.md.txt).

O mapa registra divergências reais entre specs, implementação local e definições consultadas do Xano. Não trate `xanoscript/workspace_current` como cópia atualizada do remoto. O snapshot em `docs/contexto/xano-2026-11-13/` é evidência histórica de leitura, não diretório de publicação. Sua branch foi selecionada pelo perfil do CLI e o nome não foi confirmado.

Exceção pontual verificada: `api/vendas/vendas_GET.xs` foi sincronizado com
o workspace `147643`, branch explícita `v1`, em 14/11/2026. O snapshot dessa
consulta está em `docs/contexto/xano-2026-11-14/`. Os demais arquivos ainda
precisam de comparação. Não publicar `xanoscript/patch-vendas-datas/`, que
foi marcado como obsoleto.

Distinga requisitos, código local, definição remota e comportamento comprovado por execução. Leia a fonte citada para confirmar detalhes e revalide o remoto quando necessário. Não deduza registros, IDs de catálogos, regras de autorização ou integrações ativas apenas de comentários, nomes ou documentos antigos. Testes Python não comprovam autorização, concorrência ou transações no Xano.

Ao trabalhar na interface da change `revisar-venda-e-integracao-asaas`, usar
a skill `impeccable` por solicitação do usuário. Consultar as orientações
em `docs/openspec/changes/archive/2026-11-16-revisar-venda-e-integracao-asaas/AGENTS.md` e as
decisões registradas na exploração antes de alterar a tela de venda.
