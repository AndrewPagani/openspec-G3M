# AutoGestão — Python + Reflex

Aplicação do MVP de gerenciamento de concessionária. A interface usa Reflex e
o Xano é a fonte de autenticação, autorização e dados; não há dados de negócio
embutidos no frontend.

## Executar localmente

Requer Python 3.11+:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
reflex run
```

Para conectar ao backend, configure antes de executar:

```powershell
$env:XANO_BASE_URL = "https://XXXX-XXXX-XXXX.XX.xano.io"
# Os grupos publicados são resolvidos pelo cliente HTTP do app. Só defina
# overrides se os IDs/canônicos dos grupos forem alterados no Xano:
# $env:XANO_API_GROUP_AUTH = "autenticacao"
# $env:XANO_API_GROUP_CADASTROS = "cadastros"
# $env:XANO_API_GROUP_VENDAS = "Q9GErvvS"
# $env:XANO_API_GROUP_GERENCIAMENTO = "gerenciamento"
$env:XANO_TIMEOUT = "12"
reflex run
```

Esse é o domínio do workspace Xano 147643 e também o padrão usado pelo app.
Use `XANO_BASE_URL` apenas para substituir o host, sempre com a URL raiz
(sem `/api:<grupo>`). O app escolhe o grupo para cada rota e envia o token de
sessão no cabeçalho `Authorization`. O fluxo atual não usa ASAAS nem outro
processador: `/vendas/nova` cria a reserva e o cronograma de 1–24 parcelas no
Xano; gerente/administrador registra a baixa integral informando a forma
realmente recebida. Essa baixa é somente um registro administrativo e não
processa nem verifica transferência financeira. IDs de cliente, forma de
pagamento e itens devem corresponder a registros existentes no Xano.

O host padrão conecta este app ao workspace Xano `147643`. Para outro ambiente,
substitua `XANO_BASE_URL`; se a API estiver indisponível, a aplicação mostra
mensagens claras de erro e não inventa registros. A mudança ativa que define
o contrato de parcelas e baixa manual está em
`docs/openspec/changes/registro-manual-de-parcelas-no-xano/`. Os antigos planos
de APIs/pagamento ASAAS são documentos históricos e não devem ser enviados ao
Xano como contrato atual. A verificação de prontidão está em
`docs/xano-api-readiness-check.md`.

No Windows, o frontend e o backend devem ser iniciados em terminais separados
para evitar a queda do WebSocket do Reflex:

```powershell
# Terminal 1 — backend
reflex run --env dev --backend-only --backend-port 8001

# Terminal 2 — frontend
reflex run --env dev --frontend-only --frontend-port 3000
```

Abra `http://localhost:3000`. O frontend conecta ao backend em
`http://127.0.0.1:8001`, conforme `rxconfig.py`.

## Validação

```powershell
reflex export --frontend-only --no-zip
```

O MVP inclui login, shell autenticado, guards por perfil e rotas de
gerenciamento, clientes, veículos, peças, vendas, usuários, auditoria e
configurações. Leads, oficina e multiunidade estão fora do escopo.
