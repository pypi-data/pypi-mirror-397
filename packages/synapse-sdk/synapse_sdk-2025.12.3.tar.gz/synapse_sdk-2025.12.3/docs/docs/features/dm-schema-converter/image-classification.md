---
id: image-classification
title: Classification Conversion
sidebar_position: 11
---

# Classification Conversion

A guide for bidirectional V1/V2 conversion of image classification annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "cls_1",
    "tool": "classification",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "cat",
        "confidence": 0.98,
        "breed": "persian"
    },
    "label": ["cat"]
}

# annotationsData (id only)
{
    "id": "cls_1"
}
```

### V2 Structure

```python
{
    "id": "cls_1",
    "classification": "cat",
    "attrs": [
        {"name": "confidence", "value": 0.98},
        {"name": "breed", "value": "persian"}
    ],
    "data": {}  # empty object
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| (none) | `data: {}` (empty object) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data` | (ignored) |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

:::note
The classification tool has no coordinate data, so only `id` is stored in `annotationsData`.
In V2, `data` is an empty object `{}`.
:::

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 classification data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "ClsAbc1234",
                "tool": "classification",
                "classification": {"class": "cat", "confidence": 0.98, "breed": "persian"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "ClsAbc1234"
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
cls = annotation_data["images"][0]["classification"][0]
print(cls["classification"])  # "cat"
print(cls["data"])  # {}
print(cls["attrs"])  # [{"name": "confidence", "value": 0.98}, {"name": "breed", "value": "persian"}]
```

### Multi-label Processing

```python
# Image with multiple classification tags
v1_multi = {
    "annotations": {
        "image_1": [
            {"id": "cls_animal", "tool": "classification", "classification": {"class": "animal"}},
            {"id": "cls_indoor", "tool": "classification", "classification": {"class": "indoor"}},
            {"id": "cls_pet", "tool": "classification", "classification": {"class": "pet"}}
        ]
    },
    "annotationsData": {
        "image_1": [
            {"id": "cls_animal"},
            {"id": "cls_indoor"},
            {"id": "cls_pet"}
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_multi)
classifications = result["annotation_data"]["images"][0]["classification"]

for cls in classifications:
    print(cls["classification"])
# animal
# indoor
# pet
```

### Roundtrip Verification

```python
def verify_classification_roundtrip(v1_original):
    """Verify classification roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare classifications
    orig_cls = v1_original["annotations"]["image_1"][0]["classification"]
    rest_cls = v1_restored["annotations"]["image_1"][0]["classification"]

    assert orig_cls["class"] == rest_cls["class"]

    print("Classification roundtrip verification successful")

verify_classification_roundtrip(v1_data)
```

## Differences from Other Tools

| Property | Classification | Bounding Box |
|----------|----------------|--------------|
| Coordinate data | None | Present |
| V1 annotationsData | id only | coordinate |
| V2 data | `{}` | `[x, y, w, h]` |
| Purpose | Whole image tagging | Region specification |
