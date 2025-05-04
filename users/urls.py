from django.urls import path
from .views import (
    RegisterUserView,
    ActivateAccountView,
    EmergencyProfilesListView,
    ActivateEmergencyProfileView,
    LoginView,
    SendResetCodeView,
    VerifyResetCodeView,
    PasswordResetWithTokenView,
    SendLoginCodeView,
    LoginWithCodeView,
    ManageUserView,
    ListPilgrimsView, GetSupervisorView, GetLinkedPilgrimView,
)


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('activate/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/send-code/', SendLoginCodeView.as_view(), name='send-login-code'),
    path('login/with-code/', LoginWithCodeView.as_view(), name='login-with-code'),
    path('password/send-reset-code/', SendResetCodeView.as_view(), name='send-reset-code'),
    path('password/verify-reset-code/', VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('password/reset/', PasswordResetWithTokenView.as_view(), name='reset-password'),
    path('me/', ManageUserView.as_view(), name='manage-user'),
    path('pilgrims/', ListPilgrimsView.as_view(), name='list-pilgrims'),
    path('emergency/', EmergencyProfilesListView.as_view(), name='emergency-profiles'),
    path('emergency/activate/', ActivateEmergencyProfileView.as_view(), name='activate-emergency'),
    path('get-supervisor/', GetSupervisorView.as_view()),
    path('linked-pilgrim/', GetLinkedPilgrimView.as_view()),

]
