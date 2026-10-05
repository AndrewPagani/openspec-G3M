// Esquema mínimo do MVP real da concessionária.
// Valores monetários usam decimal e datas usam timestamp no Xano.
// Regras de transição, estoque e validação de item devem ficar nas APIs.

table perfil {
  schema {
    int id
    text Cargo filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Cargo", op: "asc"}]}
  ]
}

---

table user {
  auth = true
  schema {
    int id
    text UNome filters=trim
    email Email filters=trim|lower
    int perfil_id { table = "perfil" }
    password Senha {
      sensitive = true
    }
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Email", op: "asc"}]}
    {type: "btree", field: [{name: "perfil_id", op: "asc"}]}
  ]
}

---

table cliente {
  schema {
    int id
    text CNome filters=trim
    text CPF filters=trim
    text Telefone filters=trim
    email Email filters=trim|lower
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "CPF", op: "asc"}]}
    {type: "btree|unique", field: [{name: "Email", op: "asc"}]}
  ]
}

---

table status_veiculo {
  schema {
    int id
    text Descricao filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Descricao", op: "asc"}]}
  ]
}

---

table veiculo {
  schema {
    int id
    text Marca filters=trim
    text Modelo filters=trim
    text Cor filters=trim
    int Ano
    text Placa? filters=trim|upper
    text Chassi? filters=trim|upper
    decimal Quilometragem?=0 filters=min:0
    decimal Preco filters=min:0
    text Imagem_url? filters=trim
    int status_id { table = "status_veiculo" }
    timestamp created_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Placa", op: "asc"}]}
    {type: "btree|unique", field: [{name: "Chassi", op: "asc"}]}
    {type: "btree", field: [{name: "Marca", op: "asc"}, {name: "Modelo", op: "asc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]
}

---

table veiculo_area {
  schema {
    int id
    text Secao filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Secao", op: "asc"}]}
  ]
}

---

table peca {
  schema {
    int id
    text PCNome filters=trim
    decimal PCvalor filters=min:0
    int qtd_disp?=0 filters=min:0
    int area_id? { table = "veiculo_area" }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "PCNome", op: "asc"}]}
    {type: "btree", field: [{name: "area_id", op: "asc"}]}
  ]
}

---

table forma_pagamento {
  schema {
    int id
    text Metodo filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Metodo", op: "asc"}]}
  ]
}

---

table status_venda {
  schema {
    int id
    text Descricao_venda filters=trim
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "Descricao_venda", op: "asc"}]}
  ]
}

---

table venda {
  schema {
    int id
    int cliente_id { table = "cliente" }
    int vendedor_id { table = "user" }
    int forma_pagamento_id { table = "forma_pagamento" }
    int status_id { table = "status_venda" }
    decimal Valor_bruto filters=min:0
    decimal Desconto?=0 filters=min:0
    decimal Valor_final filters=min:0
    timestamp data_venda?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "data_venda", op: "desc"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
    {type: "btree", field: [{name: "vendedor_id", op: "asc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]
}

---

table venda_item {
  schema {
    int id
    int venda_id { table = "venda" }
    int veiculo_id? { table = "veiculo" }
    int peca_id? { table = "peca" }
    int qtd?=1 filters=min:1
    decimal preco_unit filters=min:0
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "venda_id", op: "asc"}]}
    {type: "btree", field: [{name: "veiculo_id", op: "asc"}]}
    {type: "btree", field: [{name: "peca_id", op: "asc"}]}
  ]
}
