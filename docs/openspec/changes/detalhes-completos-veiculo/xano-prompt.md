# Prompt para o Xano

No workspace Xano `147643`, ajuste a tabela `veiculo_detalhe` para conter
**somente** os campos abaixo. Não apague a tabela `veiculo`, não altere os
veículos existentes e preserve o `veiculo_id` dos registros atuais.

## Estrutura final obrigatória

```text
id: inteiro, chave primária
veiculo_id: inteiro, FK obrigatória para veiculo.id, índice UNIQUE
uf_registro: texto opcional, trim e uppercase
cidade_registro: texto opcional, trim
ano_fabricacao: inteiro opcional, entre 1900 e 2100
motorizacao: texto opcional, trim
combustivel: texto opcional, aceitar Flex, Gasolina, Diesel, Elétrico ou Híbrido
cambio: texto opcional, aceitar Automático, Manual ou CVT
quilometragem: decimal opcional, maior ou igual a 0
numero_portas: inteiro opcional, entre 1 e 20
numero_lugares: inteiro opcional, entre 1 e 100
opcionais: lista JSON opcional de textos
created_at: timestamp
```

Remova da tabela e dos endpoints os campos que não fazem parte da lista:
`numero_motor`, `origem`, `versao`, `ano_modelo`, `cor_externa`,
`cor_interna`, `carroceria` e `updated_at`.

## GET do veículo

Atualize `GET /api:cadastros/veiculos/{id}` para consultar
`veiculo_detalhe.veiculo_id` e retornar:

```json
{
  "veiculo": {},
  "detalhes": {
    "id": 1,
    "veiculo_id": 25,
    "uf_registro": "SP",
    "cidade_registro": "São Paulo",
    "ano_fabricacao": 2023,
    "motorizacao": "2.0 Turbo - 192 cv",
    "combustivel": "Gasolina",
    "cambio": "Automático",
    "quilometragem": 25000,
    "numero_portas": 4,
    "numero_lugares": 5,
    "opcionais": ["Teto Solar", "Couro", "Ar Digital", "Sensor de Ré"],
    "created_at": "2026-11-03T00:00:00Z"
  }
}
```

Preserve os campos atuais de `veiculo`. Se não houver registro relacionado,
retorne `"detalhes": {}` sem erro.

## POST

Mantenha `POST /api:cadastros/veiculos/{id}/detalhes` com autenticação e
permissão somente para Gerente/Administrador. Valide:

- veículo existente;
- `veiculo_id` único;
- anos entre 1900 e 2100;
- quilometragem não negativa;
- portas entre 1 e 20;
- lugares entre 1 e 100;
- combustível dentro dos valores permitidos;
- câmbio dentro dos valores permitidos.
- `opcionais` deve ser uma lista JSON de textos.

Retorne erro de conflito se os detalhes já existirem e devolva o registro
criado completo.

## PATCH

Mantenha `PATCH /api:cadastros/veiculos/{id}/detalhes` com autenticação e
permissão Gerente/Administrador. O PATCH deve ser parcial, aceitar somente os
campos da estrutura final e retornar 404 se os detalhes não existirem.

## Segurança e publicação

Não confiar em validações do frontend. Faça validação no backend, execute
dry-run e testes no draft, compare live/draft e não publique outros objetos.
Não use `--sync`, `--delete`, `--records` ou `--truncate`.
Retorne o JSON final e o resultado dos testes.
