from django.contrib import admin
from django.urls import path, include
from php.views import UserAPIView, PostAPIView, RegisterAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('api/v1/userlist/', UserAPIView.as_view()),
    path('api/v1/postlist/', PostAPIView.as_view()),
    path('api/v1/postlist/<int:pk>', PostAPIView.as_view()),
]
