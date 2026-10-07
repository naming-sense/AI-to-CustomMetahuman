# AI to Custom MetaHuman

커스텀 얼굴 메시의 표면·UV를 유지하면서 MetaHuman의 스키닝, 표정 보정, DNA와 RigLogic을 적용한 구현 기록입니다.

## 구현 문서

[커스텀 토폴로지에 MetaHuman DNA·스키닝·RigLogic 적용하기](docs/HeadP2_CustomTopology_MetaHuman_Rig_Implementation.md)

Blender 5.2.2 LTS와 Unreal Engine 5.7.4에서 작업한 P2 얼굴을 기준으로 전달 계산식, 실행 순서, 실패 원인과 해결 방법, 검증 결과를 설명합니다. 눈 주변 연결 수정과 별도 안구 사용은 원본 보존 조건에서 허용한 예외입니다.

## 저장소 구성

- `docs/`: 상세 구현 문서와 표정 검수 화면
- `tools/`: 실제 작업에서 사용한 Python 스크립트
- `verification/`: 채널 대응표와 검증 결과

## 재현 전 준비

Character DNA 애드온, 사용 가능한 MetaHuman donor DNA, 커스텀 원본 메시, Unreal 프로젝트를 별도로 준비해야 합니다. 이 저장소에는 모델·DNA·플러그인 바이너리가 포함되지 않습니다.

스크립트에는 모델별 좌표, 오브젝트 이름과 예시 절대 경로가 들어 있습니다. 문서의 실행 순서와 입력 파일 조건을 먼저 확인하고, 별도 작업 폴더에서 경로를 수정해 사용하세요. 다른 얼굴에는 대응 영역과 fitting 파라미터를 다시 맞춰야 합니다.

문서와 기존 검증 기록을 공개한 저장소이며, 임의의 모델을 자동 리깅하는 완제품은 아닙니다. 검수 이미지는 Unlit 텍스처 확인 화면으로, 실제 레벨의 조명 결과와 구분합니다.
