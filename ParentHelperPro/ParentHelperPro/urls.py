from django.contrib import admin
from django.urls import path, include
from php import views

urlpatterns = [
    path('php/', include("php.urls")),
    path('admin/', admin.site.urls),
]
