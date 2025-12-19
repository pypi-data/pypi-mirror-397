---
id: developer-guide
title: 개발자 가이드
sidebar_position: 4
---

# 개발자 가이드

새로운 어노테이션 도구 컨버터를 추가하는 방법을 설명합니다.

## 아키텍처 개요

DM Schema 컨버터는 확장 가능한 프로세서 패턴을 사용합니다:

```
synapse_sdk/utils/converters/dm/
├── __init__.py          # 공개 API
├── types.py             # TypedDict 정의
├── base.py              # BaseDMConverter 추상 클래스
├── from_v1.py           # DMV1ToV2Converter
├── to_v1.py             # DMV2ToV1Converter
├── utils.py             # 유틸리티 함수
└── tools/
    ├── __init__.py      # ToolProcessor Protocol
    ├── bounding_box.py  # BoundingBoxProcessor
    └── polygon.py       # PolygonProcessor
```

## ToolProcessor Protocol

새 도구 프로세서는 다음 Protocol을 구현해야 합니다:

```python
from typing import Any, Protocol

class ToolProcessor(Protocol):
    """도구별 변환 프로세서 프로토콜"""

    tool_name: str  # 도구 이름 (예: "bounding_box", "polygon")

    def to_v2(
        self,
        v1_annotation: dict[str, Any],
        v1_data: dict[str, Any]
    ) -> dict[str, Any]:
        """V1 어노테이션을 V2로 변환"""
        ...

    def to_v1(
        self,
        v2_annotation: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """V2 어노테이션을 V1으로 변환

        Returns:
            (V1 annotation, V1 annotationData) 튜플
        """
        ...
```

## 새 도구 프로세서 추가

### 1단계: 프로세서 클래스 생성

`synapse_sdk/utils/converters/dm/tools/` 디렉토리에 새 파일을 생성합니다.

예: `keypoint.py`

```python
"""키포인트 도구 프로세서"""

from typing import Any

from ..utils import generate_random_id


class KeypointProcessor:
    """키포인트 도구 프로세서

    V1 coordinate: {x, y}
    V2 data: [x, y]
    """

    tool_name = "keypoint"

    def to_v2(
        self,
        v1_annotation: dict[str, Any],
        v1_data: dict[str, Any]
    ) -> dict[str, Any]:
        """V1 키포인트를 V2로 변환"""
        coordinate = v1_data.get("coordinate", {})
        classification_obj = v1_annotation.get("classification") or {}

        # V2 data: [x, y]
        data = [
            coordinate.get("x", 0),
            coordinate.get("y", 0),
        ]

        # V2 attrs 구성
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
        """V2 키포인트를 V1으로 변환"""
        annotation_id = v2_annotation.get("id", "")
        classification_str = v2_annotation.get("classification", "")
        attrs = v2_annotation.get("attrs", [])
        data = v2_annotation.get("data", [0, 0])

        # V1 coordinate 구성
        coordinate = {
            "x": data[0] if len(data) > 0 else 0,
            "y": data[1] if len(data) > 1 else 0,
        }

        # V1 classification 구성
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

### 2단계: 프로세서 등록

`from_v1.py`와 `to_v1.py`의 `_setup_tool_processors()` 메서드에 등록합니다:

```python
def _setup_tool_processors(self) -> None:
    """도구별 프로세서 등록"""
    from .tools.bounding_box import BoundingBoxProcessor
    from .tools.polygon import PolygonProcessor
    from .tools.keypoint import KeypointProcessor  # 새로 추가

    self.register_processor(BoundingBoxProcessor())
    self.register_processor(PolygonProcessor())
    self.register_processor(KeypointProcessor())  # 새로 추가
```

### 3단계: 테스트 작성

`tests/utils/converters/dm/` 디렉토리에 테스트 파일을 생성합니다:

```python
"""키포인트 변환 테스트"""

import pytest

from synapse_sdk.utils.converters.dm import convert_v1_to_v2, convert_v2_to_v1


class TestV1ToV2Keypoint:
    """V1 → V2 키포인트 변환 테스트"""

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
        """기본 변환 테스트"""
        result = convert_v1_to_v2(v1_keypoint_sample)

        keypoint = result["annotation_data"]["images"][0]["keypoint"][0]
        assert keypoint["data"] == [100, 200]
        assert keypoint["classification"] == "joint"

    def test_roundtrip(self, v1_keypoint_sample):
        """라운드트립 테스트"""
        v2_result = convert_v1_to_v2(v1_keypoint_sample)
        v1_result = convert_v2_to_v1(v2_result)

        orig_coord = v1_keypoint_sample["annotationsData"]["image_1"][0]["coordinate"]
        rest_coord = v1_result["annotationsData"]["image_1"][0]["coordinate"]

        assert orig_coord["x"] == rest_coord["x"]
        assert orig_coord["y"] == rest_coord["y"]
```

## 런타임 프로세서 등록

컨버터 인스턴스에 동적으로 프로세서를 등록할 수도 있습니다:

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


# 커스텀 프로세서 등록
converter = DMV1ToV2Converter()
converter.register_processor(CustomProcessor())

# 변환 실행
result = converter.convert(v1_data_with_custom_tool)
```

## 유틸리티 함수

### `generate_random_id()`

고유한 랜덤 ID를 생성합니다:

```python
from synapse_sdk.utils.converters.dm.utils import generate_random_id

id1 = generate_random_id()  # 예: "Cd1qfFQFI4"
id2 = generate_random_id()  # 예: "AUjPgaMzQa"
```

### `extract_media_type_info(media_id)`

미디어 ID에서 타입 정보를 추출합니다:

```python
from synapse_sdk.utils.converters.dm.utils import extract_media_type_info

singular, plural = extract_media_type_info("image_1")
# singular: "image", plural: "images"

singular, plural = extract_media_type_info("video_5")
# singular: "video", plural: "videos"
```

## 타입 정의

주요 TypedDict 정의:

```python
from synapse_sdk.utils.converters.dm.types import (
    V2ConversionResult,  # V1→V2 변환 결과
    V2AnnotationData,    # V2 공통 어노테이션 구조
    AnnotationMeta,      # V1 최상위 구조
)
```

## 테스트 가이드라인

1. **TDD 접근**: 구현 전에 테스트를 먼저 작성합니다.
2. **라운드트립 검증**: V1→V2→V1 변환이 데이터를 보존하는지 확인합니다.
3. **엣지 케이스**: 빈 데이터, 누락된 필드 등을 테스트합니다.
4. **기존 테스트 영향 없음**: 새 프로세서 추가 후 기존 테스트가 여전히 통과하는지 확인합니다.

## AI 어시스턴트용 프롬프트 템플릿

새로운 도구 타입을 추가할 때 아래 프롬프트를 사용하여 AI 어시스턴트에게 구현을 요청할 수 있습니다.

### 프롬프트 템플릿

```markdown
# DM Schema Converter 새 도구 타입 추가 요청

## 도구 정보
- **도구 이름**: [도구 이름, 예: cuboid, ellipse, etc.]
- **미디어 타입**: [image / video / pcd / text / prompt]

## V1 데이터 구조

### annotations 구조
```json
{
  "id": "[어노테이션 ID]",
  "tool": "[도구 이름]",
  "classification": {
    "class": "[클래스명]",
    "[추가 속성]": "[값]"
  }
}
```

### annotationsData 구조
```json
{
  "id": "[어노테이션 ID]",
  "[데이터 필드명]": {
    // V1 좌표/데이터 구조
  }
}
```

## V2 데이터 구조 (희망하는 형태)
```json
{
  "id": "[어노테이션 ID]",
  "classification": "[클래스명]",
  "attrs": [{"name": "[속성명]", "value": "[값]"}],
  "data": [
    // V2 좌표/데이터 구조 (배열 또는 객체)
  ]
}
```

## 변환 규칙
- V1 `[필드명]` → V2 `data.[필드명]`
- V1 `classification.class` → V2 `classification`
- V1 `classification.[기타]` → V2 `attrs[{name, value}]`

## 예시 데이터

### V1 예시
```json
// 실제 V1 데이터 예시
```

### V2 예시 (변환 후)
```json
// 실제 V2 데이터 예시
```

## 요청사항
1. `synapse_sdk/utils/converters/dm/tools/[도구명].py` 프로세서 생성
2. `from_v1.py`, `to_v1.py`에 프로세서 등록
3. `tests/utils/converters/dm/test_[도구명].py` 테스트 생성
4. (선택) `docs/docs/features/dm-schema-converter/[미디어]-[도구명].md` 문서 생성
```

### 사용 예시

아래는 실제 사용 예시입니다:

```markdown
# DM Schema Converter 새 도구 타입 추가 요청

## 도구 정보
- **도구 이름**: ellipse
- **미디어 타입**: image

## V1 데이터 구조

### annotations 구조
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

### annotationsData 구조
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

## V2 데이터 구조 (희망하는 형태)
```json
{
  "id": "ellipse_1",
  "classification": "defect",
  "attrs": [{"name": "severity", "value": "high"}],
  "data": [100, 200, 50, 30, 45]
}
```

## 변환 규칙
- V1 `coordinate.cx` → V2 `data[0]`
- V1 `coordinate.cy` → V2 `data[1]`
- V1 `coordinate.rx` → V2 `data[2]`
- V1 `coordinate.ry` → V2 `data[3]`
- V1 `coordinate.rotation` → V2 `data[4]`

## 요청사항
1. EllipseProcessor 프로세서 생성
2. 컨버터에 프로세서 등록
3. 테스트 케이스 작성
4. 문서 생성
```

### 체크리스트

새 도구 타입 추가 시 확인해야 할 사항:

- [ ] `tools/[도구명].py` 프로세서 파일 생성
- [ ] `ToolProcessor` Protocol 구현 (`tool_name`, `to_v2`, `to_v1`)
- [ ] `from_v1.py`의 `_setup_tool_processors()`에 등록
- [ ] `to_v1.py`의 `_setup_tool_processors()`에 등록
- [ ] `tools/__init__.py`에 export 추가
- [ ] `tests/utils/converters/dm/test_[도구명].py` 테스트 작성
- [ ] V1→V2 변환 테스트
- [ ] V2→V1 변환 테스트
- [ ] 라운드트립 테스트 (V1→V2→V1)
- [ ] 기존 테스트 통과 확인 (`pytest tests/utils/converters/dm/`)
- [ ] (선택) 문서 작성 및 sidebars.ts 업데이트
