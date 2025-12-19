---
id: pcd-3d-segmentation
title: 3D Segmentation Conversion
sidebar_position: 9
---

# 3D Segmentation Conversion

A guide for bidirectional V1/V2 conversion of 3D segmentation annotations for PCD (Point Cloud Data).

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "seg3d_1",
    "tool": "3d_segmentation",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "ground",
        "material": "concrete"
    },
    "label": ["ground"]
}

# annotationsData
{
    "id": "seg3d_1",
    "points": [0, 1, 5, 10, 15, 20, 25, 30, 35]
}
```

### V2 Structure

```python
{
    "id": "seg3d_1",
    "classification": "ground",
    "attrs": [
        {"name": "material", "value": "concrete"}
    ],
    "data": {
        "points": [0, 1, 5, 10, 15, 20, 25, 30, 35]
    }
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `points` | `data.points` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data.points` | `points` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 3D segmentation data
v1_data = {
    "annotations": {
        "pcd_1": [
            {
                "id": "3DSeg12345",
                "tool": "3d_segmentation",
                "classification": {"class": "ground", "material": "concrete"}
            }
        ]
    },
    "annotationsData": {
        "pcd_1": [
            {
                "id": "3DSeg12345",
                "points": [0, 1, 5, 10, 15, 20, 25, 30, 35]
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
seg3d = annotation_data["pcds"][0]["3d_segmentation"][0]
print(seg3d["data"]["points"])  # [0, 1, 5, 10, 15, 20, 25, 30, 35]
print(seg3d["classification"])  # "ground"
```

### Large Point Cloud Processing

```python
import numpy as np

# Extract segmentation indices from point cloud
point_cloud = np.random.rand(100000, 3)  # 100,000 points
ground_mask = point_cloud[:, 2] < 0.1  # Select low height points
ground_indices = np.where(ground_mask)[0].tolist()

v1_large = {
    "annotations": {
        "pcd_1": [
            {"id": "GroundSeg", "tool": "3d_segmentation", "classification": {"class": "ground"}}
        ]
    },
    "annotationsData": {
        "pcd_1": [
            {"id": "GroundSeg", "points": ground_indices}
        ]
    }
}

# Convert and verify
result = convert_v1_to_v2(v1_large)
restored = convert_v2_to_v1(result)

original_count = len(v1_large["annotationsData"]["pcd_1"][0]["points"])
restored_count = len(restored["annotationsData"]["pcd_1"][0]["points"])
assert original_count == restored_count
```

### Roundtrip Verification

```python
def verify_3d_seg_roundtrip(v1_original):
    """Verify 3D segmentation roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare points
    orig_points = v1_original["annotationsData"]["pcd_1"][0]["points"]
    rest_points = v1_restored["annotationsData"]["pcd_1"][0]["points"]

    assert orig_points == rest_points

    print("3D segmentation roundtrip verification successful")

verify_3d_seg_roundtrip(v1_data)
```

## Image vs 3D Segmentation

| Property | Image | 3D |
|----------|-------|-----|
| V1 data field | `pixel_indices` | `points` |
| V2 data type | `list[int]` | `{points: list[int]}` |
| Media ID | `image_N` | `pcd_N` |
| Index meaning | Pixel index | Point index |
