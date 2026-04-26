# BookStudio 문서 인덱스

## design/

| 문서 | 설명 |
|------|------|
| [frontend-ui-spec.md](design/frontend-ui-spec.md) | 프론트엔드 UI 설계 명세서 — 원본 에디터 UI 완벽 재현을 위한 컴포넌트, 레이아웃, 컬러, 상호작용 상세 스펙 |
| [frontend-reinforcement.md](design/frontend-reinforcement.md) | 프론트엔드 보강 설계서 — 원본 Vue2 분석 기반 버그 수정, 기능 보강, 디자인 재현 (7단계) |
| [css-restoration.md](design/css-restoration.md) | CSS 디자인 복원 설계서 — 원본 Vue2 CSS를 React에 정밀 복원 (색상, 레이아웃, 핸들, 컨트롤, 폰트) |
| [backend-model-review.md](design/backend-model-review.md) | 백엔드 모델 점검 보고서 — 구조, 누락, 모순, 버그 분석 (10건, 수정 완료) |
| [auto-save.md](design/auto-save.md) | 디바운스 자동 저장 설계서 — 카테고리별 디바운스, dirty tracking, 재시도, 협업 연동 |
| [ai-integration-proposal.md](design/ai-integration-proposal.md) | AI 통합 구현 기획서 — 기획/콘텐츠/디자인 자동 생성 파이프라인, 디자인 패턴 시스템, SSE 스트리밍, LLM Adapter |
| [ai-phase1-design-pattern-system.md](design/ai-phase1-design-pattern-system.md) | Phase 1 상세 설계서 — DesignPattern/Slot/Set 모델, PatternApplicator 서비스, 레거시 추출 커맨드, 큐레이션 패턴 15개, API |
| [ai-phase2-pipeline.md](design/ai-phase2-pipeline.md) | Phase 2 상세 설계서 — AISession 모델, LLM Adapter, Planner/Writer/Designer/Orchestrator 서비스, Celery+Redis+SSE 스트리밍, 프롬프트 설계 |
| [ai-phase3-frontend.md](design/ai-phase3-frontend.md) | Phase 3 상세 설계서 — aiStore, AIChatPanel 컴포넌트, useAISession SSE 훅, 에디터 캔버스 실시간 반영, CSS |
