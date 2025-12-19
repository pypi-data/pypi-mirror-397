---
id: text-named-entity
title: Named Entity Recognition Conversion
sidebar_position: 10
---

# Named Entity Recognition Conversion

A guide for bidirectional V1/V2 conversion of Named Entity Recognition (NER) annotations for text.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "ner_1",
    "tool": "named_entity",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "PERSON",
        "confidence": 0.95
    },
    "label": ["PERSON"]
}

# annotationsData
{
    "id": "ner_1",
    "ranges": [{"start": 0, "end": 5}],
    "content": "John"
}
```

### V2 Structure

```python
{
    "id": "ner_1",
    "classification": "PERSON",
    "attrs": [
        {"name": "confidence", "value": 0.95}
    ],
    "data": {
        "ranges": [{"start": 0, "end": 5}],
        "content": "John"
    }
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `ranges` | `data.ranges` |
| `content` | `data.content` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data.ranges` | `ranges` |
| `data.content` | `content` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 NER data
v1_data = {
    "annotations": {
        "text_1": [
            {
                "id": "NerAbc1234",
                "tool": "named_entity",
                "classification": {"class": "PERSON", "confidence": 0.95}
            }
        ]
    },
    "annotationsData": {
        "text_1": [
            {
                "id": "NerAbc1234",
                "ranges": [{"start": 0, "end": 4}],
                "content": "John"
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
ner = annotation_data["texts"][0]["named_entity"][0]
print(ner["data"]["ranges"])  # [{"start": 0, "end": 4}]
print(ner["data"]["content"])  # "John"
print(ner["classification"])  # "PERSON"
```

### Multiple Entity Processing

```python
# Text with multiple named entities
# "John met Mary at New York."
v1_multi = {
    "annotations": {
        "text_1": [
            {"id": "ner_john", "tool": "named_entity", "classification": {"class": "PERSON"}},
            {"id": "ner_mary", "tool": "named_entity", "classification": {"class": "PERSON"}},
            {"id": "ner_nyc", "tool": "named_entity", "classification": {"class": "LOCATION"}}
        ]
    },
    "annotationsData": {
        "text_1": [
            {"id": "ner_john", "ranges": [{"start": 0, "end": 4}], "content": "John"},
            {"id": "ner_mary", "ranges": [{"start": 9, "end": 13}], "content": "Mary"},
            {"id": "ner_nyc", "ranges": [{"start": 17, "end": 25}], "content": "New York"}
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_multi)
entities = result["annotation_data"]["texts"][0]["named_entity"]

for ent in entities:
    print(f"{ent['classification']}: {ent['data']['content']} ({ent['data']['ranges']})")
# PERSON: John ([{"start": 0, "end": 4}])
# PERSON: Mary ([{"start": 9, "end": 13}])
# LOCATION: New York ([{"start": 17, "end": 25}])
```

### Roundtrip Verification

```python
def verify_ner_roundtrip(v1_original):
    """Verify NER roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare data
    orig_data = v1_original["annotationsData"]["text_1"][0]
    rest_data = v1_restored["annotationsData"]["text_1"][0]

    assert orig_data["ranges"] == rest_data["ranges"]
    assert orig_data["content"] == rest_data["content"]

    print("NER roundtrip verification successful")

verify_ner_roundtrip(v1_data)
```

## Entity Types

Commonly used entity types:

| Type | Description | Example |
|------|-------------|---------|
| PERSON | Person | John, Mary |
| ORGANIZATION | Organization | Google, Samsung |
| LOCATION | Location | Seoul, New York |
| DATE | Date | January 2025 |
| TIME | Time | 3:00 PM |
| MONEY | Currency | $100, 10,000 won |
