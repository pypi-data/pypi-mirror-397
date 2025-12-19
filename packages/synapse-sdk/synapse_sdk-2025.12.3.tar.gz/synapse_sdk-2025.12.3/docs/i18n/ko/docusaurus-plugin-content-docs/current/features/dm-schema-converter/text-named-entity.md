---
id: text-named-entity
title: 개체명 인식 변환
sidebar_position: 10
---

# 개체명 인식 변환

텍스트용 개체명 인식(Named Entity Recognition) 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "ner_1",
    "tool": "named_entity",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "PERSON",
        "confidence": 0.95
    },
    "label": ["PERSON"]
}

# annotationsData
{
    "id": "ner_1",
    "ranges": [{"start": 0, "end": 5}],
    "content": "John"
}
```

### V2 구조

```python
{
    "id": "ner_1",
    "classification": "PERSON",
    "attrs": [
        {"name": "confidence", "value": 0.95}
    ],
    "data": {
        "ranges": [{"start": 0, "end": 5}],
        "content": "John"
    }
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `ranges` | `data.ranges` |
| `content` | `data.content` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data.ranges` | `ranges` |
| `data.content` | `content` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 개체명 인식 데이터
v1_data = {
    "annotations": {
        "text_1": [
            {
                "id": "NerAbc1234",
                "tool": "named_entity",
                "classification": {"class": "PERSON", "confidence": 0.95}
            }
        ]
    },
    "annotationsData": {
        "text_1": [
            {
                "id": "NerAbc1234",
                "ranges": [{"start": 0, "end": 4}],
                "content": "John"
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
ner = annotation_data["texts"][0]["named_entity"][0]
print(ner["data"]["ranges"])  # [{"start": 0, "end": 4}]
print(ner["data"]["content"])  # "John"
print(ner["classification"])  # "PERSON"
```

### 여러 개체 처리

```python
# 여러 개체명이 포함된 텍스트
# "John met Mary at New York."
v1_multi = {
    "annotations": {
        "text_1": [
            {"id": "ner_john", "tool": "named_entity", "classification": {"class": "PERSON"}},
            {"id": "ner_mary", "tool": "named_entity", "classification": {"class": "PERSON"}},
            {"id": "ner_nyc", "tool": "named_entity", "classification": {"class": "LOCATION"}}
        ]
    },
    "annotationsData": {
        "text_1": [
            {"id": "ner_john", "ranges": [{"start": 0, "end": 4}], "content": "John"},
            {"id": "ner_mary", "ranges": [{"start": 9, "end": 13}], "content": "Mary"},
            {"id": "ner_nyc", "ranges": [{"start": 17, "end": 25}], "content": "New York"}
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_multi)
entities = result["annotation_data"]["texts"][0]["named_entity"]

for ent in entities:
    print(f"{ent['classification']}: {ent['data']['content']} ({ent['data']['ranges']})")
# PERSON: John ([{"start": 0, "end": 4}])
# PERSON: Mary ([{"start": 9, "end": 13}])
# LOCATION: New York ([{"start": 17, "end": 25}])
```

### 라운드트립 검증

```python
def verify_ner_roundtrip(v1_original):
    """개체명 인식 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 데이터 비교
    orig_data = v1_original["annotationsData"]["text_1"][0]
    rest_data = v1_restored["annotationsData"]["text_1"][0]

    assert orig_data["ranges"] == rest_data["ranges"]
    assert orig_data["content"] == rest_data["content"]

    print("개체명 인식 라운드트립 검증 성공")

verify_ner_roundtrip(v1_data)
```

## 개체명 타입

일반적으로 사용되는 개체명 타입:

| 타입 | 설명 | 예시 |
|------|------|------|
| PERSON | 인물 | 홍길동, John |
| ORGANIZATION | 조직/기관 | 삼성전자, Google |
| LOCATION | 장소 | 서울, New York |
| DATE | 날짜 | 2025년 1월 |
| TIME | 시간 | 오후 3시 |
| MONEY | 금액 | $100, 만원 |
