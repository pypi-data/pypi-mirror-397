---
id: image-bounding-box
title: 바운딩 박스 변환
sidebar_position: 2
---

# 바운딩 박스 변환

바운딩 박스 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "ann_1",
    "tool": "bounding_box",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "person",
        "color": "red"  # 추가 속성
    },
    "label": ["person"]
}

# annotationsData
{
    "id": "ann_1",
    "coordinate": {
        "x": 100,
        "y": 200,
        "width": 150,
        "height": 100,
        "rotation": 0.5236  # 선택적
    }
}
```

### V2 구조

```python
{
    "id": "ann_1",
    "classification": "person",
    "attrs": [
        {"name": "color", "value": "red"},
        {"name": "rotation", "value": 0.5236}
    ],
    "data": [100, 200, 150, 100]  # [x, y, width, height]
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `coordinate.{x, y, width, height}` | `data[0, 1, 2, 3]` |
| `coordinate.rotation` | `attrs[{name: "rotation", value}]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data[0, 1, 2, 3]` | `coordinate.{x, y, width, height}` |
| `attrs.rotation` | `coordinate.rotation` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 바운딩 박스 데이터
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "Cd1qfFQFI4",
                "tool": "bounding_box",
                "isLocked": False,
                "isVisible": True,
                "classification": {"class": "person", "color": "red"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "Cd1qfFQFI4",
                "coordinate": {"x": 100, "y": 200, "width": 150, "height": 100}
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
bbox = annotation_data["images"][0]["bounding_box"][0]
print(bbox["data"])  # [100, 200, 150, 100]
print(bbox["classification"])  # "person"
print(bbox["attrs"])  # [{"name": "color", "value": "red"}]
```

### rotation 포함 변환

```python
# rotation이 포함된 바운딩 박스
v1_rotated = {
    "annotations": {
        "image_1": [
            {
                "id": "Rot12345ab",
                "tool": "bounding_box",
                "classification": {"class": "text"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "Rot12345ab",
                "coordinate": {
                    "x": 50,
                    "y": 100,
                    "width": 200,
                    "height": 50,
                    "rotation": 0.5236  # 약 30도 (라디안)
                }
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_rotated)
bbox = result["annotation_data"]["images"][0]["bounding_box"][0]

# rotation은 attrs에 보존됨
print(bbox["data"])  # [50, 100, 200, 50]
rotation_attr = [a for a in bbox["attrs"] if a["name"] == "rotation"][0]
print(rotation_attr["value"])  # 0.5236

# V1으로 복원
v1_restored = convert_v2_to_v1(result)
restored_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]
print(restored_coord["rotation"])  # 0.5236 (보존됨)
```

### 라운드트립 검증

```python
def verify_bounding_box_roundtrip(v1_original):
    """바운딩 박스 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 좌표 비교
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    assert orig_coord["x"] == rest_coord["x"]
    assert orig_coord["y"] == rest_coord["y"]
    assert orig_coord["width"] == rest_coord["width"]
    assert orig_coord["height"] == rest_coord["height"]

    if "rotation" in orig_coord:
        assert orig_coord["rotation"] == rest_coord["rotation"]

    print("바운딩 박스 라운드트립 검증 성공")

verify_bounding_box_roundtrip(v1_data)
```

## 메타 정보 복원

`annotation_meta`를 함께 전달하면 V1의 메타 필드가 완전히 복원됩니다:

```python
# 완전한 변환 (메타 정보 포함)
v1_full = convert_v2_to_v1(result)

# 메타 필드 확인
ann = v1_full["annotations"]["image_1"][0]
print(ann["isLocked"])  # False (원본 값)
print(ann["isVisible"])  # True (원본 값)
print(ann["isValid"])  # True (원본 값)

# annotation_data만으로 변환 시 기본값 사용
v1_basic = convert_v2_to_v1({"annotation_data": annotation_data})
ann_basic = v1_basic["annotations"]["image_1"][0]
print(ann_basic["isLocked"])  # False (기본값)
print(ann_basic["isValid"])  # False (기본값)
```
