# Proposta: Registrar parcelas e baixas manuais no Xano

## Por que

O fluxo atual cria links de checkout ASAAS e depende de Webhooks/reconciliação
para confirmar pagamentos. O produto agora deve funcionar sem ASAAS e sem
qualquer motor de pagamento. O Xano será o registro operacional de vendas,
parcelas previstas e parcelas recebidas; a liquidação financeira ocorrerá fora
do sistema e será confirmada manualmente por gerente ou administrador.

## O que muda

- Ao criar uma venda, o backend criará atomicamente de 1 a 24 parcelas
  positivas, distribuindo o total em centavos e colocando eventual resto na
  última parcela. A primeira vence na data local da venda em
  `America/Sao_Paulo`; as seguintes vencem mensalmente.
- Apenas gerente/administrador poderá registrar a quitação integral de uma
  parcela; a baixa guardará data/hora, usuário que confirmou e forma de
  pagamento realmente recebida.
- A primeira parcela baixada torna a venda `Paga` e permite a entrega conforme
  a regra comercial já aprovada. As parcelas restantes continuam pendentes.
- Cancelamento de venda reservada cancelará parcelas pendentes no próprio Xano
  e liberará os recursos atomicamente, sem chamada a serviço externo.
- O app deixará de solicitar ou exibir links ASAAS e exibirá o cronograma e o
  estado das parcelas com ações de baixa autorizadas.

## Fora do escopo

- Processar, iniciar, custodiar ou confirmar automaticamente transferências,
  Pix, cartões, boletos ou qualquer pagamento.
- Integrar outro gateway, enviar cobranças/notificações ou consultar bancos.
- Baixas parciais, estorno de venda paga e edição do plano após a criação.
- Apagar registros, campos ou referências ASAAS históricos durante a migração.

## Capabilities

### Modificadas

- `vendas-e-link-pagamento`: substituir checkout e confirmação externa por plano
  local de parcelas e baixa manual autorizada.
- `integracao-xano`: manter somente os grupos usados pela aplicação; pagamentos
  não dependem de Webhook ou gateway.
- `dashboard-gerencial`: contabilizar somente parcelas locais com baixa manual
  e usar a forma realmente recebida nos filtros.

## Impacto

- Reflex: `app/pages/sales.py`, `app/state/vendas_state.py` e serviços/rotas de
  detalhe de venda.
- Xano: criação atômica da venda e parcelas, novo endpoint de baixa, leitura de
  parcelas e cancelamento sem chamadas externas; indicadores devem contabilizar
  apenas parcelas locais confirmadas.
- Schema: adicionar uma tabela de parcelas locais, mantendo as tabelas/campos
  ASAAS antigos em modo legado até verificar dados e dependências.
- Documentação e testes: atualizar o contrato API, specs OpenSpec, checklist de
  prontidão e testes de venda/pagamento.

O novo schema/API Xano será pré-visualizado e mostrado antes de qualquer
publicação. Nenhuma variável de ambiente ou segredo será lido, alterado ou
removido por esta mudança.
