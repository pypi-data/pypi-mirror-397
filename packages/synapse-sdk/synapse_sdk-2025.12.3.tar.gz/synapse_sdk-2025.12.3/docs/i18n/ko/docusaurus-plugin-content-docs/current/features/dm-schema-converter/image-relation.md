---
id: image-relation
title: 관계 변환
sidebar_position: 12
---

# 관계 변환

어노테이션 간 관계(Relation) 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "rel_1",
    "tool": "relation",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "belongs_to",
        "confidence": 0.9
    },
    "label": ["belongs_to"]
}

# annotationsData
{
    "id": "rel_1",
    "annotationId": "BBoxAbc001",      # from (소스 어노테이션)
    "targetAnnotationId": "BBoxAbc002"  # to (타겟 어노테이션)
}
```

### V2 구조

```python
{
    "id": "rel_1",
    "classification": "belongs_to",
    "attrs": [
        {"name": "confidence", "value": 0.9}
    ],
    "data": ["BBoxAbc001", "BBoxAbc002"]  # [from_id, to_id]
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `annotationId` | `data[0]` (from_id) |
| `targetAnnotationId` | `data[1]` (to_id) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data[0]` | `annotationId` |
| `data[1]` | `targetAnnotationId` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 관계 데이터
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "RelAbc123",
                "tool": "relation",
                "classification": {"class": "belongs_to", "confidence": 0.9}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "RelAbc123",
                "annotationId": "BBoxAbc001",
                "targetAnnotationId": "BBoxAbc002"
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
rel = annotation_data["images"][0]["relation"][0]
print(rel["data"])  # ["BBoxAbc001", "BBoxAbc002"]
print(rel["classification"])  # "belongs_to"
```

### 복잡한 관계 그래프

```python
# 여러 객체 간 관계
# person -> (holding) -> bag
# person -> (wearing) -> hat
# bag -> (near) -> chair

v1_graph = {
    "annotations": {
        "image_1": [
            {"id": "rel_holding", "tool": "relation", "classification": {"class": "holding"}},
            {"id": "rel_wearing", "tool": "relation", "classification": {"class": "wearing"}},
            {"id": "rel_near", "tool": "relation", "classification": {"class": "near"}}
        ]
    },
    "annotationsData": {
        "image_1": [
            {"id": "rel_holding", "annotationId": "person_1", "targetAnnotationId": "bag_1"},
            {"id": "rel_wearing", "annotationId": "person_1", "targetAnnotationId": "hat_1"},
            {"id": "rel_near", "annotationId": "bag_1", "targetAnnotationId": "chair_1"}
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_graph)
relations = result["annotation_data"]["images"][0]["relation"]

for rel in relations:
    from_id, to_id = rel["data"]
    print(f"{from_id} --{rel['classification']}--> {to_id}")
# person_1 --holding--> bag_1
# person_1 --wearing--> hat_1
# bag_1 --near--> chair_1
```

### 라운드트립 검증

```python
def verify_relation_roundtrip(v1_original):
    """관계 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 관계 비교
    orig_data = v1_original["annotationsData"]["image_1"][0]
    rest_data = v1_restored["annotationsData"]["image_1"][0]

    assert orig_data["annotationId"] == rest_data["annotationId"]
    assert orig_data["targetAnnotationId"] == rest_data["targetAnnotationId"]

    print("관계 라운드트립 검증 성공")

verify_relation_roundtrip(v1_data)
```

## 관계 타입

일반적인 관계 타입:

| 타입 | 설명 | 예시 |
|------|------|------|
| belongs_to | 소속 관계 | 사람 → 그룹 |
| part_of | 부분 관계 | 바퀴 → 자동차 |
| near | 근접 관계 | 의자 → 테이블 |
| holding | 들고 있음 | 사람 → 가방 |
| wearing | 착용 | 사람 → 모자 |
| parent_of | 부모-자식 | 부모 → 자식 |
