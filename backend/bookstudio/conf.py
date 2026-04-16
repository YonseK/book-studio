from django.conf import settings

# 기본 레이아웃 프리셋
DEFAULT_LAYOUT = getattr(settings, "BOOKSTUDIO_DEFAULT_LAYOUT", "PPTX_WIDE")

# 파일 스토리지 백엔드
STORAGE_BACKEND = getattr(settings, "BOOKSTUDIO_STORAGE_BACKEND", "django.core.files.storage.FileSystemStorage")

# 이미지 리사이즈 설정
IMAGE_MAX_WIDTH = getattr(settings, "BOOKSTUDIO_IMAGE_MAX_WIDTH", 1152)
IMAGE_PREVIEW_WIDTH = getattr(settings, "BOOKSTUDIO_IMAGE_PREVIEW_WIDTH", 840)
IMAGE_THUMB_WIDTH = getattr(settings, "BOOKSTUDIO_IMAGE_THUMB_WIDTH", 300)
IMAGE_MIN_WIDTH = getattr(settings, "BOOKSTUDIO_IMAGE_MIN_WIDTH", 120)

# 월페이퍼 기본 너비
WALLPAPER_PAD_WIDTH = getattr(settings, "BOOKSTUDIO_WALLPAPER_PAD_WIDTH", 768)

# 초대 링크 만료 기간 (일)
INVITATION_EXPIRE_DAYS = getattr(settings, "BOOKSTUDIO_INVITATION_EXPIRE_DAYS", 7)

# HMAC Salt
SALT = getattr(settings, "BOOKSTUDIO_HMAC_SALT", "bookstudio-invitation")

# User 모델
USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")
