# Proposta: Listagem visual de veículos

## Why

A tela de veículos deve facilitar a identificação visual dos registros e não
deve omitir veículos além da primeira página retornada pelo Xano. A resposta
atual da API também não inclui a URL de imagem, apesar de o formulário Reflex
já aceitar `Imagem_url`.

## What Changes

- Carregar todas as páginas da listagem de veículos, usando páginas de até 100
  registros e preservando a paginação existente no endpoint.
- Apresentar cards com imagem retangular em destaque, marca/modelo, ano,
  quilometragem, preço e acesso aos detalhes; exibir um substituto quando não
  houver imagem.
- Apresentar até três cards por linha em telas amplas, reduzindo o número de
  colunas em telas menores.
- Reutilizar o campo opcional `imagem_url` já existente no schema Xano e
  expor `Imagem_url` nos endpoints de cadastro, consulta, edição e listagem
  de veículos.

## Fora do escopo

- Publicar alterações no workspace Xano remoto: a publicação requer autorização
  explícita e será tratada como etapa operacional separada.
- Alterar filtros, disponibilidade comercial, fluxo de vendas ou os cartões de
  clientes e peças.
- Tornar a imagem obrigatória para veículos legados.

## Impacto

- Aplicação Reflex: carregamento e normalização em `app/state/resource_state.py`
  e apresentação em `app/pages/resource.py`.
- Contrato local Xano: schema e endpoints de veículos em
  `xanoscript/workspace_current`.
- Testes: validação da normalização dos campos e carregamento de todas as
  páginas.
- Spec: delta em `specs/cadastros-e-listagens/spec.md`.

Parte da implementação já está no workspace local. O dry-run remoto confirmou
que a prévia é não destrutiva. A publicação e a validação autenticada em runtime
permanecem fora desta change e devem ocorrer separadamente após autorização.
