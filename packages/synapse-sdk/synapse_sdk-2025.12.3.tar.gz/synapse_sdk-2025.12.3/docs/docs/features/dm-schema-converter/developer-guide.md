---
id: developer-guide
title: Developer Guide
sidebar_position: 4
---

# Developer Guide

Learn how to add new annotation tool converters.

## Architecture Overview

The DM Schema Converter uses an extensible processor pattern:

```
synapse_sdk/utils/converters/dm/
├── __init__.py          # Public API
├── types.py             # TypedDict definitions
├── base.py              # BaseDMConverter abstract class
├── from_v1.py           # DMV1ToV2Converter
├── to_v1.py             # DMV2ToV1Converter
├── utils.py             # Utility functions
└── tools/
    ├── __init__.py      # ToolProcessor Protocol
    ├── bounding_box.py  # BoundingBoxProcessor
    └── polygon.py       # PolygonProcessor
```

## ToolProcessor Protocol

New tool processors must implement this Protocol:

```python
from typing import Any, Protocol

class ToolProcessor(Protocol):
    """Tool-specific conversion processor protocol"""

    tool_name: str  # Tool name (e.g., "bounding_box", "polygon")

    def to_v2(
        self,
        v1_annotation: dict[str, Any],
        v1_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert V1 annotation to V2"""
        ...

    def to_v1(
        self,
        v2_annotation: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Convert V2 annotation to V1

        Returns:
            (V1 annotation, V1 annotationData) tuple
        """
        ...
```

## Adding a New Tool Processor

### Step 1: Create the Processor Class

Create a new file in `synapse_sdk/utils/converters/dm/tools/`.

Example: `keypoint.py`

```python
"""Keypoint tool processor"""

from typing import Any

from ..utils import generate_random_id


class KeypointProcessor:
    """Keypoint tool processor

    V1 coordinate: {x, y}
    V2 data: [x, y]
    """

    tool_name = "keypoint"

    def to_v2(
        self,
        v1_annotation: dict[str, Any],
        v1_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert V1 keypoint to V2"""
        coordinate = v1_data.get("coordinate", {})
        classification_obj = v1_annotation.get("classification") or {}

        # V2 data: [x, y]
        data = [
            coordinate.get("x", 0),
            coordinate.get("y", 0),
        ]

        # Build V2 attrs
        attrs: list[dict[str, Any]] = []
        for key, value in classification_obj.items():
            if key != "class":
                attrs.append({"name": key, "value": value})

        return {
            "id": v1_annotation.get("id", ""),
            "classification": classification_obj.get("class", ""),
            "attrs": attrs,
            "data": data,
        }

    def to_v1(
        self,
        v2_annotation: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Convert V2 keypoint to V1"""
        annotation_id = v2_annotation.get("id", "")
        classification_str = v2_annotation.get("classification", "")
        attrs = v2_annotation.get("attrs", [])
        data = v2_annotation.get("data", [0, 0])

        # Build V1 coordinate
        coordinate = {
            "x": data[0] if len(data) > 0 else 0,
            "y": data[1] if len(data) > 1 else 0,
        }

        # Build V1 classification
        classification: dict[str, Any] = {"class": classification_str}
        for attr in attrs:
            name = attr.get("name", "")
            value = attr.get("value")
            if not name.startswith("_"):
                classification[name] = value

        v1_annotation = {
            "id": annotation_id,
            "tool": self.tool_name,
            "classification": classification,
        }

        v1_data = {
            "id": annotation_id,
            "coordinate": coordinate,
        }

        return v1_annotation, v1_data
```

### Step 2: Register the Processor

Add registration to `_setup_tool_processors()` in `from_v1.py` and `to_v1.py`:

```python
def _setup_tool_processors(self) -> None:
    """Register tool processors"""
    from .tools.bounding_box import BoundingBoxProcessor
    from .tools.polygon import PolygonProcessor
    from .tools.keypoint import KeypointProcessor  # New

    self.register_processor(BoundingBoxProcessor())
    self.register_processor(PolygonProcessor())
    self.register_processor(KeypointProcessor())  # New
```

### Step 3: Write Tests

Create a test file in `tests/utils/converters/dm/`:

```python
"""Keypoint conversion tests"""

import pytest

from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1


class TestV1ToV2Keypoint:
    """V1 → V2 keypoint conversion tests"""

    @pytest.fixture
    def v1_keypoint_sample(self):
        return {
            "annotations": {
                "image_1": [
                    {
                        "id": "kp_1",
                        "tool": "keypoint",
                        "classification": {"class": "joint"}
                    }
                ]
            },
            "annotationsData": {
                "image_1": [
                    {
                        "id": "kp_1",
                        "coordinate": {"x": 100, "y": 200}
                    }
                ]
            }
        }

    def test_basic_conversion(self, v1_keypoint_sample):
        """Basic conversion test"""
        result = convert_v1_to_v2(v1_keypoint_sample)

        keypoint = result["annotation_data"]["images"][0]["keypoint"][0]
        assert keypoint["data"] == [100, 200]
        assert keypoint["classification"] == "joint"

    def test_roundtrip(self, v1_keypoint_sample):
        """Roundtrip test"""
        v2_result = convert_v1_to_v2(v1_keypoint_sample)
        v1_result = convert_v2_to_v1(v2_result)

        orig_coord = v1_keypoint_sample["annotationsData"]["image_1"][0]["coordinate"]
        rest_coord = v1_result["annotationsData"]["image_1"][0]["coordinate"]

        assert orig_coord["x"] == rest_coord["x"]
        assert orig_coord["y"] == rest_coord["y"]
```

## Runtime Processor Registration

You can also register processors dynamically at runtime:

```python
from synapse_sdk.utils.converters.dm.from_v1 import DMV1ToV2Converter


class CustomProcessor:
    tool_name = "custom_tool"

    def to_v2(self, v1_annotation, v1_data):
        return {
            "id": v1_annotation.get("id", ""),
            "classification": v1_annotation.get("classification", {}).get("class", ""),
            "attrs": [],
            "data": v1_data.get("custom_data", {}),
        }

    def to_v1(self, v2_annotation):
        return (
            {
                "id": v2_annotation.get("id", ""),
                "tool": self.tool_name,
                "classification": {"class": v2_annotation.get("classification", "")},
            },
            {
                "id": v2_annotation.get("id", ""),
                "custom_data": v2_annotation.get("data", {}),
            },
        )


# Register custom processor
converter = DMV1ToV2Converter()
converter.register_processor(CustomProcessor())

# Run conversion
result = converter.convert(v1_data_with_custom_tool)
```

## Utility Functions

### `generate_random_id()`

Generates a unique random ID:

```python
from synapse_sdk.utils.converters.dm.utils import generate_random_id

id1 = generate_random_id()  # e.g., "Cd1qfFQFI4"
id2 = generate_random_id()  # e.g., "AUjPgaMzQa"
```

## Testing Guidelines

1. **TDD Approach**: Write tests before implementation.
2. **Roundtrip Verification**: Verify V1→V2→V1 conversion preserves data.
3. **Edge Cases**: Test empty data, missing fields, etc.
4. **No Impact on Existing Tests**: Ensure existing tests still pass after adding new processors.

## AI Assistant Prompt Template

Use the following prompt template to request AI assistants to implement new tool types.

### Prompt Template

```markdown
# DM Schema Converter New Tool Type Request

## Tool Information
- **Tool Name**: [tool name, e.g., cuboid, ellipse, etc.]
- **Media Type**: [image / video / pcd / text / prompt]

## V1 Data Structure

### annotations structure
```json
{
  "id": "[annotation ID]",
  "tool": "[tool name]",
  "classification": {
    "class": "[class name]",
    "[additional attribute]": "[value]"
  }
}
```

### annotationsData structure
```json
{
  "id": "[annotation ID]",
  "[data field name]": {
    // V1 coordinate/data structure
  }
}
```

## V2 Data Structure (desired format)
```json
{
  "id": "[annotation ID]",
  "classification": "[class name]",
  "attrs": [{"name": "[attribute name]", "value": "[value]"}],
  "data": [
    // V2 coordinate/data structure (array or object)
  ]
}
```

## Conversion Rules
- V1 `[field name]` → V2 `data.[field name]`
- V1 `classification.class` → V2 `classification`
- V1 `classification.[other]` → V2 `attrs[{name, value}]`

## Example Data

### V1 Example
```json
// Actual V1 data example
```

### V2 Example (after conversion)
```json
// Actual V2 data example
```

## Requirements
1. Create `synapse_sdk/utils/converters/dm/tools/[tool_name].py` processor
2. Register processor in `from_v1.py`, `to_v1.py`
3. Create `tests/utils/converters/dm/test_[tool_name].py` tests
4. (Optional) Create `docs/docs/features/dm-schema-converter/[media]-[tool_name].md` documentation
```

### Usage Example

Here is a practical example:

```markdown
# DM Schema Converter New Tool Type Request

## Tool Information
- **Tool Name**: ellipse
- **Media Type**: image

## V1 Data Structure

### annotations structure
```json
{
  "id": "ellipse_1",
  "tool": "ellipse",
  "classification": {
    "class": "defect",
    "severity": "high"
  }
}
```

### annotationsData structure
```json
{
  "id": "ellipse_1",
  "coordinate": {
    "cx": 100,
    "cy": 200,
    "rx": 50,
    "ry": 30,
    "rotation": 45
  }
}
```

## V2 Data Structure (desired format)
```json
{
  "id": "ellipse_1",
  "classification": "defect",
  "attrs": [{"name": "severity", "value": "high"}],
  "data": [100, 200, 50, 30, 45]
}
```

## Conversion Rules
- V1 `coordinate.cx` → V2 `data[0]`
- V1 `coordinate.cy` → V2 `data[1]`
- V1 `coordinate.rx` → V2 `data[2]`
- V1 `coordinate.ry` → V2 `data[3]`
- V1 `coordinate.rotation` → V2 `data[4]`

## Requirements
1. Create EllipseProcessor
2. Register processor in converters
3. Write test cases
4. Create documentation
```

### Checklist

Items to verify when adding a new tool type:

- [ ] Create `tools/[tool_name].py` processor file
- [ ] Implement `ToolProcessor` Protocol (`tool_name`, `to_v2`, `to_v1`)
- [ ] Register in `from_v1.py`'s `_setup_tool_processors()`
- [ ] Register in `to_v1.py`'s `_setup_tool_processors()`
- [ ] Add export in `tools/__init__.py`
- [ ] Write `tests/utils/converters/dm/test_[tool_name].py` tests
- [ ] V1→V2 conversion tests
- [ ] V2→V1 conversion tests
- [ ] Roundtrip tests (V1→V2→V1)
- [ ] Verify all existing tests pass (`pytest tests/utils/converters/dm/`)
- [ ] (Optional) Write documentation and update sidebars.ts
