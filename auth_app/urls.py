from django.urls import path
from .views import RegisterView, LoginView, RefreshTokenView, LogoutView

urlpatterns = [
    path('register/',      RegisterView.as_view(),      name='auth_register'),
    path('login/',         LoginView.as_view(),          name='auth_login'),
    path('token/refresh/', RefreshTokenView.as_view(),   name='auth_token_refresh'),
    path('logout/',        LogoutView.as_view(),         name='auth_logout'),
]
