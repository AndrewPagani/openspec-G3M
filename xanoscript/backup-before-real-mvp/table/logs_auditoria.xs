// Auditoria de alterações críticas.
table logs_auditoria {
  auth = false

  schema {
    int id
    text entity_type filters=trim|lower
    int entity_id
    text action filters=trim|lower
    int user_id? {
      table = "usuarios"
    }
  
    json before_data?
    json after_data?
    json metadata?
    text ip_address?
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree"
      field: [
        {name: "entity_type", op: "asc"}
        {name: "entity_id", op: "asc"}
      ]
    }
    {
      type : "btree"
      field: [
        {name: "user_id", op: "asc"}
        {name: "created_at", op: "desc"}
      ]
    }
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "BNgcr3iWatNMcCkCPuQOpm44gxQ"
}