---
id: image-keypoint
title: Keypoint Conversion
sidebar_position: 5
---

# Keypoint Conversion

A guide for bidirectional V1/V2 conversion of keypoint annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "keypoint_1",
    "tool": "keypoint",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "joint",
        "body_part": "elbow"
    },
    "label": ["joint"]
}

# annotationsData
{
    "id": "keypoint_1",
    "coordinate": {
        "x": 150.5,
        "y": 200.3
    }
}
```

### V2 Structure

```python
{
    "id": "keypoint_1",
    "classification": "joint",
    "attrs": [
        {"name": "body_part", "value": "elbow"}
    ],
    "data": [150.5, 200.3]
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `coordinate.{x, y}` | `data[0, 1]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data[0, 1]` | `coordinate.{x, y}` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 keypoint data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "KpAbc12345",
                "tool": "keypoint",
                "classification": {"class": "joint", "body_part": "elbow"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "KpAbc12345",
                "coordinate": {"x": 150.5, "y": 200.3}
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
kp = annotation_data["images"][0]["keypoint"][0]
print(kp["data"])  # [150.5, 200.3]
print(kp["classification"])  # "joint"
print(kp["attrs"])  # [{"name": "body_part", "value": "elbow"}]
```

### Multiple Keypoints Processing

```python
# Skeleton pose data
v1_skeleton = {
    "annotations": {
        "image_1": [
            {"id": "kp_head", "tool": "keypoint", "classification": {"class": "head"}},
            {"id": "kp_shoulder", "tool": "keypoint", "classification": {"class": "shoulder"}},
            {"id": "kp_elbow", "tool": "keypoint", "classification": {"class": "elbow"}}
        ]
    },
    "annotationsData": {
        "image_1": [
            {"id": "kp_head", "coordinate": {"x": 100, "y": 50}},
            {"id": "kp_shoulder", "coordinate": {"x": 100, "y": 100}},
            {"id": "kp_elbow", "coordinate": {"x": 130, "y": 150}}
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_skeleton)
keypoints = result["annotation_data"]["images"][0]["keypoint"]

for kp in keypoints:
    print(f"{kp['classification']}: {kp['data']}")
# head: [100, 50]
# shoulder: [100, 100]
# elbow: [130, 150]
```

### Roundtrip Verification

```python
def verify_keypoint_roundtrip(v1_original):
    """Verify keypoint roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare coordinates
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    assert orig_coord["x"] == rest_coord["x"]
    assert orig_coord["y"] == rest_coord["y"]

    print("Keypoint roundtrip verification successful")

verify_keypoint_roundtrip(v1_data)
```
