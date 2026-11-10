# Design

## Origem dos dados

- `GET /clientes` fornece nome (`CNome`), CPF, telefone, e-mail (`Email`) e
  `created_at`, além de paginação.
- `GET /vendas` fornece vendas paginadas e autorizadas pelo escopo do usuário.
  A data da venda e a relação com o cliente permitem derivar a última compra.
  Os status `Reservado` ou `Pendente` são contados como compras pendentes.
- Nenhum status de cliente é criado ou inferido.

## Cálculos

- Total de clientes: número de registros retornados após carregar todas as
  páginas do endpoint de clientes.
- Novos neste mês: clientes cujo `created_at`, convertido para o fuso de São
  Paulo, pertence ao mês e ano atuais.
- Compras pendentes: contagem de vendas acessíveis com status `Reservado` ou
  `Pendente`.
- Última atividade: data da venda mais recente associada ao cliente, entre as
  vendas acessíveis ao usuário. Sem venda correspondente, mostrar “Sem compras”.

As métricas relacionadas a vendas e a última atividade representam o escopo
autorizado pela API para o usuário atual; não devem ser apresentadas como
totais globais se a autorização restringir as vendas.

## Interface

Uma grade de indicadores antecede a busca e a tabela. A tabela mostra identidade
do cliente, CPF, e-mail, última compra e ação de abertura. A lista é paginada
localmente em grupos de dez e a busca inclui nome, CPF, telefone e e-mail.
A disposição adapta-se a telas estreitas sem modificar a tela de login.

## Limites de dados

Não exibir badge “Ativo”, pois não existe campo ou critério contratual para
esse estado. Não substituir informações ausentes por dados exemplificativos.
