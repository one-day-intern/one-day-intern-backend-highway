from django.urls import path
from .views import (
    serve_login_assessee,
    serve_register_company,
    serve_google_login_callback_for_assessor,
    serve_register_assessee,
    serve_google_login_register_assessee,
    serve_google_register_assessor,
    serve_register_assessor,
    serve_get_user_info,
    generate_assessor_one_time_code,
    serve_login_assessor_company
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register-company/', serve_register_company),
    path('register-assessor/', serve_register_assessor),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/oauth/login/assessor/', serve_google_login_callback_for_assessor, name='glogin-login-assessor'),
    path('google/oauth/register/assessor/', serve_google_register_assessor, name='glogin-register-assessor'),
    path('google/oauth/login-register/assessee/', serve_google_login_register_assessee, name='glogin-assessee'),
    path('register-assessee/', serve_register_assessee),
    path('generate-code/', generate_assessor_one_time_code),
    path('get-info/', serve_get_user_info),
    path('login/assessor-company/', serve_login_assessor_company, name='login-assessor-company'),
    path('login/assessee/', serve_login_assessee, name='login-assessee'),
]

