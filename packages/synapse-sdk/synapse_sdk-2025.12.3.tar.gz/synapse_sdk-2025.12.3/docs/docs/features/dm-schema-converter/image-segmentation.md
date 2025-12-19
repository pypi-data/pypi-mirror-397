---
id: image-segmentation
title: Segmentation Conversion (Image)
sidebar_position: 7
---

# Segmentation Conversion (Image)

A guide for bidirectional V1/V2 conversion of image segmentation annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "seg_1",
    "tool": "segmentation",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "road",
        "surface": "asphalt"
    },
    "label": ["road"]
}

# annotationsData
{
    "id": "seg_1",
    "pixel_indices": [100, 101, 102, 200, 201, 202, 300, 301, 302]
}
```

### V2 Structure

```python
{
    "id": "seg_1",
    "classification": "road",
    "attrs": [
        {"name": "surface", "value": "asphalt"}
    ],
    "data": [100, 101, 102, 200, 201, 202, 300, 301, 302]
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `pixel_indices` | `data` (array as-is) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data` | `pixel_indices` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 segmentation data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "SegAbc1234",
                "tool": "segmentation",
                "classification": {"class": "road", "surface": "asphalt"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "SegAbc1234",
                "pixel_indices": [100, 101, 102, 200, 201, 202]
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
seg = annotation_data["images"][0]["segmentation"][0]
print(seg["data"])  # [100, 101, 102, 200, 201, 202]
print(seg["classification"])  # "road"
```

### Large Pixel Indices Processing

```python
# Large segmentation mask
import numpy as np

# Extract pixel indices from image mask
mask = np.zeros((1080, 1920), dtype=np.uint8)
mask[100:200, 300:500] = 1  # Mark region

# Calculate pixel indices (row * width + col)
pixel_indices = np.where(mask.flatten() == 1)[0].tolist()

v1_large = {
    "annotations": {
        "image_1": [
            {"id": "LargeSeg01", "tool": "segmentation", "classification": {"class": "object"}}
        ]
    },
    "annotationsData": {
        "image_1": [
            {"id": "LargeSeg01", "pixel_indices": pixel_indices}
        ]
    }
}

# Convert and verify
result = convert_v1_to_v2(v1_large)
restored = convert_v2_to_v1(result)

original_count = len(v1_large["annotationsData"]["image_1"][0]["pixel_indices"])
restored_count = len(restored["annotationsData"]["image_1"][0]["pixel_indices"])
assert original_count == restored_count
```

### Roundtrip Verification

```python
def verify_segmentation_roundtrip(v1_original):
    """Verify segmentation roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare pixel indices
    orig_pixels = v1_original["annotationsData"]["image_1"][0]["pixel_indices"]
    rest_pixels = v1_restored["annotationsData"]["image_1"][0]["pixel_indices"]

    assert orig_pixels == rest_pixels

    print("Segmentation roundtrip verification successful")

verify_segmentation_roundtrip(v1_data)
```

## Related Documentation

- [Video Segmentation Conversion](./video-segmentation.md) - Video segmentation conversion
- [3D Segmentation Conversion](./pcd-3d-segmentation.md) - PCD segmentation conversion
