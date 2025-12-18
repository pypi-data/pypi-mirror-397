"""Provide the validation JSONschema."""

import json

schema = json.loads("""
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/jmespath-filters/filter-rule.schema.json",
  "title": "JMESPath Filters - Filter Rule",
  "description": "A rule is either a non-empty JMESPath expression string, or a composite rule using AND/OR/NOT.",
  "$ref": "#/$defs/rule",
  "$defs": {
    "rule": {
      "oneOf": [
        { "$ref": "#/$defs/simpleExpression" },
        { "$ref": "#/$defs/andRule" },
        { "$ref": "#/$defs/orRule" },
        { "$ref": "#/$defs/notRule" }
      ]
    },
    "simpleExpression": {
      "type": "string",
      "minLength": 1,
      "description": "A non-empty JMESPath expression string."
    },
    "andRule": {
      "type": "object",
      "additionalProperties": false,
      "required": ["AND"],
      "properties": {
        "AND": {
          "type": "array",
          "minItems": 2,
          "items": { "$ref": "#/$defs/rule" }
        }
      }
    },
    "orRule": {
      "type": "object",
      "additionalProperties": false,
      "required": ["OR"],
      "properties": {
        "OR": {
          "type": "array",
          "minItems": 2,
          "items": { "$ref": "#/$defs/rule" }
        }
      }
    },
    "notRule": {
      "type": "object",
      "additionalProperties": false,
      "required": ["NOT"],
      "properties": {
        "NOT": {
          "description": "Negates exactly one rule. Accepts either a single rule or a single-item list (tests reject 0 or 2+).",
          "oneOf": [
            { "$ref": "#/$defs/rule" },
            {
              "type": "array",
              "minItems": 1,
              "maxItems": 1,
              "items": { "$ref": "#/$defs/rule" }
            }
          ]
        }
      }
    }
  }
}
""")
