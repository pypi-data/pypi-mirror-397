---
id: image-segmentation
title: 세그멘테이션 변환 (이미지)
sidebar_position: 7
---

# 세그멘테이션 변환 (이미지)

이미지 세그멘테이션 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

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

### V2 구조

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

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `pixel_indices` | `data` (배열 그대로) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data` | `pixel_indices` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 세그멘테이션 데이터
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

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
seg = annotation_data["images"][0]["segmentation"][0]
print(seg["data"])  # [100, 101, 102, 200, 201, 202]
print(seg["classification"])  # "road"
```

### 대용량 픽셀 인덱스 처리

```python
# 대용량 세그멘테이션 마스크
import numpy as np

# 이미지 마스크에서 픽셀 인덱스 추출
mask = np.zeros((1080, 1920), dtype=np.uint8)
mask[100:200, 300:500] = 1  # 영역 마킹

# 픽셀 인덱스 계산 (row * width + col)
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

# 변환 및 검증
result = convert_v1_to_v2(v1_large)
restored = convert_v2_to_v1(result)

original_count = len(v1_large["annotationsData"]["image_1"][0]["pixel_indices"])
restored_count = len(restored["annotationsData"]["image_1"][0]["pixel_indices"])
assert original_count == restored_count
```

### 라운드트립 검증

```python
def verify_segmentation_roundtrip(v1_original):
    """세그멘테이션 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 픽셀 인덱스 비교
    orig_pixels = v1_original["annotationsData"]["image_1"][0]["pixel_indices"]
    rest_pixels = v1_restored["annotationsData"]["image_1"][0]["pixel_indices"]

    assert orig_pixels == rest_pixels

    print("세그멘테이션 라운드트립 검증 성공")

verify_segmentation_roundtrip(v1_data)
```

## 관련 문서

- [비디오 세그멘테이션 변환](./video-segmentation.md) - 비디오 세그멘테이션 변환
- [3D 세그멘테이션 변환](./pcd-3d-segmentation.md) - PCD 세그멘테이션 변환
