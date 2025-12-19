---
id: image-polygon
title: 폴리곤 변환
sidebar_position: 3
---

# 폴리곤 변환

폴리곤 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "poly_1",
    "tool": "polygon",
    "isLocked": False,
    "isVisible": True,
    "classification": {
        "class": "road"
    },
    "label": ["road"]
}

# annotationsData
{
    "id": "poly_1",
    "coordinate": [
        {"x": 100, "y": 200, "id": "pt1"},
        {"x": 150, "y": 250, "id": "pt2"},
        {"x": 200, "y": 200, "id": "pt3"}
    ]
}
```

### V2 구조

```python
{
    "id": "poly_1",
    "classification": "road",
    "attrs": [],
    "data": [[100, 200], [150, 250], [200, 200]]  # [[x, y], ...]
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `coordinate[{x, y, id}]` | `data[[x, y]]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

**참고:** V1의 각 점에 있는 `id` 필드는 V2로 변환 시 제거됩니다. 이 정보는 `annotation_meta`에 보존됩니다.

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data[[x, y]]` | `coordinate[{x, y, id}]` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

**참고:** V2에서 V1으로 변환 시 각 점에 대해 고유한 `id`가 자동 생성됩니다.

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 폴리곤 데이터
v1_polygon = {
    "annotations": {
        "image_1": [
            {
                "id": "AUjPgaMzQa",
                "tool": "polygon",
                "isLocked": False,
                "isVisible": True,
                "classification": {"class": "road"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "AUjPgaMzQa",
                "coordinate": [
                    {"x": 100, "y": 200, "id": "pt1"},
                    {"x": 150, "y": 250, "id": "pt2"},
                    {"x": 200, "y": 200, "id": "pt3"}
                ]
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_polygon)
annotation_data = result["annotation_data"]

# V2 결과 확인
polygon = annotation_data["images"][0]["polygon"][0]
print(polygon["data"])  # [[100, 200], [150, 250], [200, 200]]
print(polygon["classification"])  # "road"
```

### 복잡한 폴리곤 변환

```python
# 많은 점을 가진 복잡한 폴리곤
v1_complex = {
    "annotations": {
        "image_1": [
            {
                "id": "complex_poly",
                "tool": "polygon",
                "classification": {"class": "building"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "complex_poly",
                "coordinate": [
                    {"x": 0, "y": 0, "id": f"p{i}"}
                    for i in range(20)
                ] + [
                    {"x": i * 10, "y": i * 5, "id": f"p{20+i}"}
                    for i in range(20)
                ]
            }
        ]
    }
}

# V2로 변환 - 모든 점이 순서대로 보존됨
result = convert_v1_to_v2(v1_complex)
polygon = result["annotation_data"]["images"][0]["polygon"][0]
print(len(polygon["data"]))  # 40개 점 모두 보존
```

### 점 ID 생성

V2에서 V1으로 변환 시 각 점에 고유한 ID가 자동 생성됩니다:

```python
# V2 폴리곤 데이터 (점 ID 없음)
v2_polygon = {
    "annotation_data": {
        "images": [
            {
                "polygon": [
                    {
                        "id": "new_poly",
                        "classification": "road",
                        "attrs": [],
                        "data": [[0, 0], [100, 0], [50, 100]]
                    }
                ]
            }
        ]
    }
}

# V1으로 변환
v1_result = convert_v2_to_v1(v2_polygon)
coord = v1_result["annotationsData"]["image_1"][0]["coordinate"]

# 각 점에 고유 ID가 생성됨
for point in coord:
    print(f"x={point['x']}, y={point['y']}, id={point['id']}")
    # id는 랜덤 문자열로 생성됨

# 모든 ID가 고유한지 확인
ids = [p["id"] for p in coord]
assert len(ids) == len(set(ids))  # 중복 없음
```

### 라운드트립 검증

```python
def verify_polygon_roundtrip(v1_original):
    """폴리곤 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 좌표 비교
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    # 점 개수 일치
    assert len(orig_coord) == len(rest_coord)

    # 모든 점의 x, y 좌표 일치
    for orig_pt, rest_pt in zip(orig_coord, rest_coord):
        assert orig_pt["x"] == rest_pt["x"]
        assert orig_pt["y"] == rest_pt["y"]

    print("폴리곤 라운드트립 검증 성공")

verify_polygon_roundtrip(v1_polygon)
```

## 메타 정보 복원

`annotation_meta`를 사용하면 V1의 원본 점 ID도 복원됩니다:

```python
# 완전한 라운드트립 (annotation_meta 포함)
result = convert_v1_to_v2(v1_polygon)

# annotation_meta에 원본 점 ID 보존됨
meta = result["annotation_meta"]
orig_coord = meta["annotationsData"]["image_1"][0]["coordinate"]
print([p["id"] for p in orig_coord])  # ['pt1', 'pt2', 'pt3']

# V1으로 완전 복원
v1_restored = convert_v2_to_v1(result)
# 메타 정보 덕분에 어노테이션 레벨 정보가 완전 복원됨
```

## 주의사항

1. **점 순서**: 변환 시 점의 순서가 항상 유지됩니다.
2. **점 ID**: V2는 점 ID를 저장하지 않으므로, `annotation_meta` 없이 V1으로 변환하면 새 ID가 생성됩니다.
3. **최소 점 수**: 폴리곤은 최소 3개의 점이 필요합니다.
