# Validação da configuração — 14/11/2026

Após o usuário salvar ASAAS_ENV=sandbox e criar webhook/token, a função
`asaas/check_setup` foi executada em 147643/v1. Resultado sanitizado em
setup-check.json. Nenhum segredo é retornado pela função.

## Comprovado por execução remota

- Ambiente Sandbox, chave presente e token com comprimento entre 32 e 255.
- GET /v3/webhooks no Sandbox retornou HTTP 200, validando a chave nesse ambiente.
- A função `asaas/request` usada na integração também retornou a estrutura
  esperada da consulta; envelope HTTP validado nessa leitura.
- Encontrado um webhook com URL exata do endpoint publicado, enabled=true,
  interrupted=false, SEQUENTIALLY e os 15 eventos escolhidos.
- Sonda HTTP interna com token correto atingiu `asaas/reconcile` e retornou a
  mensagem esperada de cobrança não vinculada. O ID fictício não criou evento,
  cobrança ou pagamento. Isso comprova autenticação, não confirmação financeira.
- Sete sondas públicas complementares retornaram 401 sem token, com cabeçalho
  incorreto ou token só no corpo. Sem tracing ou logs de segredos.

## Catálogos corrigidos

Leitura real mostrou apenas Pendente (1), Concluída (2) e Cancelada (3) no
catálogo de venda. IDs preservados. A função idempotente `asaas/prepare_catalog`
adicionou os requisitos ausentes: Reservado (4), Paga (5) e Expirada (6).
Esses IDs foram retornados pelo Xano, não fixados no código. Nenhuma venda antiga
foi migrada ou reclassificada.

O catálogo possui PIX, Cartão de Crédito e Boleto Bancário. A conciliação foi
corrigida para reconhecer também Boleto Bancário por nome normalizado, sem
inventar IDs. Correspondência ambígua mantém FK nula. Patch restrito à função.

Perfis reais: Gerente, Vendedor e Cliente. Não existe Administrador no catálogo
consultado; não foram criados perfil/conta nem atribuídos privilégios. O suporte
do código a Administrador depende de um perfil real com esse nome.

## Limites e pendências

Apenas datasource live disponível. Criar asaas_verificacao foi recusado com
HTTP 403: `Not supported. Please upgrade your Xano instance.` Não houve upgrade
nem criação de registros sintéticos em live. Script da tentativa:
scripts/prepare_xano_asaas_test_source.mjs.

Esta etapa não criou clientes, usuários, veículos, peças, vendas ou cobranças.
Somente o catálogo recebeu as 3 adições documentadas. Continuam pendentes
cadastro integrado, reserva concorrente, cobrança, pagamento Sandbox, eventos
reais/duplicados/atrasados, cancelamento e matriz de autorização por perfil.
Não arquivar a change ou declarar recebimento validado com base nessas sondas.

Pacote auxiliar xanoscript/asaas-operations: check_setup (leitura, sem API pública)
e prepare_catalog (adições idempotentes, guarda Sandbox). Ruff do gerador passou.
Dry-runs finais dos dois pacotes: `No changes to push`.
