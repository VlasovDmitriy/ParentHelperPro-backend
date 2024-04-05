from django.urls import path
from php import views


urlpatterns = [
    path('', views.index, name="index"),
]