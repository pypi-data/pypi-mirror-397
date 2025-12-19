---
id: pcd-3d-bounding-box
title: 3D 바운딩 박스 변환
sidebar_position: 6
---

# 3D 바운딩 박스 변환

PCD(Point Cloud Data)용 3D 바운딩 박스 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

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
        "rotation": {"x": 0, "y": 0, "z": 0.785}  # 라디안
    }
}
```

### V2 구조

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

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `psr.position` | `data.position` |
| `psr.scale` | `data.scale` |
| `psr.rotation` | `data.rotation` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data.position` | `psr.position` |
| `data.scale` | `psr.scale` |
| `data.rotation` | `psr.rotation` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 3D 바운딩 박스 데이터
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

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
bbox3d = annotation_data["pcds"][0]["3d_bounding_box"][0]
print(bbox3d["data"]["position"])  # {"x": 10.5, "y": 20.3, "z": 1.2}
print(bbox3d["data"]["scale"])  # {"x": 4.5, "y": 2.0, "z": 1.5}
print(bbox3d["classification"])  # "car"
```

### 라운드트립 검증

```python
def verify_3d_bbox_roundtrip(v1_original):
    """3D 바운딩 박스 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # PSR 비교
    orig_psr = v1_original["annotationsData"]["pcd_1"][0]["psr"]
    rest_psr = v1_restored["annotationsData"]["pcd_1"][0]["psr"]

    for key in ["position", "scale", "rotation"]:
        for axis in ["x", "y", "z"]:
            assert orig_psr[key][axis] == rest_psr[key][axis]

    print("3D 바운딩 박스 라운드트립 검증 성공")

verify_3d_bbox_roundtrip(v1_data)
```

## PSR 좌표계

3D 바운딩 박스는 PSR(Position, Scale, Rotation) 형식을 사용합니다:

| 필드 | 설명 | 단위 |
|------|------|------|
| position.x | X 위치 | 미터 |
| position.y | Y 위치 | 미터 |
| position.z | Z 위치 | 미터 |
| scale.x | X 크기 (길이) | 미터 |
| scale.y | Y 크기 (너비) | 미터 |
| scale.z | Z 크기 (높이) | 미터 |
| rotation.x | X축 회전 | 라디안 |
| rotation.y | Y축 회전 | 라디안 |
| rotation.z | Z축 회전 (요) | 라디안 |
