# Delta de integração Xano

## ADDED Requirements

### Requirement: Filtros opcionais de data não devem gerar comparação inválida
`GET /vendas` MUST ignorar cada limite de data ausente na consulta ao banco e
MUST aplicar limites preenchidos sobre `venda.data_venda`, sem comparar o
timestamp com um limite nulo. MUST manter os demais parâmetros e o envelope
de resposta da definição remota revisada.

#### Scenario: Sem datas
- **WHEN** Clientes ou Vendas consultam sem datas
- **THEN** o backend MUST retornar a resposta paginada sem erro de parsing de timestamp

#### Scenario: Apenas início ou apenas fim
- **WHEN** somente um dos limites é preenchido
- **THEN** o backend MUST aplicar somente esse limite

#### Scenario: Ambos os limites
- **WHEN** início e fim válidos estão preenchidos
- **THEN** o backend MUST respeitar os dois limites e preservar a paginação
