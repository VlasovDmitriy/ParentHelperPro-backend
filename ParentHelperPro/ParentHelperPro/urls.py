from django.contrib import admin
from django.urls import path, include
from php.views import UserAPIView, PostAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/userlist/', UserAPIView.as_view()),
    path('api/v1/postlist/', PostAPIView.as_view()),
]
