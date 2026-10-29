# WAFER MAP | CNN 기반 반도체 웨이퍼 불량 패턴 분석

**신도윤 | 가천대학교 산업공학과 · InFact 교내 학회 프로젝트 맥락**  
원본 프로젝트: **2026.10.05** · GitHub 포트폴리오 정리: **2026.10.29**

![웨이퍼 결함 분석 프로젝트 시각적 소개](assets/hero_wafer_inspector.png)

[상세 국·영문 README](README.md) · [InFact 활동 배경](docs/INFACT_ACTIVITY.md) · [기술 설계](docs/TECHNICAL_DEEP_DIVE.md) · [국문 연구보고서](docs/PROJECT_REPORT_KR.md)

## 1. 이 프로젝트에서 해결하려던 문제

웨이퍼 테스트 후 발생한 불량 다이의 **개수만으로는 결함 형태를 구분할 수 없다**. 52×52 Wafer Map에 기록된 공간적 패턴을 CNN이 학습해 정상 및 단일결함 8개 유형으로 분류하고, 검사자는 웹 화면에서 각 다이의 PASS/FAIL 상태와 좌표를 확인하도록 설계했다. SEM의 광학/전자현미경 원본 이미지를 분석하는 프로젝트가 아니다.

![실제 웨이퍼 맵 9종 예시](assets/wafer_class_atlas.png)

## 2. 어떤 기술을 사용했는가?

| 구분 | 기술 | 실제 수행 역할 |
|---|---|---|
| 데이터 분석 | Python / NumPy | NPZ 입력, 샘플 선별, 결함 라벨 변환 및 검증 |
| 딥러닝 | TensorFlow / Keras | Conv2D 3단계, MaxPooling, 9-class Softmax |
| 실험 설계 | scikit-learn | 층화 분할, 클래스 불균형 가중치, 성능 지표 계산 코드 |
| API 서버 | Flask | 원본 샘플, 라벨, 다이 비율, 조건부 예측 결과 제공 |
| UI | HTML / CSS / JavaScript Canvas | 52×52 다이 표시, 좌표 Hover, 웨이퍼 선택 |
| 데이터 품질 | 자체 검증 모듈 | 설명되지 않은 값 `3`을 가진 105개 지도 격리 |
| 재현성 | pytest / GitHub Actions | 전처리 기능 3개 테스트, 실행 환경 문서화 |

![실제 데이터 품질 검증 그래프](assets/figures/dataset_filtering.png)

**원본 38,015개 → 단일라벨 대상 8,015개 → 검증 완료 7,910개**. 원본 설명서에 없는 다이 값 `3`을 가진 105개는 분류에서 제외했다. 이 수치는 **모델 정확도가 아니라 데이터 검증 결과**다.

![실제 구현을 바탕으로 시각화한 CNN 모형 구조](assets/diagrams/cnn_architecture.svg)

## 3. 인터페이스

| Edge-Ring 원본 데이터 | Center 원본 데이터 |
|:--:|:--:|
| ![HTML Canvas Edge Ring 실제 렌더링 캡처](assets/screenshots/actual_template_dataset_preview_edge_ring.png) | ![HTML Canvas Center 실제 렌더링 캡처](assets/screenshots/actual_template_dataset_preview_center.png) |

위 사진은 **기존 HTML Canvas 템플릿에 실제 데이터셋의 웨이퍼 샘플을 연결해 브라우저에서 렌더링한 화면**입니다. Flask/TensorFlow의 실시간 추론 결과는 아니며, 모델이 없을 때 미학습 상태를 그대로 표시합니다. Accuracy·Macro-F1은 최종 학습 기록이 확인되지 않아 게시하지 않습니다.

## 4. InFact 교내 학회 프로젝트

| 학회 Instagram 계정 캡처 | 프로젝트 중간발표 공지 캡처 |
|:--:|:--:|
| ![InFact 학회 공식 프로필 캡처](assets/screenshots/infact_official_profile_crop.jpg) | ![InFact 중간발표 원본 공지 캡처](assets/screenshots/infact_midterm_notice_crop.jpg) |

활동 안내의 맥락을 설명하는 **원본 제공 캡처**입니다. 학회 소속, 발표 예정 일정의 자료이며 참석·수상 증빙으로 해석하지 않습니다.

**예정된 발표**: 2026년 10월 30일(금) 18:30, 비전타워 318호, 발표 10분 이내. 10월 29일 현재 발표 전이므로 참석 또는 완료·수상 사실을 기재하지 않는다. 이 자료는 학회 프로젝트의 **기술 산출물과 진행 맥락**을 기록하기 위한 것이다.

## 5. 실행과 해석

원본 공개 데이터셋을 합법적으로 확보한 다음:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:WAFER_DATA_PATH = 'C:\path\to\Wafer_Map_Datasets.npz'
python train_cnn.py --epochs 20 --seed 42
python app.py
```

브라우저 `http://127.0.0.1:5000`에서 로컬 검사 화면을 볼 수 있다. 원본 데이터 ZIP(약 412MB NPZ)과 학습된 가중치는 저장소에 포함하지 않았다.

**산업공학적 의미**: 품질 데이터를 올바르게 검증하고, 결함의 분포를 분류하며, 관측값과 추정값을 구별하는 **검사·분석 의사결정 지원의 출발점**이다. 아직 실제 제조공정의 원인 규명, 성능 인증, 생산라인 수율 개선 효과를 입증한 단계는 아니다.

- [한국어 기술보고서 (Markdown)](docs/PROJECT_REPORT_KR.md)
- [영어 기술 상세보고서](docs/TECHNICAL_DEEP_DIVE.md)
- [코드 및 모델 기술 설명](docs/TECHNICAL_DEEP_DIVE.md)
- [검증 / 미검증 항목](docs/VERIFICATION_STATUS.md)

## 6. 원본 데이터와 연구보고서 이미지

| Normal | Center | Donut |
|:--:|:--:|:--:|
| ![Normal](assets/gallery/normal.png) | ![Center](assets/gallery/center.png) | ![Donut](assets/gallery/donut.png) |
| Edge-Loc | Edge-Ring | Loc |
| ![Edge-Loc](assets/gallery/edge_loc.png) | ![Edge-Ring](assets/gallery/edge_ring.png) | ![Loc](assets/gallery/loc.png) |
| Near-Full | Scratch | Random |
| ![Near-Full](assets/gallery/near_full.png) | ![Scratch](assets/gallery/scratch.png) | ![Random](assets/gallery/random.png) |

| 원본 보고서 표지 | 데이터 분석 | CNN 기술 설명 |
|:--:|:--:|:--:|
| ![표지](assets/gallery/report_page_01.jpg) | ![데이터 페이지](assets/gallery/report_page_03.jpg) | ![CNN 페이지](assets/gallery/report_page_06.jpg) |

모든 웨이퍼 사진은 원본 데이터 기반 시각화이며 CNN 예측 정확도나 실제 공정 수율 개선 실적을 나타내지 않습니다.
