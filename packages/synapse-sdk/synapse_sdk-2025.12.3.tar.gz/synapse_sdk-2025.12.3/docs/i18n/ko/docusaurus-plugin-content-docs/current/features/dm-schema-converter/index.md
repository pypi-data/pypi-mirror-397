---
id: dm-schema-converter
title: DM Schema V1/V2 컨버터
sidebar_position: 1
---

# DM Schema V1/V2 컨버터

DM Schema V1과 V2 간의 양방향 변환을 수행하는 컨버터입니다.

## 개요

DM Schema 컨버터는 어노테이션 데이터를 V1과 V2 형식 간에 변환합니다:

- **V1 → V2**: 레거시 V1 데이터를 현대적인 V2 구조로 변환
- **V2 → V1**: V2 데이터를 V1 형식으로 역변환 (레거시 시스템 호환)

## 주요 특징

### 분리된 출력 구조

V1→V2 변환 시 결과가 두 부분으로 분리됩니다:

- **`annotation_data`**: V2 공통 어노테이션 구조 (id, classification, attrs, data)
- **`annotation_meta`**: V1 최상위 구조 유지 (메타 정보 보존)

이 분리 구조를 통해:
- `annotation_data`만으로 V2 공통 포맷 활용 가능
- `annotation_meta`와 결합하면 완전한 V1 복원 가능

### 지원 도구

| 도구 | V1 → V2 | V2 → V1 | 미디어 타입 | 비고 |
|------|---------|---------|-------------|------|
| `bounding_box` | ✅ | ✅ | image | rotation 보존 |
| `polygon` | ✅ | ✅ | image | 점 ID 자동 생성 |
| `polyline` | ✅ | ✅ | image | 점 ID 자동 생성 |
| `keypoint` | ✅ | ✅ | image | 단일 점 좌표 |
| `3d_bounding_box` | ✅ | ✅ | pcd | PSR 좌표계 |
| `segmentation` | ✅ | ✅ | image/video | 이미지: pixel_indices, 비디오: section |
| `3d_segmentation` | ✅ | ✅ | pcd | 포인트 인덱스 |
| `named_entity` | ✅ | ✅ | text | NER 태깅 |
| `classification` | ✅ | ✅ | image | 데이터 없음 (빈 객체) |
| `relation` | ✅ | ✅ | image/text | 어노테이션 간 관계 |
| `prompt` | ✅ | ✅ | prompt | 프롬프트 입력 |
| `answer` | ✅ | ✅ | prompt | 답변 출력 |

## 빠른 시작

### 설치

```bash
pip install synapse-sdk
```

### V1 → V2 변환

```python
from synapse_sdk.utils.converters.dm import convert_v1_to_v2

# V1 데이터
v1_data = {
    "annotations": {
        "image_1": [
            {
                "id": "ann_1",
                "tool": "bounding_box",
                "classification": {"class": "person"}
            }
        ]
    },
    "annotationsData": {
        "image_1": [
            {
                "id": "ann_1",
                "coordinate": {"x": 100, "y": 200, "width": 150, "height": 100}
            }
        ]
    }
}

# V2로 변환 (분리된 결과)
result = convert_v1_to_v2(v1_data)

annotation_data = result["annotation_data"]  # V2 공통 구조
annotation_meta = result["annotation_meta"]  # V1 최상위 구조
```

### V2 → V1 변환

```python
from synapse_sdk.utils.converters.dm import convert_v2_to_v1

# 완전한 변환 (annotation_data + annotation_meta)
v1_restored = convert_v2_to_v1(result)

# annotation_data만으로 변환 (기본값 사용)
v1_basic = convert_v2_to_v1({"annotation_data": annotation_data})
```

## 세부 가이드

### 이미지 도구
- [바운딩 박스 변환](./image-bounding-box.md) - 바운딩 박스 어노테이션 변환
- [폴리곤 변환](./image-polygon.md) - 폴리곤 어노테이션 변환
- [폴리라인 변환](./image-polyline.md) - 폴리라인 어노테이션 변환
- [키포인트 변환](./image-keypoint.md) - 키포인트 어노테이션 변환
- [세그멘테이션 변환 (이미지)](./image-segmentation.md) - 이미지 세그멘테이션 변환
- [분류 변환](./image-classification.md) - 분류 어노테이션 변환
- [관계 변환](./image-relation.md) - 어노테이션 간 관계 변환

### 비디오 도구
- [세그멘테이션 변환 (비디오)](./video-segmentation.md) - 비디오 세그멘테이션 변환

### PCD (포인트 클라우드) 도구
- [3D 바운딩 박스 변환](./pcd-3d-bounding-box.md) - 3D 바운딩 박스 변환
- [3D 세그멘테이션 변환](./pcd-3d-segmentation.md) - 3D 세그멘테이션 변환

### 텍스트 도구
- [개체명 인식 변환](./text-named-entity.md) - NER 어노테이션 변환

### 프롬프트 도구
- [프롬프트 변환](./prompt-prompt.md) - 프롬프트 어노테이션 변환
- [답변 변환](./prompt-answer.md) - 답변 어노테이션 변환

### 개발자 문서
- [개발자 가이드](./developer-guide.md) - 새 도구 추가 방법

## API 참조

### `convert_v1_to_v2(v1_data)`

V1 데이터를 V2 형식으로 변환합니다.

**파라미터:**
- `v1_data`: DM Schema V1 형식 데이터

**반환값:**
- `V2ConversionResult`: `annotation_data`와 `annotation_meta`를 포함하는 딕셔너리

### `convert_v2_to_v1(v2_data, annotation_meta=None)`

V2 데이터를 V1 형식으로 변환합니다.

**파라미터:**
- `v2_data`: DM Schema V2 형식 데이터 또는 V2ConversionResult
- `annotation_meta`: 별도 전달되는 V1 최상위 구조 (선택)

**반환값:**
- DM Schema V1 형식 데이터
