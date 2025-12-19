---
id: dm-schema-converter
title: DM Schema V1/V2 Converter
sidebar_position: 1
---

# DM Schema V1/V2 Converter

A bidirectional converter between DM Schema V1 and V2 formats.

## Overview

The DM Schema Converter transforms annotation data between V1 and V2 formats:

- **V1 → V2**: Convert legacy V1 data to modern V2 structure
- **V2 → V1**: Reverse convert V2 data to V1 format (legacy system compatibility)

## Key Features

### Separated Output Structure

V1→V2 conversion returns two separate parts:

- **`annotation_data`**: V2 common annotation structure (id, classification, attrs, data)
- **`annotation_meta`**: Preserved V1 top-level structure (meta information)

This separation enables:
- Use `annotation_data` alone for V2 common format
- Combine with `annotation_meta` for complete V1 restoration

### Supported Tools

| Tool | V1 → V2 | V2 → V1 | Media Type | Notes |
|------|---------|---------|------------|-------|
| `bounding_box` | ✅ | ✅ | image | rotation preserved |
| `polygon` | ✅ | ✅ | image | point IDs auto-generated |
| `polyline` | ✅ | ✅ | image | point IDs auto-generated |
| `keypoint` | ✅ | ✅ | image | single point coordinate |
| `3d_bounding_box` | ✅ | ✅ | pcd | PSR coordinate system |
| `segmentation` | ✅ | ✅ | image/video | image: pixel_indices, video: section |
| `3d_segmentation` | ✅ | ✅ | pcd | point indices |
| `named_entity` | ✅ | ✅ | text | NER tagging |
| `classification` | ✅ | ✅ | image | no data (empty object) |
| `relation` | ✅ | ✅ | image/text | annotation relationships |
| `prompt` | ✅ | ✅ | prompt | prompt input |
| `answer` | ✅ | ✅ | prompt | answer output |

## Quick Start

### Installation

```bash
pip install synapse-sdk
```

### V1 → V2 Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2

# V1 data
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "ann_1",
                "tool": "bounding_box",
                "classification": {"class": "person"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "ann_1",
                "coordinate": {"x": 100, "y": 200, "width": 150, "height": 100}
            }
        ]
    }
}

# Convert to V2 (separated result)
result = convert_v1_to_v2(v1_data)

annotation_data = result["annotation_data"]  # V2 common structure
annotation_meta = result["annotation_meta"]  # V1 top-level structure
```

### V2 → V1 Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v2_to_v1

# Complete conversion (annotation_data + annotation_meta)
v1_restored = convert_v2_to_v1(result)

# Convert with annotation_data only (uses defaults)
v1_basic = convert_v2_to_v1({"annotation_data": annotation_data})
```

## Detailed Guides

### Image Tools
- [Bounding Box Conversion](./image-bounding-box.md) - Bounding box annotation conversion
- [Polygon Conversion](./image-polygon.md) - Polygon annotation conversion
- [Polyline Conversion](./image-polyline.md) - Polyline annotation conversion
- [Keypoint Conversion](./image-keypoint.md) - Keypoint annotation conversion
- [Segmentation Conversion (Image)](./image-segmentation.md) - Image segmentation conversion
- [Classification Conversion](./image-classification.md) - Classification annotation conversion
- [Relation Conversion](./image-relation.md) - Annotation relationship conversion

### Video Tools
- [Segmentation Conversion (Video)](./video-segmentation.md) - Video segmentation conversion

### PCD (Point Cloud) Tools
- [3D Bounding Box Conversion](./pcd-3d-bounding-box.md) - 3D bounding box conversion
- [3D Segmentation Conversion](./pcd-3d-segmentation.md) - 3D segmentation conversion

### Text Tools
- [Named Entity Recognition Conversion](./text-named-entity.md) - NER annotation conversion

### Prompt Tools
- [Prompt Conversion](./prompt-prompt.md) - Prompt annotation conversion
- [Answer Conversion](./prompt-answer.md) - Answer annotation conversion

### Developer Documentation
- [Developer Guide](./developer-guide.md) - How to add new tools

## API Reference

### `convert_v1_to_v2(v1_data)`

Converts V1 data to V2 format.

**Parameters:**
- `v1_data`: DM Schema V1 format data

**Returns:**
- `V2ConversionResult`: Dictionary containing `annotation_data` and `annotation_meta`

### `convert_v2_to_v1(v2_data, annotation_meta=None)`

Converts V2 data to V1 format.

**Parameters:**
- `v2_data`: DM Schema V2 format data or V2ConversionResult
- `annotation_meta`: Optional V1 top-level structure passed separately

**Returns:**
- DM Schema V1 format data
