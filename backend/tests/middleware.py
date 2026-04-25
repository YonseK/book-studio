from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication


class AutoLoginMiddleware:
    """개발 서버 전용: 모든 요청을 dev 유저로 자동 인증."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            User = get_user_model()
            user, _ = User.objects.get_or_create(
                username="dev",
                defaults={"is_staff": True, "is_superuser": True},
            )
            request.user = user
        return self.get_response(request)


class NoCsrfSessionAuthentication(SessionAuthentication):
    """개발 서버 전용: CSRF 검사를 건너뛰는 SessionAuthentication."""

    def enforce_csrf(self, request):
        pass
