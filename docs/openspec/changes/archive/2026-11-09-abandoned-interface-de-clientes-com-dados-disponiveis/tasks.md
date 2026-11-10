# Tarefas

## 1. Especificar a mudança

- [x] 1.1 Definir campos apresentados conforme o contrato atual de clientes.
- [x] 1.2 Definir “última atividade” como a venda mais recente autorizada.
- [x] 1.3 Excluir status de cliente sem suporte contratual.
- [x] 1.4 Documentar escopo de autorização das métricas derivadas de vendas.

## 2. Implementar a interface

- [x] 2.1 Normalizar nome, CPF, telefone e e-mail dos registros do Xano.
- [x] 2.2 Derivar a última compra por cliente a partir das vendas acessíveis.
- [x] 2.3 Calcular total, novos no mês e compras pendentes sem dados estáticos.
- [x] 2.4 Adicionar busca, paginação, ação para abrir cadastro e layout responsivo.
- [x] 2.5 Aplicar o tema Dark Slate sem alterar a tela de login.

## 3. Validar

- [x] 3.1 Cobrir normalização de contato, atividade e métricas com testes.
- [x] 3.2 Executar a suíte Python e compilação.
- [ ] 3.3 Concluir exportação do frontend quando o Windows liberar o arquivo
  bloqueado em `node_modules` (`EBUSY`).
