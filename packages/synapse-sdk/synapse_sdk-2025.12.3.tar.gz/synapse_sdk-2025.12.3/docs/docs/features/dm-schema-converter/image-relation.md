---
id: image-relation
title: Relation Conversion
sidebar_position: 12
---

# Relation Conversion

A guide for converting annotation relationships (Relation).

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "rel_1",
    "tool": "relation",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "belongs_to",
        "confidence": 0.9
    },
    "label": ["belongs_to"]
}

# annotationsData
{
    "id": "rel_1",
    "annotationId": "BBoxAbc001",      # from (source annotation)
    "targetAnnotationId": "BBoxAbc002"  # to (target annotation)
}
```

### V2 Structure

```python
{
    "id": "rel_1",
    "classification": "belongs_to",
    "attrs": [
        {"name": "confidence", "value": 0.9}
    ],
    "data": ["BBoxAbc001", "BBoxAbc002"]  # [from_id, to_id]
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `annotationId` | `data[0]` (from_id) |
| `targetAnnotationId` | `data[1]` (to_id) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data[0]` | `annotationId` |
| `data[1]` | `targetAnnotationId` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 relation data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "RelAbc123",
                "tool": "relation",
                "classification": {"class": "belongs_to", "confidence": 0.9}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "RelAbc123",
                "annotationId": "BBoxAbc001",
                "targetAnnotationId": "BBoxAbc002"
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
rel = annotation_data["images"][0]["relation"][0]
print(rel["data"])  # ["BBoxAbc001", "BBoxAbc002"]
print(rel["classification"])  # "belongs_to"
```

### Complex Relationship Graph

```python
# Multiple object relationships
# person -> (holding) -> bag
# person -> (wearing) -> hat
# bag -> (near) -> chair

v1_graph = {
    "annotations": {
        "image_1": [
            {"id": "rel_holding", "tool": "relation", "classification": {"class": "holding"}},
            {"id": "rel_wearing", "tool": "relation", "classification": {"class": "wearing"}},
            {"id": "rel_near", "tool": "relation", "classification": {"class": "near"}}
        ]
    },
    "annotationsData": {
        "image_1": [
            {"id": "rel_holding", "annotationId": "person_1", "targetAnnotationId": "bag_1"},
            {"id": "rel_wearing", "annotationId": "person_1", "targetAnnotationId": "hat_1"},
            {"id": "rel_near", "annotationId": "bag_1", "targetAnnotationId": "chair_1"}
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_graph)
relations = result["annotation_data"]["images"][0]["relation"]

for rel in relations:
    from_id, to_id = rel["data"]
    print(f"{from_id} --{rel['classification']}--> {to_id}")
# person_1 --holding--> bag_1
# person_1 --wearing--> hat_1
# bag_1 --near--> chair_1
```

### Roundtrip Verification

```python
def verify_relation_roundtrip(v1_original):
    """Verify relation roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare relations
    orig_data = v1_original["annotationsData"]["image_1"][0]
    rest_data = v1_restored["annotationsData"]["image_1"][0]

    assert orig_data["annotationId"] == rest_data["annotationId"]
    assert orig_data["targetAnnotationId"] == rest_data["targetAnnotationId"]

    print("Relation roundtrip verification successful")

verify_relation_roundtrip(v1_data)
```

## Relation Types

Common relation types:

| Type | Description | Example |
|------|-------------|---------|
| belongs_to | Membership | person → group |
| part_of | Part relationship | wheel → car |
| near | Proximity | chair → table |
| holding | Holding | person → bag |
| wearing | Wearing | person → hat |
| parent_of | Parent-child | parent → child |
