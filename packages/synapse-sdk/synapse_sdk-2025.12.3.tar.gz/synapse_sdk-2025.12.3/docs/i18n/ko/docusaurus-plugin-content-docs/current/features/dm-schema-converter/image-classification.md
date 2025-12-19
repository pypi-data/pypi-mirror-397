---
id: image-classification
title: 분류 변환
sidebar_position: 11
---

# 분류 변환

이미지 분류(Classification) 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "cls_1",
    "tool": "classification",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "cat",
        "confidence": 0.98,
        "breed": "persian"
    },
    "label": ["cat"]
}

# annotationsData (id만 존재)
{
    "id": "cls_1"
}
```

### V2 구조

```python
{
    "id": "cls_1",
    "classification": "cat",
    "attrs": [
        {"name": "confidence", "value": 0.98},
        {"name": "breed", "value": "persian"}
    ],
    "data": {}  # 빈 객체
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| (없음) | `data: {}` (빈 객체) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data` | (무시됨) |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

:::note
분류 도구는 좌표 데이터가 없으므로 `annotationsData`에 `id`만 저장됩니다.
V2에서는 `data`가 빈 객체 `{}`입니다.
:::

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 분류 데이터
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "ClsAbc1234",
                "tool": "classification",
                "classification": {"class": "cat", "confidence": 0.98, "breed": "persian"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "ClsAbc1234"
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
cls = annotation_data["images"][0]["classification"][0]
print(cls["classification"])  # "cat"
print(cls["data"])  # {}
print(cls["attrs"])  # [{"name": "confidence", "value": 0.98}, {"name": "breed", "value": "persian"}]
```

### 다중 레이블 처리

```python
# 여러 분류 태그가 있는 이미지
v1_multi = {
    "annotations": {
        "image_1": [
            {"id": "cls_animal", "tool": "classification", "classification": {"class": "animal"}},
            {"id": "cls_indoor", "tool": "classification", "classification": {"class": "indoor"}},
            {"id": "cls_pet", "tool": "classification", "classification": {"class": "pet"}}
        ]
    },
    "annotationsData": {
        "image_1": [
            {"id": "cls_animal"},
            {"id": "cls_indoor"},
            {"id": "cls_pet"}
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_multi)
classifications = result["annotation_data"]["images"][0]["classification"]

for cls in classifications:
    print(cls["classification"])
# animal
# indoor
# pet
```

### 라운드트립 검증

```python
def verify_classification_roundtrip(v1_original):
    """분류 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 분류 비교
    orig_cls = v1_original["annotations"]["image_1"][0]["classification"]
    rest_cls = v1_restored["annotations"]["image_1"][0]["classification"]

    assert orig_cls["class"] == rest_cls["class"]

    print("분류 라운드트립 검증 성공")

verify_classification_roundtrip(v1_data)
```

## 다른 도구와의 차이

| 특성 | 분류 | 바운딩 박스 |
|------|------|-------------|
| 좌표 데이터 | 없음 | 있음 |
| V1 annotationsData | id만 | coordinate |
| V2 data | `{}` | `[x, y, w, h]` |
| 용도 | 이미지 전체 태깅 | 영역 지정 |
