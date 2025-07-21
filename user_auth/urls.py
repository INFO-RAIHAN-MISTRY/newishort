from django.urls import path
from user_auth.views import (
    auth_login, 
    auth_register, 
    verification_msg,
    user_email_verify,
    auth_logout,
    reset_pass_email,
    reset_password,
    google_auth,
)

app_name = "user_auth"
urlpatterns = [
    path('logout/', auth_logout, name="user_logout"),
    path('login/', auth_login, name="auth_login"),
    path('register/', auth_register, name="auth_register"),
    path('verification/message/', verification_msg, name="Verify_account"),
    path('verify/<slug>/', user_email_verify),
    path('reset/password/email/', reset_pass_email, name="reset_pass_email"),
    path('reset/password/<slug>/', reset_password, name="reset_password"),
    path('google-auth/', google_auth, name="google_auth"),
]
