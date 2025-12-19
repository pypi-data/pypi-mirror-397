---
id: image-polyline
title: Polyline Conversion
sidebar_position: 4
---

# Polyline Conversion

A guide for bidirectional V1/V2 conversion of polyline annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "polyline_1",
    "tool": "polyline",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "road_line",
        "type": "dashed"
    },
    "label": ["road_line"]
}

# annotationsData
{
    "id": "polyline_1",
    "coordinate": [
        {"x": 100, "y": 200, "id": "pt_1"},
        {"x": 150, "y": 250, "id": "pt_2"},
        {"x": 200, "y": 200, "id": "pt_3"}
    ]
}
```

### V2 Structure

```python
{
    "id": "polyline_1",
    "classification": "road_line",
    "attrs": [
        {"name": "type", "value": "dashed"}
    ],
    "data": [[100, 200], [150, 250], [200, 200]]
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `coordinate[{x, y, id}]` | `data[[x, y], ...]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data[[x, y], ...]` | `coordinate[{x, y, id}]` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

:::note
During V2→V1 conversion, point IDs are automatically generated as `pt_0`, `pt_1`, ...
:::

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 polyline data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "Line123abc",
                "tool": "polyline",
                "classification": {"class": "road_line", "type": "dashed"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "Line123abc",
                "coordinate": [
                    {"x": 100, "y": 200, "id": "pt_1"},
                    {"x": 150, "y": 250, "id": "pt_2"},
                    {"x": 200, "y": 200, "id": "pt_3"}
                ]
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
polyline = annotation_data["images"][0]["polyline"][0]
print(polyline["data"])  # [[100, 200], [150, 250], [200, 200]]
print(polyline["classification"])  # "road_line"
print(polyline["attrs"])  # [{"name": "type", "value": "dashed"}]
```

### Roundtrip Verification

```python
def verify_polyline_roundtrip(v1_original):
    """Verify polyline roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare coordinates
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    assert len(orig_coord) == len(rest_coord)
    for i, (orig, rest) in enumerate(zip(orig_coord, rest_coord)):
        assert orig["x"] == rest["x"]
        assert orig["y"] == rest["y"]

    print("Polyline roundtrip verification successful")

verify_polyline_roundtrip(v1_data)
```

## Difference from Polygon

| Property | Polyline | Polygon |
|----------|----------|---------|
| Shape closure | Open shape | Closed shape |
| Minimum points | 2 | 3 |
| Purpose | Lines, paths | Areas |
