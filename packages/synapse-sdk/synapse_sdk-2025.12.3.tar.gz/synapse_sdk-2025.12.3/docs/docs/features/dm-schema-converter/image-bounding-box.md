---
id: image-bounding-box
title: Bounding Box Conversion
sidebar_position: 2
---

# Bounding Box Conversion

Guide for bidirectional V1/V2 conversion of bounding box annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "ann_1",
    "tool": "bounding_box",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "person",
        "color": "red"  # additional attribute
    },
    "label": ["person"]
}

# annotationsData
{
    "id": "ann_1",
    "coordinate": {
        "x": 100,
        "y": 200,
        "width": 150,
        "height": 100,
        "rotation": 0.5236  # optional
    }
}
```

### V2 Structure

```python
{
    "id": "ann_1",
    "classification": "person",
    "attrs": [
        {"name": "color", "value": "red"},
        {"name": "rotation", "value": 0.5236}
    ],
    "data": [100, 200, 150, 100]  # [x, y, width, height]
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `coordinate.{x, y, width, height}` | `data[0, 1, 2, 3]` |
| `coordinate.rotation` | `attrs[{name: "rotation", value}]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data[0, 1, 2, 3]` | `coordinate.{x, y, width, height}` |
| `attrs.rotation` | `coordinate.rotation` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 bounding box data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "Cd1qfFQFI4",
                "tool": "bounding_box",
                "isLocked": False,
                "isVisible": True,
                "classification": {"class": "person", "color": "red"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "Cd1qfFQFI4",
                "coordinate": {"x": 100, "y": 200, "width": 150, "height": 100}
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
bbox = annotation_data["images"][0]["bounding_box"][0]
print(bbox["data"])  # [100, 200, 150, 100]
print(bbox["classification"])  # "person"
print(bbox["attrs"])  # [{"name": "color", "value": "red"}]
```

### Rotation Handling

```python
# Bounding box with rotation
v1_rotated = {
    "annotations": {
        "image_1": [
            {
                "id": "Rot12345ab",
                "tool": "bounding_box",
                "classification": {"class": "text"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "Rot12345ab",
                "coordinate": {
                    "x": 50, "y": 100,
                    "width": 200, "height": 50,
                    "rotation": 0.5236  # ~30 degrees (radians)
                }
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_rotated)
bbox = result["annotation_data"]["images"][0]["bounding_box"][0]

# rotation is preserved in attrs
print(bbox["data"])  # [50, 100, 200, 50]
rotation_attr = [a for a in bbox["attrs"] if a["name"] == "rotation"][0]
print(rotation_attr["value"])  # 0.5236

# Restore to V1
v1_restored = convert_v2_to_v1(result)
restored_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]
print(restored_coord["rotation"])  # 0.5236 (preserved)
```

## Meta Information Restoration

Using `annotation_meta` restores all V1 meta fields:

```python
# Complete conversion (with meta information)
v1_full = convert_v2_to_v1(result)

# Check meta fields
ann = v1_full["annotations"]["image_1"][0]
print(ann["isLocked"])  # False (original value)
print(ann["isVisible"])  # True (original value)
print(ann["isValid"])  # True (original value)

# Conversion with annotation_data only uses defaults
v1_basic = convert_v2_to_v1({"annotation_data": annotation_data})
ann_basic = v1_basic["annotations"]["image_1"][0]
print(ann_basic["isLocked"])  # False (default)
print(ann_basic["isValid"])  # False (default)
```
