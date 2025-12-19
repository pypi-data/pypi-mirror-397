---
id: pcd-3d-segmentation
title: 3D 세그멘테이션 변환
sidebar_position: 9
---

# 3D 세그멘테이션 변환

PCD(Point Cloud Data)용 3D 세그멘테이션 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

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

### V2 구조

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

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `points` | `data.points` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data.points` | `points` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 3D 세그멘테이션 데이터
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

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
seg3d = annotation_data["pcds"][0]["3d_segmentation"][0]
print(seg3d["data"]["points"])  # [0, 1, 5, 10, 15, 20, 25, 30, 35]
print(seg3d["classification"])  # "ground"
```

### 대용량 포인트 클라우드 처리

```python
import numpy as np

# 포인트 클라우드에서 세그멘테이션 인덱스 추출
point_cloud = np.random.rand(100000, 3)  # 10만개 포인트
ground_mask = point_cloud[:, 2] < 0.1  # 낮은 높이 포인트 선택
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

# 변환 및 검증
result = convert_v1_to_v2(v1_large)
restored = convert_v2_to_v1(result)

original_count = len(v1_large["annotationsData"]["pcd_1"][0]["points"])
restored_count = len(restored["annotationsData"]["pcd_1"][0]["points"])
assert original_count == restored_count
```

### 라운드트립 검증

```python
def verify_3d_seg_roundtrip(v1_original):
    """3D 세그멘테이션 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 포인트 비교
    orig_points = v1_original["annotationsData"]["pcd_1"][0]["points"]
    rest_points = v1_restored["annotationsData"]["pcd_1"][0]["points"]

    assert orig_points == rest_points

    print("3D 세그멘테이션 라운드트립 검증 성공")

verify_3d_seg_roundtrip(v1_data)
```

## 이미지 vs 3D 세그멘테이션

| 특성 | 이미지 | 3D |
|------|--------|-----|
| V1 데이터 필드 | `pixel_indices` | `points` |
| V2 data 타입 | `list[int]` | `{points: list[int]}` |
| 미디어 ID | `image_N` | `pcd_N` |
| 인덱스 의미 | 픽셀 인덱스 | 포인트 인덱스 |
