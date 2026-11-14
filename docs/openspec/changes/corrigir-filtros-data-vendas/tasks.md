# Tarefas

Atualização em 14/11/2026: a definição remota consultada já contém outra
implementação, com quatro caminhos de data. Ela foi sincronizada localmente
e o CLI retornou `No changes to push` para GET /vendas. O patch experimental
de operadores condicionais tornou-se obsoleto; as tarefas de publicação e
aceitação desses operadores abaixo não devem ser executadas. Os testes
autenticados de comportamento continuam pendentes.

- [x] Ler definição remota atual e identificar branch ativa.
- [x] Preparar patch isolado preservando alterações remotas não relacionadas.
- [x] Executar prévia CLI: somente `GET /vendas` atualizado.
- [ ] Publicar após autorização da alteração na API ativa.
- [ ] Confirmar aceitação dos operadores pelo importador Xano.
- [ ] Validar com sessão de teste: sem datas, início, fim e ambos.
- [ ] Conferir Clientes e Vendas, filtros preenchidos e bordas do intervalo.
