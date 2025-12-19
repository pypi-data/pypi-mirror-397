---
id: prompt-answer
title: Answer Conversion
sidebar_position: 14
---

# Answer Conversion

A guide for bidirectional V1/V2 conversion of answer annotations.

## Data Structure

### V1 Structure

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
    "promptAnnotationId": "PromptAbc123"  # linked prompt
}
```

### V2 Structure

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

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `output` | `data.output` |
| `model` | `data.model` |
| `displayName` | `data.displayName` |
| `generatedBy` | `data.generatedBy` |
| `promptAnnotationId` | `data.promptAnnotationId` |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data.output` | `output` |
| `data.model` | `model` |
| `data.displayName` | `displayName` |
| `data.generatedBy` | `generatedBy` |
| `data.promptAnnotationId` | `promptAnnotationId` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 answer data
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

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
answer = annotation_data["prompts"][0]["answer"][0]
print(answer["data"]["output"])  # [{"type": "text", "value": "...", ...}]
print(answer["data"]["model"])  # "gpt-4"
print(answer["data"]["promptAnnotationId"])  # "PromptAbc123"
```

### Prompt-Answer Pair Processing

```python
# Data with both prompt and answer
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

# Convert to V2
result = convert_v1_to_v2(v1_qa)

# Both prompt and answer included
prompts = result["annotation_data"]["prompts"][0].get("prompt", [])
answers = result["annotation_data"]["prompts"][0].get("answer", [])

print(f"Prompts: {len(prompts)}, Answers: {len(answers)}")
```

### Roundtrip Verification

```python
def verify_answer_roundtrip(v1_original):
    """Verify answer roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare output
    orig_data = v1_original["annotationsData"]["prompt_1"][0]
    rest_data = v1_restored["annotationsData"]["prompt_1"][0]

    assert orig_data["output"] == rest_data["output"]
    assert orig_data["model"] == rest_data["model"]
    assert orig_data["promptAnnotationId"] == rest_data["promptAnnotationId"]

    print("Answer roundtrip verification successful")

verify_answer_roundtrip(v1_data)
```

## Field Descriptions

| Field | Description |
|-------|-------------|
| `output` | Answer content array |
| `model` | Generation model (e.g., gpt-4, human) |
| `displayName` | Display name |
| `generatedBy` | Generator (ai/human) |
| `promptAnnotationId` | Linked prompt ID |

## Related Documentation

- [Prompt Conversion](./prompt-prompt.md) - Prompt annotations
