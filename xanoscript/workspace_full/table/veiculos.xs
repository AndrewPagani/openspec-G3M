// Veículos comercializados pela concessionária.
table veiculos {
  schema {
    int id
    text chassi filters=trim|upper
    text placa? filters=trim|upper
    text marca filters=trim
    text modelo filters=trim
    text cor filters=trim
    int ano_fabricacao filters=min:1886
    int modelo_year? filters=min:1886
    int quilometragem filters=min:0
    decimal preco filters=min:0
    int status_id { table = "status_veiculo" }
    timestamp disponivel_em?
    timestamp vendido_em?
    bool ativo?=true
    int created_by? { table = "usuarios" }
    int updated_by? { table = "usuarios" }
    timestamp created_at?=now
    timestamp updated_at?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "chassi", op: "asc"}]}
    {type: "btree|unique", field: [{name: "placa", op: "asc"}]}
    {type: "btree", field: [{name: "marca", op: "asc"}, {name: "modelo", op: "asc"}]}
    {type: "btree", field: [{name: "status_id", op: "asc"}]}
  ]
  guid = "6X-c8ACnvG-XbpLt2VeePMISu1s"
}
