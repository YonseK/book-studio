"""WebSocket Consumer (Django Channels).

실시간 편집 동기화를 위한 consumer.
소비 프로젝트에서 Django Channels가 설치되어 있을 때만 활성화.

사용법 (소비 프로젝트 routing.py):
    from bookstudio.consumers import BookStudioConsumer

    websocket_urlpatterns = [
        re_path(r"ws/studio/(?P<book_id>\\w+)/$", BookStudioConsumer.as_asgi()),
    ]
"""

import json
from typing import Optional

try:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
    from channels.db import database_sync_to_async

    HAS_CHANNELS = True
except ImportError:
    HAS_CHANNELS = False


if HAS_CHANNELS:

    class BookStudioConsumer(AsyncJsonWebsocketConsumer):
        """북 에디터 실시간 동기화 consumer.

        그룹: book_{book_id}
        메시지 타입:
        - page.update: 페이지 변경 알림
        - panel.update: 패널 변경 알림
        - panel.move: 패널 이동 (위치/크기)
        - panel.create: 패널 생성
        - panel.delete: 패널 삭제
        - page.create: 페이지 생성
        - page.delete: 페이지 삭제
        - page.sort: 페이지 순서 변경
        - cursor.move: 커서 위치 공유 (협업)
        - user.join: 사용자 접속
        - user.leave: 사용자 퇴장
        """

        async def connect(self):
            self.book_id = self.scope["url_route"]["kwargs"]["book_id"]
            self.group_name = f"book_{self.book_id}"
            self.user = self.scope.get("user")

            if not self.user or self.user.is_anonymous:
                await self.close()
                return

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # 접속 알림
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "user.join",
                    "user_id": str(self.user.pk),
                    "username": self.user.get_username(),
                },
            )

        async def disconnect(self, close_code):
            if hasattr(self, "group_name"):
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "user.leave",
                        "user_id": str(self.user.pk),
                        "username": self.user.get_username(),
                    },
                )
                await self.channel_layer.group_discard(
                    self.group_name, self.channel_name
                )

        async def receive_json(self, content, **kwargs):
            """클라이언트 → 서버 메시지 수신 후 그룹에 브로드캐스트."""
            msg_type = content.get("type")
            if not msg_type:
                return

            # 발신자 정보 추가
            content["sender_id"] = str(self.user.pk)
            content["sender_name"] = self.user.get_username()

            await self.channel_layer.group_send(self.group_name, content)

        # ─── 이벤트 핸들러 ───

        async def page_update(self, event):
            await self._broadcast_except_sender(event)

        async def panel_update(self, event):
            await self._broadcast_except_sender(event)

        async def panel_move(self, event):
            await self._broadcast_except_sender(event)

        async def panel_create(self, event):
            await self._broadcast_except_sender(event)

        async def panel_delete(self, event):
            await self._broadcast_except_sender(event)

        async def page_create(self, event):
            await self._broadcast_except_sender(event)

        async def page_delete(self, event):
            await self._broadcast_except_sender(event)

        async def page_sort(self, event):
            await self._broadcast_except_sender(event)

        async def cursor_move(self, event):
            await self._broadcast_except_sender(event)

        async def user_join(self, event):
            await self.send_json(event)

        async def user_leave(self, event):
            await self.send_json(event)

        async def _broadcast_except_sender(self, event):
            """발신자를 제외하고 메시지 전송."""
            sender_id = event.get("sender_id")
            if sender_id != str(self.user.pk):
                await self.send_json(event)

else:
    # channels 미설치 시 placeholder
    class BookStudioConsumer:
        """Placeholder — django-channels 설치 필요."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "실시간 협업을 사용하려면 channels 패키지가 필요합니다: "
                "pip install channels channels-redis"
            )
