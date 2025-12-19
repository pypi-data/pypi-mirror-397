---
id: image-polygon
title: Polygon Conversion
sidebar_position: 3
---

# Polygon Conversion

Guide for bidirectional V1/V2 conversion of polygon annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "poly_1",
    "tool": "polygon",
    "isLocked": False,
    "isVisible": True,
    "classification": {
        "class": "road"
    },
    "label": ["road"]
}

# annotationsData
{
    "id": "poly_1",
    "coordinate": [
        {"x": 100, "y": 200, "id": "pt1"},
        {"x": 150, "y": 250, "id": "pt2"},
        {"x": 200, "y": 200, "id": "pt3"}
    ]
}
```

### V2 Structure

```python
{
    "id": "poly_1",
    "classification": "road",
    "attrs": [],
    "data": [[100, 200], [150, 250], [200, 200]]  # [[x, y], ...]
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `coordinate[{x, y, id}]` | `data[[x, y]]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

**Note:** The `id` field in each V1 point is removed during V2 conversion. This information is preserved in `annotation_meta`.

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data[[x, y]]` | `coordinate[{x, y, id}]` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

**Note:** When converting from V2 to V1, unique `id`s are auto-generated for each point.

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 polygon data
v1_polygon = {
    "annotations": {
        "image_1": [
            {
                "id": "AUjPgaMzQa",
                "tool": "polygon",
                "classification": {"class": "road"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "AUjPgaMzQa",
                "coordinate": [
                    {"x": 100, "y": 200, "id": "pt1"},
                    {"x": 150, "y": 250, "id": "pt2"},
                    {"x": 200, "y": 200, "id": "pt3"}
                ]
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_polygon)
annotation_data = result["annotation_data"]

# Check V2 result
polygon = annotation_data["images"][0]["polygon"][0]
print(polygon["data"])  # [[100, 200], [150, 250], [200, 200]]
print(polygon["classification"])  # "road"
```

### Point ID Generation

Unique IDs are auto-generated for each point when converting V2 to V1:

```python
# V2 polygon data (no point IDs)
v2_polygon = {
    "annotation_data": {
        "images": [
            {
                "polygon": [
                    {
                        "id": "new_poly",
                        "classification": "road",
                        "attrs": [],
                        "data": [[0, 0], [100, 0], [50, 100]]
                    }
                ]
            }
        ]
    }
}

# Convert to V1
v1_result = convert_v2_to_v1(v2_polygon)
coord = v1_result["annotationsData"]["image_1"][0]["coordinate"]

# Each point has a unique ID
for point in coord:
    print(f"x={point['x']}, y={point['y']}, id={point['id']}")

# Verify all IDs are unique
ids = [p["id"] for p in coord]
assert len(ids) == len(set(ids))  # No duplicates
```

### Roundtrip Verification

```python
def verify_polygon_roundtrip(v1_original):
    """Verify polygon roundtrip conversion"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare coordinates
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    # Point count matches
    assert len(orig_coord) == len(rest_coord)

    # All x, y coordinates match
    for orig_pt, rest_pt in zip(orig_coord, rest_coord):
        assert orig_pt["x"] == rest_pt["x"]
        assert orig_pt["y"] == rest_pt["y"]

    print("Polygon roundtrip verification successful")

verify_polygon_roundtrip(v1_polygon)
```

## Important Notes

1. **Point Order**: Point order is always preserved during conversion.
2. **Point IDs**: V2 doesn't store point IDs, so new IDs are generated when converting to V1 without `annotation_meta`.
3. **Minimum Points**: Polygons require at least 3 points.
