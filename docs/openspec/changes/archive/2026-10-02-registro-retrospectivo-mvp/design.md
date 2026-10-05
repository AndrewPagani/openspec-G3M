## Context

Consulte `proposal.md` para a motivação e as especificações desta mudança para o comportamento observável que será registrado. A implementação está distribuída entre `app/`, os testes em `tests/`, contratos em `docs/` e esquemas Xano locais em `xanoscript/`. O workspace Xano não faz parte dos arquivos que podem ser verificados por este registro; sucesso de chamadas anteriores não comprova a configuração publicada atual.

## Goals / Non-Goals

**Goals:**

- Registrar como capacidades OpenSpec as funções identificáveis no código e cobertas pelos testes existentes.
- Distinguir comportamento da interface, responsabilidades do Xano e integrações ainda dependentes de validação no ambiente remoto.
- Após validar os artefatos, arquivar esta mudança na pasta `openspec/changes/archive/`, deixando `definir-nucleo-do-dominio` inalterada.

**Non-Goals:**

- Alterar a aplicação, dados, tabelas ou APIs remotas.
- Declarar como implementados ou validados webhooks, confirmação ASAAS, reconciliação, expiração, CRUD completo ou gráficos que não estejam comprovados no código e nos testes atuais.
- Sincronizar ou arquivar a mudança ativa `definir-nucleo-do-dominio`.

## Decisions

- Tratar as especificações como baseline retrospectiva: requisitos descrevem respostas observáveis implementadas e não ampliam o escopo além da aplicação atual.
- Manter quatro capacidades separadas por responsabilidade: integração Xano, cadastros/listagens, vendas/link de pagamento e dashboard.
- Usar estados vazios e erros conforme o código existente; não inferir dados ou comportamento do backend a partir apenas da documentação.
- Arquivar pelo comando OpenSpec para aplicar os deltas às especificações principais e preservar o histórico completo da mudança.

Alternativa considerada: copiar documentos de requisitos existentes diretamente para `archive`. Rejeitada porque isso não registra evidência de comportamento implementado nem cria especificações principais a partir dos deltas OpenSpec.

## Risks / Trade-offs

- [O Xano publicado pode divergir dos contratos locais] → Especificar a dependência externa e não afirmar validação remota atual.
- [A interface possui limitações não refletidas nos requisitos amplos do MVP] → Restringir o baseline ao que o código expõe e descrever link criado como diferente de pagamento confirmado.
- [O arquivamento pode criar especificações principais ainda inexistentes] → Validar cada delta e o destino de sincronização antes de executar o comando de archive.

## Migration Plan

1. Executar os testes disponíveis e validar os artefatos OpenSpec.
2. Confirmar que a mudança ativa `definir-nucleo-do-dominio` permanece em seu diretório original.
3. Executar o arquivamento OpenSpec desta mudança, sincronizando as quatro capacidades novas para `openspec/specs/` e movendo o registro para `openspec/changes/archive/`.
4. Revalidar a mudança arquivada, as especificações principais e o estado da mudança ativa.

Rollback: se a validação do arquivamento revelar conteúdo incorreto, corrigir as especificações e os artefatos da mudança arquivada por meio do fluxo OpenSpec, sem editar ou mover a mudança ativa.
