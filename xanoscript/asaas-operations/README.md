# Operações auxiliares ASAAS

`asaas/prepare_catalog` completa idempotentemente os status Reservado, Paga e
Expirada exigidos pela spec, sob transação e somente em ASAAS_ENV=sandbox.
Não muda IDs/status antigos nem migra vendas. Foi executada uma vez e adicionou
os três status ausentes. Não é uma função somente leitura. Sem API pública.

Função `asaas/check_setup`, sem API pública. Consulta configurações dentro do
Xano e retorna somente indicadores, status HTTP e propriedades não secretas
dos webhooks. Não exporta variáveis nem retorna chaves/tokens/dados de clientes.

```powershell
xano.cmd function run asaas/check_setup --workspace 147643 --branch v1 --json '{}'
```

Executa GET /webhooks apenas se ASAAS_ENV=sandbox e existir a chave. A sondagem
autenticada envia um ID externo fictício ao endpoint publicado e deve falhar
por cobrança não vinculada (400), depois da autenticação. Não cria eventos,
cobranças, clientes ou recebimentos. HTTP 400 isolado deve ser interpretado
junto das sondas públicas com os mesmos campos, que retornaram 401 sem token.
Não executar com `--logs`, tracing ou depuração que exponha headers/variáveis.

Última execução registrada em setup-check.json na change. Ter chave presente
não prova que ela é válida no Sandbox. Ausência de ASAAS_ENV=sandbox impede
deliberadamente a consulta externa; não há fallback para produção.
