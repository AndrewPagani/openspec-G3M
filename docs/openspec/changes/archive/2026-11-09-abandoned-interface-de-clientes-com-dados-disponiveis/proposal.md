# Proposta: Interface de clientes com dados disponíveis

## Por que

A listagem atual de clientes mostra uma identificação resumida e não aproveita
os dados cadastrais existentes no contrato do Xano. A nova interface deve
facilitar a consulta de contatos e da atividade comercial sem exigir mudanças
no schema ou introduzir valores de demonstração.

## O que muda

- Apresentar clientes em tabela com nome, CPF, e-mail, última atividade e ação
  para abrir o cadastro.
- Exibir telefone como informação secundária junto ao nome.
- Oferecer busca por nome, CPF, telefone ou e-mail e paginação local.
- Calcular o total de clientes e a quantidade criada no mês a partir dos
  registros e de `created_at` já retornados.
- Calcular compras pendentes a partir das vendas disponíveis ao usuário,
  considerando os status `Reservado` e `Pendente`.
- Exibir a última compra registrada por cliente como sua última atividade,
  respeitando os registros de venda que o usuário está autorizado a consultar.
- Manter o tema Dark Slate usado pelo dashboard.

## Fora do escopo

- Alterar tabelas, campos, índices, permissões ou endpoints do Xano.
- Exibir “Clientes ativos”: o contrato não fornece status nem regra para
  determinar atividade de um cliente.
- Tratar eventos diferentes de compra como atividade do cliente.
- Expor vendas fora do escopo de autorização do usuário.
- Apresentar métricas não calculáveis com os dados das APIs atuais.

## Impacto

- Reflex: `app/pages/resource.py` e `app/state/resource_state.py`.
- Estilos: `assets/styles.css`.
- Testes: `tests/test_resource_state.py`.
- API: consumo autenticado de `GET /clientes` e `GET /vendas`; sem publicação
  ou alteração do backend Xano.
