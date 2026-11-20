## 1. Contratos de leitura

- [x] 1.1 Revalidar as definições ativas de indicadores, vendas, clientes, veículos, peças e usuários. Registrar formatos, campos, permissões e paginação observados, distinguindo definição de teste autenticado.
- [x] 1.2 Comparar o recorte de vendas com o Dashboard para datas, vendedor, status e forma, incluindo meia-noite e os filtros de item e estoque. Registrar e resolver divergências antes de liberar o relatório.

## 2. Dados e geração do Excel

- [x] 2.1 Capturar o contexto aplicado do Dashboard e normalizar indicadores e séries com tipos preservados. Comparar com o painel em exemplos gerenciais, de vendedor e com séries opcionais ausentes.
- [x] 2.2 Implementar a coleta das abas usando o cliente HTTP existente, com paginação completa, escopo por perfil e limite de concorrência. Verificar todas as páginas, estoque zero, veículos indisponíveis, lista vazia e falha em página posterior.
- [x] 2.3 Adicionar a dependência de escrita de Excel e gerar as abas com colunas permitidas e estilos leves. Reabrir o arquivo em um leitor compatível para verificar nomes das abas, cabeçalhos, tipos de célula, zeros iniciais, formato monetário e texto literal semelhante a fórmula.

## 3. Ação e entrega

- [x] 3.1 Substituir a ação CSV por **Exportar Excel** e informar progresso por etapa. Aplicar Impeccable aos estados da ação e verificar teclado, foco, temas e tela estreita. Confirmar indisponibilidade com filtros pendentes e ausência de gerações duplicadas.
- [x] 3.2 Gerar o arquivo fora da fila interativa e entregar somente à sessão solicitante. Verificar troca de conta, logout, tempo limite, limpeza de temporários quando usados e nova tentativa após falha sem download parcial.

## 4. Validação integrada

- [x] 4.1 Executar fluxo de download no navegador com dados controlados para vendedor, gerente e administrador. Conferir as abas por perfil, a ausência de Configurações e de campos excluídos e as contagens de uma exportação multipágina.
- [x] 4.2 Medir duração e tamanho em uma coleção representativa, verificar que a navegação permanece operável e documentar os limites observados. Distinguir simulação local de autorização Xano validada.
- [x] 4.3 Atualizar documentação de uso e o teste de download do Dashboard. Executar testes, lint, build e validação OpenSpec, registrando resultados antes de concluir a aplicação.
