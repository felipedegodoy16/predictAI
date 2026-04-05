from django.urls import path
from .views import (
    UserListCreateView, UserDetailView, MeView, ChangePasswordView,
    ForgotPasswordView, ValidateResetCodeView, ResetPasswordWithCodeView
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('me/', MeView.as_view(), name='user-me'),
    path('change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='user-forgot-password'),
    path('validate-reset-code/', ValidateResetCodeView.as_view(), name='user-validate-reset-code'),
    path('reset-password-with-code/', ResetPasswordWithCodeView.as_view(), name='user-reset-password-with-code'),
]
