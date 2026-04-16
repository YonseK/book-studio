import uuid


def uuid_key():
    """UUID4 기반 키 생성 (하이픈 제거)."""
    return uuid.uuid4().hex


def short_key():
    """짧은 키 생성 (UUID4 앞 8자)."""
    return uuid.uuid4().hex[:8]
