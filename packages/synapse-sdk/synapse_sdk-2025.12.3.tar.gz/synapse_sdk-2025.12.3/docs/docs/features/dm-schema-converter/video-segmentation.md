---
id: video-segmentation
title: Segmentation Conversion (Video)
sidebar_position: 8
---

# Segmentation Conversion (Video)

A guide for bidirectional V1/V2 conversion of video segmentation annotations.

## Data Structure

### V1 Structure

```python
# annotations
{
    "id": "vid_seg_1",
    "tool": "segmentation",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "action",
        "action_type": "walking"
    },
    "label": ["action"]
}

# annotationsData
{
    "id": "vid_seg_1",
    "section": {
        "startFrame": 100,
        "endFrame": 250
    }
}
```

### V2 Structure

```python
{
    "id": "vid_seg_1",
    "classification": "action",
    "attrs": [
        {"name": "action_type", "value": "walking"}
    ],
    "data": {
        "startFrame": 100,
        "endFrame": 250
    }
}
```

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `section.startFrame` | `data.startFrame` |
| `section.endFrame` | `data.endFrame` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data.startFrame` | `section.startFrame` |
| `data.endFrame` | `section.endFrame` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 video segmentation data
v1_data = {
    "annotations": {
        "video_1": [
            {
                "id": "VidSeg123",
                "tool": "segmentation",
                "classification": {"class": "action", "action_type": "walking"}
            }
        ]
    },
    "annotationsData": {
        "video_1": [
            {
                "id": "VidSeg123",
                "section": {"startFrame": 100, "endFrame": 250}
            }
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
seg = annotation_data["videos"][0]["segmentation"][0]
print(seg["data"])  # {"startFrame": 100, "endFrame": 250}
print(seg["classification"])  # "action"
```

### Multiple Segment Processing

```python
# Multiple action segments in a video
v1_multi = {
    "annotations": {
        "video_1": [
            {"id": "seg_walk", "tool": "segmentation", "classification": {"class": "walking"}},
            {"id": "seg_run", "tool": "segmentation", "classification": {"class": "running"}},
            {"id": "seg_stand", "tool": "segmentation", "classification": {"class": "standing"}}
        ]
    },
    "annotationsData": {
        "video_1": [
            {"id": "seg_walk", "section": {"startFrame": 0, "endFrame": 100}},
            {"id": "seg_run", "section": {"startFrame": 101, "endFrame": 200}},
            {"id": "seg_stand", "section": {"startFrame": 201, "endFrame": 300}}
        ]
    }
}

# Convert to V2
result = convert_v1_to_v2(v1_multi)
segments = result["annotation_data"]["videos"][0]["segmentation"]

for seg in segments:
    print(f"{seg['classification']}: frame {seg['data']['startFrame']}-{seg['data']['endFrame']}")
# walking: frame 0-100
# running: frame 101-200
# standing: frame 201-300
```

### Roundtrip Verification

```python
def verify_video_seg_roundtrip(v1_original):
    """Verify video segmentation roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare sections
    orig_section = v1_original["annotationsData"]["video_1"][0]["section"]
    rest_section = v1_restored["annotationsData"]["video_1"][0]["section"]

    assert orig_section["startFrame"] == rest_section["startFrame"]
    assert orig_section["endFrame"] == rest_section["endFrame"]

    print("Video segmentation roundtrip verification successful")

verify_video_seg_roundtrip(v1_data)
```

## Image vs Video Segmentation

| Property | Image | Video |
|----------|-------|-------|
| V1 data field | `pixel_indices` | `section` |
| V2 data type | `list[int]` | `{startFrame, endFrame}` |
| Media ID | `image_N` | `video_N` |
| Purpose | Pixel mask | Frame range |
