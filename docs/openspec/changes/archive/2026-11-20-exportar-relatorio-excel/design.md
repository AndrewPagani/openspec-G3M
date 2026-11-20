## Context

O evento `DashboardState.export_csv` usa indicadores formatados da interface e as datas atuais. O painel possui séries estruturadas e sinaliza filtros pendentes. A aplicação já tem HTTP assíncrono com limite de três leituras por processo, e as listagens usam paginação para exibir registros progressivamente. O relatório precisa de consultas completas, independentes das páginas e buscas abertas no navegador.

## Goals / Non-Goals

**Goals** — Fixar os filtros e a identidade no início de cada geração, manter a interface responsiva e entregar um arquivo utilizável com dados autorizados e tipos corretos.

**Non-Goals** — Agendamento, histórico de arquivos no servidor, alteração de fórmulas gerenciais ou de regras de vendas e estoque. O escopo das abas está em `proposal.md`.

## Decisions

1. **Fotografia da consulta aplicada.** Capturar credencial, conta, geração da sessão, parâmetros aplicados e agrupamento. Usar o mesmo construtor de parâmetros do Dashboard para buscar indicadores na geração e compartilhar sua validação numérica. Exportar os KPIs e séries canônicos, sem interpretar o texto em `R$` ou depender da ordem ou visibilidade dos widgets. Filtros posteriores não alteram a geração já iniciada. A hora de geração documenta a leitura, sem prometer uma fotografia transacional das várias APIs.
2. **Recorte de vendas conforme a métrica.** Na definição do Xano lida para esta análise, `indicadores` aplica datas, status, vendedor e forma à população de vendas. Tipo de item atua na consulta de itens e status do veículo atua no estoque. Conferir novamente o contrato ativo e os limites de datas antes de implementar. A aba Vendas usa a população comparável aos totais do painel, com esses escopos explicitados no arquivo. Verificar inclusividade de datas e fuso especialmente nas vendas próximas à meia-noite. Um filtro divergente não deve ser ignorado silenciosamente.
3. **Reutilizar APIs autenticadas.** Consultar `/gerenciamento/indicadores`, `/vendas`, `/clientes`, `/veiculos`, `/pecas` e `/usuarios` conforme o perfil. A autorização efetiva permanece no Xano. Para Vendas, avançar a paginação conforme os metadados, enviando `page` e `per_page` como strings e omitindo filtros vazios. Para Veículos, pedir a coleção completa e não restringir a disponíveis. Usar a opção padrão de listagem de Peças que inclui saldo zero, conforme confirmado durante a implementação. Usuários é uma lista gerencial restrita a administradores. Validar envelopes, páginas faltantes e duplicação de IDs. Uma negativa de acesso da API para uma aba esperada é falha, nunca indicação de lista vazia. As leituras independentes podem avançar no limite existente, com páginas de uma mesma coleção em sequência.
4. **Colunas explícitas.** Dashboard inclui metadados, KPIs e blocos das séries. Vendas inclui ID, data, cliente, vendedor, forma, status, bruto, desconto e valor final conforme disponíveis. Clientes inclui ID, nome, CPF, telefone, e-mail e cadastro. Veículos inclui ID, marca, modelo, ano, placa, quilometragem, preço e status conforme disponíveis. Peças inclui ID, nome, área, preço e saldo. Usuários inclui ID, nome, e-mail, perfil e cadastro. Campos opcionais ausentes ficam em branco. Preservar nomes, IDs e tipos sem serializar objetos inteiros ou buscar detalhes registro por registro. Campos como senhas, CPF de usuário, IDs externos, detalhes de cobrança e URLs de pagamento ficam fora das colunas.
5. **Geração fora da fila interativa.** Usar o ciclo assíncrono da aplicação para leitura e publicar progresso por etapa. Gerar o `.xlsx` com uma biblioteca Python própria para escrita de Excel, em tarefa fora do loop interativo. Usar valores tipados e estilo simples com cabeçalhos legíveis, filtros nas listagens e formatos de moeda e data. Gravar texto literal mesmo quando começa por `=`, `+`, `-` ou `@`, sem produção de fórmulas ou hiperlinks automáticos. Uma ação por sessão em andamento evita duplicar consultas. Revisar o botão e estados com Impeccable durante a implementação.
6. **Entrega vinculada à identidade.** Preferir download binário privado e temporário da própria aplicação, com autorização de uso restrita à sessão e expiração, se o envio direto pelo Reflex não suportar o volume medido. Usar a entrega direta quando comprovadamente adequada ao limite, sem enviar o conteúdo para armazenamento de estado do navegador nem publicar arquivos em assets. A troca de identidade invalida entrega pendente. Limpar qualquer artefato temporário ao concluir, falhar, expirar ou cancelar. Tratar a geração como sucesso apenas depois de validar todas as abas.

## Risks / Trade-offs

- **Volume grande ou resposta inconsistente** → Medir memória e transferência em fixtures com várias páginas. Escrever em lotes quando necessário e aplicar limite explícito de tamanho ou duração com mensagem, sem truncamento silencioso.
- **Diferença entre indicadores e vendas por janela de datas ou filtros** → Comparar casos de borda e cenário com filtros de item e estoque. Se as APIs não satisfizerem o mesmo recorte, registrar a divergência antes de liberar. Qualquer alteração remota exige comparação e prévia próprias.
- **Dados pessoais fora da aplicação** → Usar colunas permitidas, acesso por sessão, entrega privada e logs que registrem apenas etapa e tipo de falha. Dados financeiros e de estoque não ficam em cache para reaproveitar relatórios.

## Migration Plan

Implementar, validar e substituir a ação CSV junto com os testes de download. Sem migração de tabelas prevista. Para reverter, restaurar a ação CSV anterior e remover o serviço Excel e sua dependência do mesmo conjunto de alterações.

A revisão da branch ativa identificou que apenas Gerente e Vendedor podiam
consultar indicadores. O patch de `GET indicadores` habilita para
Administrador o acesso gerencial previsto na spec. O escopo de vendas do
Vendedor continua derivado da sessão do Xano.
