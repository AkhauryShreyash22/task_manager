from django.urls import path
from .views import RegisterView, LoginAPI, LogoutAPI, ProfileAPI

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('profile/', ProfileAPI.as_view(), name='profile'),
]