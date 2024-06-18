from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ParentHelperPro import settings
from php.views import UserAPIView, PostAPIView, RegisterAPIView, DecodeTokenAPIView, UserProfileView, \
    UpdateAvatarAPIView, PostListFilterView, PasswordResetRequestView, PasswordResetView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('api/v1/userlist/', UserAPIView.as_view()),
    path('api/v1/postlist/', PostAPIView.as_view()),
    path('api/v1/postlist/<int:pk>', PostAPIView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('get-user-id/', DecodeTokenAPIView.as_view(), name='get_user_id'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('update_avatar/', UpdateAvatarAPIView.as_view(), name='update_avatar'),
    path('posts/', PostListFilterView.as_view(), name='post-list'),

    path('password_reset_request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
