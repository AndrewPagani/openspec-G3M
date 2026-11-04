# Design

## Modelo

`veiculo_detalhe` possui relação 1:1 com `veiculo` por `veiculo_id` único.
Campos documentais e técnicos são opcionais para manter compatibilidade com
veículos já cadastrados. O modelo contém apenas RENAVAM, localização de
registro, ano de fabricação, motorização, combustível, câmbio, quilometragem,
portas, lugares e timestamps.

## Interface

A rota `/veiculos/{id}` usa um hero com marca/modelo, imagem e status, seguido
por cards de Identificação completa e Especificações técnicas. Campos ausentes
são exibidos como “Não informado”.

## API

`GET /api:cadastros/veiculos/{id}` preserva os campos base em `veiculo` e
adiciona `detalhes`, contendo o registro relacionado ou objeto vazio quando
não houver detalhes.
