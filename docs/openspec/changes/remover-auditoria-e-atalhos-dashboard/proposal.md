# Remover Auditoria genérica e atalhos do Dashboard

## Contexto

A aplicação local ainda registrava a página genérica `/auditoria`, embora o
cliente local não tenha um endpoint correspondente e a auditoria genérica não
faça parte do schema atual do MVP. O Dashboard também exibia atalhos para criar
clientes, veículos e vendas, com controles de personalização que deixaram de
ter uso.

## Escopo

- Remover a rota e o item de navegação da Auditoria genérica na aplicação local.
- Remover do Dashboard os atalhos “Novo cliente”, “Novo veículo” e “Nova venda”.
- Remover das Configurações os controles de personalização desses atalhos.
- Manter as rotas de cadastro existentes e suas permissões.
- Aceitar preferências locais antigas que contenham atalhos, sem voltar a exibi-los.
- Não alterar APIs, dados ou definições remotas do Xano; o endpoint remoto
  `auditoria_parcelas` é distinto da página genérica removida.

## Fora de escopo

- Remover ou alterar endpoints e dados no Xano.
- Remover as páginas ou rotas de cadastro de clientes, veículos e vendas.
- Alterar métricas, filtros, exportação ou permissões do Dashboard.

## Critérios de aceitação

- A navegação autenticada não exibe Auditoria e a aplicação local não registra
  a rota `/auditoria`.
- O Dashboard não apresenta os três atalhos de criação.
- As Configurações não permitem ativar atalhos removidos.
- Preferências antigas contendo atalhos continuam carregando sem erro, mas os
  atalhos não são mostrados.
- As rotas de cadastro continuam disponíveis conforme as permissões existentes.
- Nenhuma API ou dado do Xano é alterado.
