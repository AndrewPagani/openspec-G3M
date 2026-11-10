## MODIFIED Requirements

### Requirement: Indicadores devem corresponder ao contrato e schema do MVP
O dashboard MUST apresentar, conforme o perfil, total de vendas, valor bruto, descontos, valor recebido por baixa manual, vendas pagas/canceladas e ticket médio; séries por período, status, forma realmente recebida, vendedor e mix de veículos/peças; quantidade de veículos por status e disponíveis; saldo disponível de peças e quantidade sem estoque (`qtd_disp = 0`). Cálculos MUST usar dados persistidos e MUST incluir somente parcelas locais com status `RECEBIDA` e timestamp de baixa. Dados ASAAS legados MUST NOT ser somados aos recebimentos locais. Vendas canceladas, vencidas ou sem parcela recebida MUST NOT compor receita recebida ou ticket médio. O dashboard MUST NOT exigir limiar configurável de estoque baixo, valor vendido de peças ou contadores persistidos de estoque reservado/vendido que não existam no schema atual. Atualização em tempo real, conversão, leads, test-drives, oficina, pós-venda e tabelas de acompanhamento MUST NOT integrar o MVP.

#### Scenario: Peças sem estoque
- **WHEN** existem peças com `qtd_disp = 0`
- **THEN** o indicador de peças sem estoque MUST contar esses registros

#### Scenario: Venda sem parcela recebida
- **WHEN** a venda não possui parcela local com baixa manual registrada
- **THEN** o valor recebido e o ticket médio MUST NOT contar a venda como paga

#### Scenario: Venda cancelada ou vencida
- **WHEN** venda está cancelada ou expirada
- **THEN** seus valores MUST NOT ser incluídos na receita recebida ou ticket médio
