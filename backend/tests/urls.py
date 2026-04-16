from django.urls import path, include

urlpatterns = [
    path("api/studio/", include("bookstudio.api.urls")),
]
