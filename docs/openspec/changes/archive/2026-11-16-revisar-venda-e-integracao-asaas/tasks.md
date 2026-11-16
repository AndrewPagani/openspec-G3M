Estado em 16/11/2026: implementação, publicação, homologação principal em Sandbox
e limpeza concluídas. Ver `handoff.md`, `runtime-validation.md` e `cleanup-final.json`.
As evidências distinguem implementação local, publicação e execução autenticada.
Publicação concluída em 147643/v1 após autorização explícita; dry-run final
`No changes to push`. Configuração e ciclo principal de venda/pagamento validados em Sandbox; limitações em runtime-validation.md.
`Allow Push: false` não bloqueia este workspace Free, conforme resposta do Xano.

## 1. Contrato e fontes
- [x] 1.1 Consultar Xano atual e formalizar decisões da exploração.
- [x] 1.2 Confirmar vendedor nas próprias vendas e gerente/admin em todas.

## 2. Interface e aplicação
- [x] 2.1 Implementar seleção/resumo responsivos com Impeccable.
- [x] 2.2 Remover inputs manuais da criação; implementar geração, recuperação, cópia e nova tentativa do link.
- [x] 2.3 Exibir pagamento ASAAS e preservar leitura de parcelas legadas; tratar papéis.

## 3. Backend Xano
- [x] 3.1 Preparar schema aditivo, configuração e funções ASAAS sem e-mail.
- [x] 3.2 Implementar cadastro recuperável e criação/reserva sem parcelas manuais.
- [x] 3.3 Implementar fatura persistida, acesso por perfil e proteção de tentativas ambíguas.
- [x] 3.4 Implementar confirmação autoritativa/webhook e cancelamento seguro (validação runtime em 4.5).
- [x] 3.5 Atualizar leitura de pagamentos e indicadores com compatibilidade legada.

## 4. Verificação
- [x] 4.1 Executar testes locais de validação, retry, URL, bloqueio de baixa ASAAS e histórico (permissões remotas em 4.5).
- [x] 4.2 Executar lint/build, detector Impeccable e conferir tela renderizada.
- [x] 4.3 Validar OpenSpec e gerar prévia isolada do Xano.
- [x] 4.4 Publicar após revisão e configurar ambiente/webhook no Xano (ver setup-validation.md).
- [x] 4.5 Executar cenários autenticados Sandbox de cliente, cobrança, webhook, cancelamento e concorrência de estoque (cobertura e limites em runtime-validation.md).
- [x] 4.6 Concluir estorno Sandbox e limpeza da rodada; REFUNDED/DONE confirmado, registros e funções temporárias removidos em 16/11/2026.
