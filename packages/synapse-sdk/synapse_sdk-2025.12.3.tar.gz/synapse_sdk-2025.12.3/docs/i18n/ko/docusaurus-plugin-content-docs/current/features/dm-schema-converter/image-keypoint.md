---
id: image-keypoint
title: 키포인트 변환
sidebar_position: 5
---

# 키포인트 변환

키포인트 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

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

### V2 구조

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

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `coordinate.{x, y}` | `data[0, 1]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data[0, 1]` | `coordinate.{x, y}` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 키포인트 데이터
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

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
kp = annotation_data["images"][0]["keypoint"][0]
print(kp["data"])  # [150.5, 200.3]
print(kp["classification"])  # "joint"
print(kp["attrs"])  # [{"name": "body_part", "value": "elbow"}]
```

### 여러 키포인트 처리

```python
# 스켈레톤 포즈 데이터
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

# V2로 변환
result = convert_v1_to_v2(v1_skeleton)
keypoints = result["annotation_data"]["images"][0]["keypoint"]

for kp in keypoints:
    print(f"{kp['classification']}: {kp['data']}")
# head: [100, 50]
# shoulder: [100, 100]
# elbow: [130, 150]
```

### 라운드트립 검증

```python
def verify_keypoint_roundtrip(v1_original):
    """키포인트 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 좌표 비교
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    assert orig_coord["x"] == rest_coord["x"]
    assert orig_coord["y"] == rest_coord["y"]

    print("키포인트 라운드트립 검증 성공")

verify_keypoint_roundtrip(v1_data)
```
