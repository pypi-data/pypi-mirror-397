---
id: video-segmentation
title: 세그멘테이션 변환 (비디오)
sidebar_position: 8
---

# 세그멘테이션 변환 (비디오)

비디오 세그멘테이션 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

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

### V2 구조

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

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `section.startFrame` | `data.startFrame` |
| `section.endFrame` | `data.endFrame` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data.startFrame` | `section.startFrame` |
| `data.endFrame` | `section.endFrame` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 비디오 세그멘테이션 데이터
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

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
seg = annotation_data["videos"][0]["segmentation"][0]
print(seg["data"])  # {"startFrame": 100, "endFrame": 250}
print(seg["classification"])  # "action"
```

### 여러 구간 처리

```python
# 비디오 내 여러 액션 구간
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

# V2로 변환
result = convert_v1_to_v2(v1_multi)
segments = result["annotation_data"]["videos"][0]["segmentation"]

for seg in segments:
    print(f"{seg['classification']}: frame {seg['data']['startFrame']}-{seg['data']['endFrame']}")
# walking: frame 0-100
# running: frame 101-200
# standing: frame 201-300
```

### 라운드트립 검증

```python
def verify_video_seg_roundtrip(v1_original):
    """비디오 세그멘테이션 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 섹션 비교
    orig_section = v1_original["annotationsData"]["video_1"][0]["section"]
    rest_section = v1_restored["annotationsData"]["video_1"][0]["section"]

    assert orig_section["startFrame"] == rest_section["startFrame"]
    assert orig_section["endFrame"] == rest_section["endFrame"]

    print("비디오 세그멘테이션 라운드트립 검증 성공")

verify_video_seg_roundtrip(v1_data)
```

## 이미지 vs 비디오 세그멘테이션

| 특성 | 이미지 | 비디오 |
|------|--------|--------|
| V1 데이터 필드 | `pixel_indices` | `section` |
| V2 data 타입 | `list[int]` | `{startFrame, endFrame}` |
| 미디어 ID | `image_N` | `video_N` |
| 용도 | 픽셀 마스크 | 프레임 구간 |
