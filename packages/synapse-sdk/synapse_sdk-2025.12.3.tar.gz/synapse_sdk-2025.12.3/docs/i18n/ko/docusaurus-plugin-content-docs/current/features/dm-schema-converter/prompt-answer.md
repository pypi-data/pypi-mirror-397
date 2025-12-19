---
id: prompt-answer
title: 답변 변환
sidebar_position: 14
---

# 답변 변환

답변(Answer) 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "answer_1",
    "tool": "answer",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "response"
    },
    "label": ["response"]
}

# annotationsData
{
    "id": "answer_1",
    "tool": "answer",
    "model": "gpt-4",
    "output": [
        {
            "type": "text",
            "value": "This image shows a cat sitting on a couch.",
            "primaryKey": "main",
            "changeHistory": []
        }
    ],
    "displayName": "GPT-4 Response",
    "generatedBy": "ai",
    "promptAnnotationId": "PromptAbc123"  # 연결된 프롬프트
}
```

### V2 구조

```python
{
    "id": "answer_1",
    "classification": "response",
    "attrs": [],
    "data": {
        "model": "gpt-4",
        "output": [
            {
                "type": "text",
                "value": "This image shows a cat sitting on a couch.",
                "primaryKey": "main",
                "changeHistory": []
            }
        ],
        "displayName": "GPT-4 Response",
        "generatedBy": "ai",
        "promptAnnotationId": "PromptAbc123"
    }
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `output` | `data.output` |
| `model` | `data.model` |
| `displayName` | `data.displayName` |
| `generatedBy` | `data.generatedBy` |
| `promptAnnotationId` | `data.promptAnnotationId` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data.output` | `output` |
| `data.model` | `model` |
| `data.displayName` | `displayName` |
| `data.generatedBy` | `generatedBy` |
| `data.promptAnnotationId` | `promptAnnotationId` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 답변 데이터
v1_data = {
    "annotations": {
        "prompt_1": [
            {
                "id": "AnswerXyz789",
                "tool": "answer",
                "classification": {"class": "response"}
            }
        ]
    },
    "annotationsData": {
        "prompt_1": [
            {
                "id": "AnswerXyz789",
                "tool": "answer",
                "model": "gpt-4",
                "output": [
                    {
                        "type": "text",
                        "value": "This image shows a cat sitting on a couch.",
                        "primaryKey": "main",
                        "changeHistory": []
                    }
                ],
                "displayName": "GPT-4 Response",
                "generatedBy": "ai",
                "promptAnnotationId": "PromptAbc123"
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
answer = annotation_data["prompts"][0]["answer"][0]
print(answer["data"]["output"])  # [{"type": "text", "value": "...", ...}]
print(answer["data"]["model"])  # "gpt-4"
print(answer["data"]["promptAnnotationId"])  # "PromptAbc123"
```

### 프롬프트-답변 쌍 처리

```python
# 프롬프트와 답변이 함께 있는 데이터
v1_qa = {
    "annotations": {
        "prompt_1": [
            {"id": "Q1", "tool": "prompt", "classification": {"class": "question"}},
            {"id": "A1", "tool": "answer", "classification": {"class": "response"}}
        ]
    },
    "annotationsData": {
        "prompt_1": [
            {
                "id": "Q1",
                "tool": "prompt",
                "input": [{"type": "text", "value": "What color is the cat?"}]
            },
            {
                "id": "A1",
                "tool": "answer",
                "model": "human",
                "output": [{"type": "text", "value": "The cat is orange."}],
                "generatedBy": "human",
                "promptAnnotationId": "Q1"
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_qa)

# 프롬프트와 답변 모두 포함
prompts = result["annotation_data"]["prompts"][0].get("prompt", [])
answers = result["annotation_data"]["prompts"][0].get("answer", [])

print(f"Prompts: {len(prompts)}, Answers: {len(answers)}")
```

### 라운드트립 검증

```python
def verify_answer_roundtrip(v1_original):
    """답변 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 출력 비교
    orig_data = v1_original["annotationsData"]["prompt_1"][0]
    rest_data = v1_restored["annotationsData"]["prompt_1"][0]

    assert orig_data["output"] == rest_data["output"]
    assert orig_data["model"] == rest_data["model"]
    assert orig_data["promptAnnotationId"] == rest_data["promptAnnotationId"]

    print("답변 라운드트립 검증 성공")

verify_answer_roundtrip(v1_data)
```

## 필드 설명

| 필드 | 설명 |
|------|------|
| `output` | 답변 내용 배열 |
| `model` | 생성 모델 (예: gpt-4, human) |
| `displayName` | 표시 이름 |
| `generatedBy` | 생성 주체 (ai/human) |
| `promptAnnotationId` | 연결된 프롬프트 ID |

## 관련 문서

- [프롬프트 변환](./prompt-prompt.md) - 프롬프트 어노테이션
