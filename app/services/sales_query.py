"""Shared query parameters for the Xano sales listing."""


def sales_query_params(
    *,
    page: int = 1,
    per_page: int = 100,
    busca: str = "",
    cliente_id: str = "",
    vendedor_id: str = "",
    status_id: str = "",
    forma_pagamento_id: str = "",
    data_inicio: str = "",
    data_fim: str = "",
) -> dict[str, str]:
    params = {
        "page": str(page),
        "per_page": str(per_page),
        "busca": busca.strip(),
    }
    # These Xano inputs are optional JSON. Sending "{}" can decode to an
    # object, which is incompatible with scalar comparisons / to_int.
    # Omit absent filters so the endpoint receives its optional null value.
    for key, value in (
        ("cliente_id", cliente_id),
        ("vendedor_id", vendedor_id),
        ("status_id", status_id),
        ("forma_pagamento_id", forma_pagamento_id),
        ("data_inicio", data_inicio),
        ("data_fim", data_fim),
    ):
        normalized = value.strip()
        if normalized:
            params[key] = normalized
    return params
