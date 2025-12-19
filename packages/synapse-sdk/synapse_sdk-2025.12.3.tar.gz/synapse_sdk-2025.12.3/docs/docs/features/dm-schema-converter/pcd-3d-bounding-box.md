---
id: pcd-3d-bounding-box
title: 3D Bounding Box Conversion
sidebar_position: 6
---

# 3D Bounding Box Conversion

A guide for bidirectional V1/V2 conversion of 3D bounding box annotations for PCD (Point Cloud Data).

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "bbox3d_1",
    "tool": "3d_bounding_box",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "car",
        "confidence": 0.95
    },
    "label": ["car"]
}

# annotationsData
{
    "id": "bbox3d_1",
    "psr": {
        "position": {"x": 10.5, "y": 20.3, "z": 1.2},
        "scale": {"x": 4.5, "y": 2.0, "z": 1.5},
        "rotation": {"x": 0, "y": 0, "z": 0.785}  # radians
    }
}
```

### V2 Structure

```python
{
    "id": "bbox3d_1",
    "classification": "car",
    "attrs": [
        {"name": "confidence", "value": 0.95}
    ],
    "data": {
        "position": {"x": 10.5, "y": 20.3, "z": 1.2},
        "scale": {"x": 4.5, "y": 2.0, "z": 1.5},
        "rotation": {"x": 0, "y": 0, "z": 0.785}
    }
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `psr.position` | `data.position` |
| `psr.scale` | `data.scale` |
| `psr.rotation` | `data.rotation` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data.position` | `psr.position` |
| `data.scale` | `psr.scale` |
| `data.rotation` | `psr.rotation` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 3D bounding box data
v1_data = {
    "annotations": {
        "pcd_1": [
            {
                "id": "3DBbox123",
                "tool": "3d_bounding_box",
                "classification": {"class": "car", "confidence": 0.95}
            }
        ]
    },
    "annotationsData": {
        "pcd_1": [
            {
                "id": "3DBbox123",
                "psr": {
                    "position": {"x": 10.5, "y": 20.3, "z": 1.2},
                    "scale": {"x": 4.5, "y": 2.0, "z": 1.5},
                    "rotation": {"x": 0, "y": 0, "z": 0.785}
                }
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
bbox3d = annotation_data["pcds"][0]["3d_bounding_box"][0]
print(bbox3d["data"]["position"])  # {"x": 10.5, "y": 20.3, "z": 1.2}
print(bbox3d["data"]["scale"])  # {"x": 4.5, "y": 2.0, "z": 1.5}
print(bbox3d["classification"])  # "car"
```

### Roundtrip Verification

```python
def verify_3d_bbox_roundtrip(v1_original):
    """Verify 3D bounding box roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare PSR
    orig_psr = v1_original["annotationsData"]["pcd_1"][0]["psr"]
    rest_psr = v1_restored["annotationsData"]["pcd_1"][0]["psr"]

    for key in ["position", "scale", "rotation"]:
        for axis in ["x", "y", "z"]:
            assert orig_psr[key][axis] == rest_psr[key][axis]

    print("3D bounding box roundtrip verification successful")

verify_3d_bbox_roundtrip(v1_data)
```

## PSR Coordinate System

3D bounding boxes use the PSR (Position, Scale, Rotation) format:

| Field | Description | Unit |
|-------|-------------|------|
| position.x | X position | meters |
| position.y | Y position | meters |
| position.z | Z position | meters |
| scale.x | X size (length) | meters |
| scale.y | Y size (width) | meters |
| scale.z | Z size (height) | meters |
| rotation.x | X-axis rotation | radians |
| rotation.y | Y-axis rotation | radians |
| rotation.z | Z-axis rotation (yaw) | radians |
