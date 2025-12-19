---
id: prompt-prompt
title: 프롬프트 변환
sidebar_position: 13
---

# 프롬프트 변환

프롬프트(Prompt) 어노테이션의 V1/V2 양방향 변환 가이드입니다.

## 데이터 구조

### V1 구조

```python
# annotations
{
    "id": "prompt_1",
    "tool": "prompt",
    "isLocked": False,
    "isVisible": True,
    "isValid": True,
    "classification": {
        "class": "question"
    },
    "label": ["question"]
}

# annotationsData
{
    "id": "prompt_1",
    "tool": "prompt",
    "input": [
        {
            "type": "text",
            "value": "What is shown in this image?",
            "changeHistory": []
        }
    ]
}
```

### V2 구조

```python
{
    "id": "prompt_1",
    "classification": "question",
    "attrs": [],
    "data": {
        "input": [
            {
                "type": "text",
                "value": "What is shown in this image?",
                "changeHistory": []
            }
        ]
    }
}
```

## 변환 규칙

### V1 → V2

| V1 필드 | V2 필드 |
|---------|---------|
| `input` | `data.input` |
| `model` | `data.model` (있는 경우) |
| `displayName` | `data.displayName` (있는 경우) |
| `generatedBy` | `data.generatedBy` (있는 경우) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 필드 | V1 필드 |
|---------|---------|
| `data.input` | `input` |
| `data.model` | `model` |
| `data.displayName` | `displayName` |
| `data.generatedBy` | `generatedBy` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## 사용 예제

### 기본 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 프롬프트 데이터
v1_data = {
    "annotations": {
        "prompt_1": [
            {
                "id": "PromptAbc123",
                "tool": "prompt",
                "classification": {"class": "question"}
            }
        ]
    },
    "annotationsData": {
        "prompt_1": [
            {
                "id": "PromptAbc123",
                "tool": "prompt",
                "input": [
                    {
                        "type": "text",
                        "value": "What is shown in this image?",
                        "changeHistory": []
                    }
                ]
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# V2 결과 확인
prompt = annotation_data["prompts"][0]["prompt"][0]
print(prompt["data"]["input"])  # [{"type": "text", "value": "What is shown in this image?", ...}]
print(prompt["classification"])  # "question"
```

### 다중 입력 처리

```python
# 여러 입력이 포함된 프롬프트
v1_multi_input = {
    "annotations": {
        "prompt_1": [
            {"id": "MultiPrompt", "tool": "prompt", "classification": {"class": "complex_query"}}
        ]
    },
    "annotationsData": {
        "prompt_1": [
            {
                "id": "MultiPrompt",
                "tool": "prompt",
                "input": [
                    {"type": "text", "value": "Describe this image.", "changeHistory": []},
                    {"type": "text", "value": "Focus on the main subject.", "changeHistory": []}
                ]
            }
        ]
    }
}

# V2로 변환
result = convert_v1_to_v2(v1_multi_input)
prompt = result["annotation_data"]["prompts"][0]["prompt"][0]

for inp in prompt["data"]["input"]:
    print(f"Type: {inp['type']}, Value: {inp['value']}")
```

### 라운드트립 검증

```python
def verify_prompt_roundtrip(v1_original):
    """프롬프트 라운드트립 검증"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # 입력 비교
    orig_input = v1_original["annotationsData"]["prompt_1"][0]["input"]
    rest_input = v1_restored["annotationsData"]["prompt_1"][0]["input"]

    assert orig_input == rest_input

    print("프롬프트 라운드트립 검증 성공")

verify_prompt_roundtrip(v1_data)
```

## 관련 문서

- [답변 변환](./prompt-answer.md) - 프롬프트에 대한 답변 어노테이션
