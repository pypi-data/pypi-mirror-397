---
id: prompt-prompt
title: Prompt Conversion
sidebar_position: 13
---

# Prompt Conversion

A guide for bidirectional V1/V2 conversion of prompt annotations.

## Data Structure

### V1 Structure

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

### V2 Structure

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

## Conversion Rules

### V1 → V2

| V1 Field | V2 Field |
|----------|----------|
| `input` | `data.input` |
| `model` | `data.model` (if present) |
| `displayName` | `data.displayName` (if present) |
| `generatedBy` | `data.generatedBy` (if present) |
| `classification.class` | `classification` |
| `classification.{other}` | `attrs[{name, value}]` |

### V2 → V1

| V2 Field | V1 Field |
|----------|----------|
| `data.input` | `input` |
| `data.model` | `model` |
| `data.displayName` | `displayName` |
| `data.generatedBy` | `generatedBy` |
| `classification` | `classification.class` |
| `attrs[{name, value}]` | `classification.{name: value}` |

## Usage Examples

### Basic Conversion

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1

# V1 prompt data
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

# Convert to V2
result = convert_v1_to_v2(v1_data)
annotation_data = result["annotation_data"]

# Check V2 result
prompt = annotation_data["prompts"][0]["prompt"][0]
print(prompt["data"]["input"])  # [{"type": "text", "value": "What is shown in this image?", ...}]
print(prompt["classification"])  # "question"
```

### Multiple Input Processing

```python
# Prompt with multiple inputs
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

# Convert to V2
result = convert_v1_to_v2(v1_multi_input)
prompt = result["annotation_data"]["prompts"][0]["prompt"][0]

for inp in prompt["data"]["input"]:
    print(f"Type: {inp['type']}, Value: {inp['value']}")
```

### Roundtrip Verification

```python
def verify_prompt_roundtrip(v1_original):
    """Verify prompt roundtrip"""
    # V1 → V2 → V1
    v2_result = convert_v1_to_v2(v1_original)
    v1_restored = convert_v2_to_v1(v2_result)

    # Compare inputs
    orig_input = v1_original["annotationsData"]["prompt_1"][0]["input"]
    rest_input = v1_restored["annotationsData"]["prompt_1"][0]["input"]

    assert orig_input == rest_input

    print("Prompt roundtrip verification successful")

verify_prompt_roundtrip(v1_data)
```

## Related Documentation

- [Answer Conversion](./prompt-answer.md) - Answer annotations for prompts
