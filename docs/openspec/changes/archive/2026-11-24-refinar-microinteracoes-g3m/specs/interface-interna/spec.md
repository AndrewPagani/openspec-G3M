## ADDED Requirements

### Requirement: Nova venda indica mudanças no resumo e no pagamento

A interface MUST destacar o item afetado e a atualização do resumo ao adicionar ou remover veículo ou peça. MUST distinguir venda registrada, link disponível, cópia do link e pagamento confirmado. Os destaques de resultado MUST depender da evidência correspondente à ação e à venda atual.

#### Scenario: Operador muda os itens do resumo
- **WHEN** uma adição ou remoção é válida
- **THEN** o resumo MUST indicar a mudança perto dos itens ou do total, mantendo a seleção utilizável

#### Scenario: Venda é criada e link fica pendente
- **WHEN** a criação é confirmada e a fatura ainda está indisponível
- **THEN** a interface MUST informar que a venda está registrada e preservar a ação de recuperação do link, sem sinal de pagamento confirmado

#### Scenario: Operador copia o link ou recebe uma atualização da cobrança
- **WHEN** a área de transferência confirma a cópia ou a consulta retorna um novo status da cobrança atual
- **THEN** a interface MUST indicar o resultado específico junto ao controle ou status correspondente

### Requirement: Controles e cadastros apresentam feedback localizado

Login, cadastros e Configurações MUST apresentar foco por teclado perceptível. Seleções e erros de campo MUST indicar o estado perto do controle. Os fluxos de salvar, editar, excluir e personalizar MUST indicar o resultado no aviso ou na área afetada, conforme as operações disponíveis.

#### Scenario: Cadastro é salvo ou cliente é excluído
- **WHEN** a operação é confirmada pelo servidor
- **THEN** a interface MUST indicar a conclusão e manter o foco em um destino lógico se o controle original sair da tela

#### Scenario: Operação falha ou campo é inválido
- **WHEN** ocorre falha de validação ou persistência
- **THEN** a interface MUST apresentar a mensagem correspondente e preservar a possibilidade de correção, sem confirmação de sucesso

#### Scenario: Personalização é salva
- **WHEN** o operador salva as preferências do painel
- **THEN** o resultado MUST ser identificável perto da área de ações de Configurações

### Requirement: Dashboard indica atualização e entrega do Excel

O Dashboard MUST indicar a atualização da consulta junto aos filtros e o andamento da exportação junto à ação Excel. A indicação de entrega MUST corresponder ao disparo do download válido da sessão e distinguir falhas.

#### Scenario: Filtros aplicados e exportação concluída
- **WHEN** o Dashboard exibe o resultado do recorte aplicado e a geração entrega o arquivo
- **THEN** a interface MUST indicar os resultados junto às ações, sem apresentar a geração como conclusão do salvamento pelo navegador

### Requirement: Movimento preserva leitura, foco e continuidade

Os efeitos MUST ocorrer junto à interação que os originou. A navegação MUST identificar a aba atual e apresentar o estado da rota imediatamente, mantendo a estrutura do aplicativo estável. Com movimento reduzido, texto, ícone, cor ou contorno MUST comunicar os estados sem deslocamento. As animações MUST preservar interação, foco e rolagem nas telas com listas, imagens e gráficos.

#### Scenario: Navegação durante leitura pendente
- **WHEN** o operador troca de tela enquanto uma consulta está em andamento
- **THEN** a interface MUST identificar a nova tela sem depender do fim de uma animação e MUST descartar feedbacks obsoletos conforme a spec de navegação

#### Scenario: Confirmação com movimento reduzido
- **WHEN** a preferência por movimento reduzido está ativa
- **THEN** a interface MUST manter o texto e o foco perceptíveis com feedback estático equivalente
