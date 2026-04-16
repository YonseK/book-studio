# BookStudio

HTML 기반 프레젠테이션/문서 에디터 엔진.
PPTX를 대체하는 독립 Django 앱 + React 컴포넌트 라이브러리.

## 설치

### 백엔드 (Django)

```bash
pip install git+ssh://git@github.com/YonseK/book-studio.git#subdirectory=backend
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'bookstudio',
]

# 선택: 기본 레이아웃, 스토리지 백엔드
BOOKSTUDIO_DEFAULT_LAYOUT = "PPTX_WIDE"
BOOKSTUDIO_STORAGE_BACKEND = "storages.backends.s3boto3.S3Boto3Storage"
```

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('api/studio/', include('bookstudio.api.urls')),
]
```

```bash
python manage.py migrate
```

### 프론트엔드 (React)

```bash
npm install git+ssh://git@github.com/YonseK/book-studio.git#subdirectory=frontend
```

```tsx
import { BookStudioEditor, restClient } from '@bookstudio/react'

const client = restClient({ baseURL: '/api/studio' })

function App() {
  return (
    <BookStudioEditor
      client={client}
      bookId="your-book-id"
      defaultLayout="PPTX_WIDE"
    />
  )
}
```

## 통합 예제

### AIONETRA (기업 운영체제)

```python
# backend/settings.py
BOOKSTUDIO_DEFAULT_LAYOUT = "PPTX_WIDE"  # 16:9 프레젠테이션
```

```tsx
<BookStudioEditor
  client={client}
  bookId={projectDocId}
  defaultLayout="PPTX_WIDE"
/>
```

### KBOOKOOROO (케이팝 팬덤)

```python
# backend/settings.py
BOOKSTUDIO_DEFAULT_LAYOUT = "A4_PORTRAIT"  # A4 팬진
```

```tsx
<BookStudioEditor
  client={client}
  bookId={fanzineId}
  defaultLayout="BOOK"
/>
```

## 레이아웃 프리셋

| 프리셋 | 크기 | 용도 |
|--------|------|------|
| `PPTX_WIDE` | 1280×720 (16:9) | 프레젠테이션 기본 |
| `PPTX_STD` | 960×720 (4:3) | 클래식 프레젠테이션 |
| `BOOK` | 768×1086 (A4) | 문서/책 |
| `MBOOK` | 768×960 (4:5) | 미니북 |
| `CD` | 768×768 (1:1) | 정사각/인스타 |
| `CARD` | 768×552 | 카드/명함 |
| `CINEMA` | 768×432 (16:9) | 시네마 |
| `CUSTOM` | 사용자 지정 | 자유 비율 |

## API 엔드포인트

| 경로 | 설명 |
|------|------|
| `books/` | 북 CRUD + clone + publish |
| `books/{id}/editions/` | 에디션 관리 |
| `books/{id}/editions/{id}/pages/` | 페이지 CRUD + sort |
| `pages/{id}/panels/` | 패널 CRUD + sort |
| `photos/`, `wallpapers/` | 이미지 업로드 |
| `import/html/` | HTML → 페이지 변환 |
| `export/html/page/{id}/` | 페이지 → HTML |
| `export/pdf/page/{id}/` | 페이지 → PDF |

## 개발

```bash
# 백엔드 테스트
cd backend && pip install -e ".[dev]" && pytest

# 프론트엔드 타입 체크
cd frontend && npm install && npm run typecheck

# 프론트엔드 빌드
cd frontend && npm run build
```

## 라이선스

MIT
