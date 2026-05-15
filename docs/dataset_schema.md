# Schema do `dataset.json`

O dataset segue uma estrutura aninhada com 3 niveis (N1/N2/N3). Cada item de `datas`
contem o `text` original e a decomposicao RASE de referencia.

## Estrutura

```json
{
  "counts": 79,
  "datas": [
    {
      "text": "Texto da norma...",
      "texts_n1": [
        {
          "text_n1": "Sentenca segmentada (N1).",
          "operators_n2": {
            "aplicability": {
              "text_n2": "Trecho do operador (string vazia se ausente)",
              "properties_n3": {
                "type": "aplicabilidade",
                "object": "edificacao",
                "property": "uso",
                "comparation": "=",
                "target": "residencial",
                "unit": ""
              }
            },
            "selection":    { "text_n2": "...", "properties_n3": { ... } },
            "exception":    { "text_n2": "...", "properties_n3": { ... } },
            "requeriments": { "text_n2": "...", "properties_n3": { ... } }
          }
        }
      ]
    }
  ]
}
```

## JSON Schema (formal)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MestradoRaseDataset",
  "type": "object",
  "required": ["datas"],
  "properties": {
    "counts": { "type": "integer", "minimum": 0 },
    "time":   { "type": "number", "minimum": 0 },
    "meta":   { "type": "object" },
    "datas":  {
      "type": "array",
      "items": { "$ref": "#/$defs/textItem" }
    }
  },
  "$defs": {
    "textItem": {
      "type": "object",
      "required": ["text", "texts_n1"],
      "properties": {
        "text":    { "type": "string" },
        "texts_n1":{ "type": "array", "items": { "$ref": "#/$defs/n1Item" } }
      }
    },
    "n1Item": {
      "type": "object",
      "required": ["text_n1", "operators_n2"],
      "properties": {
        "text_n1":     { "type": "string" },
        "operators_n2":{
          "type": "object",
          "properties": {
            "aplicability": { "$ref": "#/$defs/n2Op" },
            "selection":    { "$ref": "#/$defs/n2Op" },
            "exception":    { "$ref": "#/$defs/n2Op" },
            "requeriments": { "$ref": "#/$defs/n2Op" }
          }
        }
      }
    },
    "n2Op": {
      "type": "object",
      "required": ["text_n2", "properties_n3"],
      "properties": {
        "text_n2":      { "type": "string" },
        "properties_n3":{ "$ref": "#/$defs/n3Props" }
      }
    },
    "n3Props": {
      "type": "object",
      "required": ["type", "object", "property", "comparation", "target", "unit"],
      "properties": {
        "type":        { "type": "string" },
        "object":      { "type": "string" },
        "property":    { "type": "string" },
        "comparation": { "type": "string" },
        "target":      { "type": "string" },
        "unit":        { "type": "string" }
      }
    }
  }
}
```

## Notas

- `operators_n2` contem ate 4 chaves: `aplicability`, `selection`, `exception`,
  `requeriments` (sempre nessa grafia em ingles no codigo; apenas o `type` dentro
  de `properties_n3` usa o portugues: `aplicabilidade`, `selecao`, `excecao`,
  `requisito`).
- Quando o operador nao se aplica, `text_n2` e string vazia (`""`) e
  `properties_n3` mantem a estrutura mas com strings vazias.
- Os arquivos em `predicts/` seguem o mesmo formato, com um bloco extra `meta`
  contendo `model_id`, `temperature`, `seed`, `prompt_sha256`, etc.
