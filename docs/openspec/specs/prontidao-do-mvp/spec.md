# prontidao-do-mvp Specification

## Purpose
Formalizar decisões, dependências e critérios de aceite necessários para concluir o MVP sem confundir schema publicado, contrato planejado e comportamento verificado.

## Requirements

### Requirement: Contrato implementado deve corresponder ao schema e às decisões aprovadas
Requisitos MUST identificar se são suportados pelo schema atual, contrato planejado ou validação remota. O contrato do MVP MUST usar os identificadores e campos existentes; `cliente.Email` pode permanecer anulável para registros antigos, mas MUST ser exigido em novos cadastros; placa/chassi são únicos quando informados. O MVP MUST NOT pressupor tabelas de auditoria genérica, histórico de estoque ou CRUD de permissões que não fazem parte do schema. Mudanças de schema ou de regra de negócio MUST ser aprovadas antes de alterar o contrato.

#### Scenario: Campo opcional ausente no schema
- **WHEN** um requisito exige campo ou tabela não presente no schema do MVP
- **THEN** a implementação MUST aguardar aprovação da alteração de schema ou MUST ser reescrita para usar os dados suportados

#### Scenario: E-mail ausente em registro legado
- **WHEN** cliente legado não possui e-mail
- **THEN** a leitura MUST continuar compatível e a criação de novo cliente MUST exigir e-mail

### Requirement: Paginação, busca, limites e configuração devem ser explícitos
Coleções MUST aceitar `page` e `per_page` com padrão 1 e 20, limitado a 100, além dos filtros definidos para cada recurso. Valores fora desses limites MUST ser rejeitados com erro compreensível. O backend MUST validar intervalo de datas e impor um limite de período operacional aprovado para agregações. Ambientes ASAAS e segredos MUST ser configurados explicitamente e separados entre Sandbox/Produção e chave de API/segredo de Webhook; MUST NOT haver fallback silencioso para Produção. Segredos MUST permanecer no Xano.

#### Scenario: Paginação fora dos limites
- **WHEN** é solicitada página inválida ou `per_page` acima do máximo
- **THEN** o backend MUST rejeitar a entrada com erro compreensível e MUST NOT retornar coleção ilimitada

#### Scenario: Segredo de Webhook ausente
- **WHEN** o token específico do Webhook não está configurado
- **THEN** o endpoint MUST falhar fechado sem aceitar a chave da API ASAAS como substituta

### Requirement: A conclusão do MVP depende de testes de aceite e runtime
O MVP MUST NOT ser considerado concluído até que cenários de autorização, venda inválida, disponibilidade, concorrência, cancelamento idempotente, preço congelado, desconto, transição, atomicidade, Webhook duplicado/fora de ordem, timeout ASAAS, privacidade e falha de notificação tenham sido validados. Testes locais de interface MUST NOT ser apresentados como evidência de autorização ou transação no Xano. O archive da mudança MUST aguardar conclusão das tarefas de negócio, implementação e validação nela registradas.

#### Scenario: Testes de interface passam sem teste de backend
- **WHEN** testes locais do app passam mas cenários autenticados Xano não foram executados
- **THEN** a mudança MUST permanecer com validação de backend pendente e MUST NOT declarar o MVP concluído

#### Scenario: Critérios de aceite e runtime aprovados
- **WHEN** decisões estão aprovadas e cenários de aceite locais e remotos passam
- **THEN** a mudança pode ser revisada para archive após confirmar que as tarefas e especificações correspondem à implementação
