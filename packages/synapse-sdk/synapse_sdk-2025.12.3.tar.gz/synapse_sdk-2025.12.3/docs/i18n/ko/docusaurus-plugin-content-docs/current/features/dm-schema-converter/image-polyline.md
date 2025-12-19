---
id: image-polyline
title: 폴리라인 변환
sidebar_position: 4
---

# 폴리라인 변환

폴리라인 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "polyline_1",
    "tool": "polyline",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "road_line",
        "type": "dashed"
    },
    "label": ["road_line"]
}

# annotationsData
{
    "id": "polyline_1",
    "coordinate": [
        {"x": 100, "y": 200, "id": "pt_1"},
        {"x": 150, "y": 250, "id": "pt_2"},
        {"x": 200, "y": 200, "id": "pt_3"}
    ]
}
```

### V2 구조

```python
{
    "id": "polyline_1",
    "classification": "road_line",
    "attrs": [
        {"name": "type", "value": "dashed"}
    ],
    "data": [[100, 200], [150, 250], [200, 200]]
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `coordinate[{x, y, id}]` | `data[[x, y], ...]` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data[[x, y], ...]` | `coordinate[{x, y, id}]` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

:::note
V2→V1 변환 시 점 ID는 `pt_0`, `pt_1`, ... 형태로 자동 생성됩니다.
:::

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 폴리라인 데이터
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "Line123abc",
                "tool": "polyline",
                "classification": {"class": "road_line", "type": "dashed"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "Line123abc",
                "coordinate": [
                    {"x": 100, "y": 200, "id": "pt_1"},
                    {"x": 150, "y": 250, "id": "pt_2"},
                    {"x": 200, "y": 200, "id": "pt_3"}
                ]
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
polyline = annotation_data["images"][0]["polyline"][0]
print(polyline["data"])  # [[100, 200], [150, 250], [200, 200]]
print(polyline["classification"])  # "road_line"
print(polyline["attrs"])  # [{"name": "type", "value": "dashed"}]
```

### 라운드트립 검증

```python
def verify_polyline_roundtrip(v1_original):
    """폴리라인 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 좌표 비교
    orig_coord = v1_original["annotationsData"]["image_1"][0]["coordinate"]
    rest_coord = v1_restored["annotationsData"]["image_1"][0]["coordinate"]

    assert len(orig_coord) == len(rest_coord)
    for i, (orig, rest) in enumerate(zip(orig_coord, rest_coord)):
        assert orig["x"] == rest["x"]
        assert orig["y"] == rest["y"]

    print("폴리라인 라운드트립 검증 성공")

verify_polyline_roundtrip(v1_data)
```

## 폴리곤과의 차이점

| 특성 | 폴리라인 | 폴리곤 |
|------|----------|--------|
| 도형 닫힘 | 열린 도형 | 닫힌 도형 |
| 최소 점 | 2개 | 3개 |
| 용도 | 선, 경로 | 영역 |
