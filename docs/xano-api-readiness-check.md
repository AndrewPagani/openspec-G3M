# Verificação de prontidão das APIs Xano

## Novo fluxo manual de parcelas

O contrato em andamento está em
`openspec/changes/registro-manual-de-parcelas-no-xano/`. O objetivo é manter
venda, cronograma e baixas no Xano sem ASAAS, checkout, cobrança ou consulta a
processador externo.

O código local contém:

- nova tabela `venda_parcela`, com unicidade por venda/número e estados locais;
- criação de 1–24 parcelas na mesma transação da venda/reserva, centavos
  distribuídos no plano e vencimentos no fuso `America/Sao_Paulo`;
- baixa integral autorizada somente a gerente/administrador, com forma
  realmente recebida, usuário e timestamp do servidor;
- leitura de parcelas locais e indicadores baseados somente em baixas manuais;
- cancelamento local de parcelas pendentes e neutralização das rotas antigas de
  link, conciliação, notificação e Webhook, preservando dados legados.

O app local exibe o cronograma e oferece ação de baixa somente para gerente ou
administrador. A autorização continua obrigatória no backend. A baixa é um
registro administrativo, não prova nem processa liquidação bancária.

## Validação local

- `openspec validate registro-manual-de-parcelas-no-xano --strict` passou.
- A suíte local `python -m unittest discover -s tests -v` passou com 20 testes.
- `python -m reflex export --frontend-only --no-zip` concluiu com sucesso em
  diretório temporário fora do OneDrive; o build direto na pasta sincronizada
  falhou ao tentar remover um diretório de saída somente leitura.
- `xano workspace push --directory xanoscript/workspace_current --workspace
  147643 --dry-run` mostrou 1 tabela criada e 11 endpoints atualizados/criados,
  sem erro de sintaxe. Após autorização explícita, o CLI publicou a mudança e
  sincronizou 57 documentos; a prévia posterior retornou `No changes to push`.
- Três testes protegidos representativos do Xano (vendas, cancelamento e
  indicadores) continuam retornando `401 Unauthorized` antes das asserções.
- **Correção do erro `ParseError: Invalid value for param:[50,...,1]`:** a
  consulta de itens do dashboard usava `contains` sobre uma lista de IDs
  derivada das vendas (até 50 pela paginação padrão). Substituída por join
  direto com `venda`, aplicando no banco os mesmos filtros da consulta de
  vendas. Após publicar a correção, a tela autenticada `/gerenciamento`
  carregou os indicadores e as séries, sem o erro 400; o CLI voltou a mostrar
  `No changes to push`.

## Bloqueadores antes da versão final

1. **Autenticação dos testes Xano:** os testes protegidos continuam falhando
   com `401 Unauthorized` antes das asserções; não remover `auth = "user"`
   para contornar. Configurar fixtures/sessão de teste suportadas ou executar
   com conta de teste autenticada.
2. **Datas e centavos:** validar runtime para fim de mês, ano bissexto, virada
   de ano, divisão com resto e valores menores que um centavo por parcela.
3. **Permissões e idempotência:** testar gerente, administrador, vendedor,
   baixa repetida, tentativa concorrente, forma inválida, venda cancelada e
   disputa entre baixa e cancelamento.
4. **Estoque concorrente:** a reserva atual valida disponibilidade antes das
   gravações da transação. Verificar e corrigir concorrência para impedir venda
   duplicada do mesmo veículo ou saldo de peças negativo.
5. **Dados históricos:** preservar tabela/campos ASAAS e eventos existentes;
   confirmar que nenhum Webhook antigo pode alterar registros depois da
   publicação. Não remover segredos sem inspeção operacional separada.
6. **Dashboard e histórico:** validar filtros por forma realmente recebida e
   data de baixa; confirmar que dados legados ASAAS não entram em totais locais.

## Decisão de segurança operacional

Não foram executadas operações financeiras. O app não inicia chamadas ASAAS
nem exibe links antigos. Nenhum valor de segredo ou registro de tabela foi lido
ou alterado pelo envio. A mudança foi publicada no workspace 147643 após
aprovação expressa; os testes runtime autenticados continuam pendentes.
