## 1. Baseline reproduzível

- [x] 1.1 Preparar um harness local de navegação com respostas controláveis e sem chamadas externas, reproduzindo estado compartilhado, rede lenta e carga de múltiplas páginas; verificar que captura o conteúdo anterior e registrar tempos de rota, primeiro feedback, primeiros dados, completude e chamadas antes das alterações.
- [x] 1.2 Acrescentar testes de regressão para os contratos atuais de parâmetros, headers, grupos e resultados incertos de escrita; verificar os testes existentes de HTTP, recursos, autenticação e vendas antes da migração e registrar falhas preexistentes separadamente.

## 2. Transporte não bloqueante

- [x] 2.1 Implementar cliente HTTP assíncrono com pool criado/fechado pelo lifespan da aplicação, preservando timeout e headers por chamada; verificar reutilização, encerramento repetido, cancelamento e ausência de mistura de credenciais com transporte simulado.
- [x] 2.2 Migrar os caminhos HTTP dos estados de interface, incluindo login, formulários, recursos, detalhes e vendas, e o helper de atividade de clientes, para o transporte assíncrono; verificar ausência de chamadas bloqueantes nesses caminhos, loop responsivo durante I/O e contratos existentes preservados, sem retries novos de escrita.

## 3. Isolamento e ciclo de navegação

- [x] 3.1 Separar os namespaces de listagem de clientes, veículos, peças e usuários e adaptar seus componentes/diálogos, preservando helpers puros; verificar independência de registros, busca, paginação, erros e edição entre recursos, sem campos compartilhados por herança de estado.
- [x] 3.2 Implementar o ciclo de leitura em background com captura/publicação sob bloqueio curto, chave de consulta e geração invalidada na transição; verificar outro evento da mesma sessão enquanto a rede está retida, descarte de respostas/erros antigos e que uma finalização antiga não encerra o loading novo.
- [x] 3.3 Adaptar páginas, shell, detalhes e vendas para mostrar o estado inicial antes da rede e separar loading/erro da listagem, detalhe e criação; verificar mudança rápida de recurso/ID/filtro sem cartões, links ou mensagens incompatíveis na tela de destino.

## 4. Coleções progressivas e dados auxiliares

- [x] 4.1 Publicar a primeira página válida de clientes, veículos e peças e continuar a carga integral em background, com atualizações por página/lote; verificar primeira página visível antes da segunda, carga de todos os veículos e manutenção dos metadados/parâmetros atuais.
- [x] 4.2 Separar a carga auxiliar de vendas da apresentação dos clientes, com indicadores pendentes/disponíveis/indisponíveis; verificar clientes utilizáveis com vendas retidas, falha em qualquer página de vendas sem totais parciais e restauração dos indicadores após consulta completa válida.
- [x] 4.3 Ajustar busca, paginação visual, totais e feedback durante carga parcial e falha de página posterior; verificar diferenciação de vazio final, ausência parcial de correspondências, erro de formato e lista incompleta com nova consulta explícita.

## 5. Catálogos e controle de concorrência

- [x] 5.1 Implementar cache privado somente dos três catálogos definidos, com TTL não deslizante de 300 segundos, escopo de ambiente/credencial e limite de 128 chaves; verificar relógio controlado, expiração, cópias independentes, resposta inválida/falha não armazenada e bypass de atualização explícita.
- [x] 5.2 Deduplicar leituras iguais em andamento e limitar leituras HTTP simultâneas a três por processo; verificar dois consumidores compartilhando uma chamada, saída de um deles sem cancelar o outro, liberação de capacidade em falhas e prevenção de repopulação por contexto invalidado.
- [x] 5.3 Integrar referências aos formulários e vendas e executar leituras independentes em paralelo dentro do limite; verificar vendas apresentadas antes de formas de pagamento retidas, filtro desativado enquanto pendente e preservação dos IDs, seleções e comportamento atual de Nova venda.

## 6. Sessão, escritas e integração existente

- [x] 6.1 Invalidar consultas, dados operacionais e referências da identidade anterior em logout/troca de conta, preservando preferências locais por conta; verificar resposta antiga após novo login, ausência de dados/rascunhos cruzados e manutenção de tema/nome/título configurados.
- [x] 6.2 Invalidar gerações afetadas por alterações confirmadas e preservar a ordem/recuperação das ações de cadastro, estoque e vendas; verificar GET antigo após edição/exclusão, timeout sem repetição automática e manutenção da venda criada/ID em falha do link, sem novas reservas ou cobranças no teste.
- [x] 6.3 Evitar a aplicação duplicada de preferências no shell e dashboard sem perder a primeira aplicação, troca de conta ou salvamento; verificar temas, título, widgets, exportação e ausência da Auditoria e atalhos removidos.

## 7. Validação integrada e entrega

- [x] 7.1 Executar os cenários no navegador com o runtime real do Reflex e HTTP simulado: navegação rápida, respostas fora de ordem, detalhe A/B, logout/login, páginas parciais, erro, timeout e escrita durante leitura; verificar também que teclado e navegação continuam operáveis enquanto a rede está pendente.
- [x] 7.2 Aplicar Impeccable aos estados de carregamento/progresso, lendo o craft floor antes de editar UI; revisar temas escuro/claro/automático, desktop e tela estreita, foco e contraste, e seguir o detector/revisão final da skill instalada, registrando as evidências sem redesenhar as telas.
- [x] 7.3 Comparar baseline e versão final no localhost, com primeira visita e visitas repetidas separadas e o mesmo dataset/atrasos, incluindo coleções grandes; entregar relatório de tempos, bloqueio do loop, chamadas e limitações, comprovando feedback antes da rede e dados principais antes dos auxiliares sem prometer um ganho remoto não medido.
- [x] 7.4 Executar os testes pertinentes, lint e build do projeto e revisar o diff; registrar comandos/resultados, atualizar o contexto necessário e verificar preservação dos contratos e fluxos existentes, distinguindo claramente fixtures locais de qualquer evidência autenticada Xano.
