from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from django.urls import path,include
from .views import SignupAPi,LoginApi,AdminLoginApi,ConcentrateListApi,ConcentrateCreateApi,ConcentrateUpdateApi,ConcentrateDeleteApi,\
    verifyMobileApi,SendMobileOtpApi,SendEmailOtpApi,VerifyEmailOtpApi,AvatarViewSet,UserList,ChangePasswordApi,DashboardAPIView,ProfileView,UpdateAvatarView,FeatureTogglesListCreateView,FeatureTogglesRetrieveUpdateDestroyView,FeatureTogglesGetAllView

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'avatars', AvatarViewSet)

urlpatterns = [
 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # path("verify/",VerifyApi.as_view()),
    path('profile/', ProfileView.as_view(), name='profile'),
    path("dashboard",DashboardAPIView.as_view(),name="dashboard"),
    path("signup/",SignupAPi.as_view(),name="signup"),
    path("login/", LoginApi.as_view(), name="login"),
    path("admin_login/", AdminLoginApi.as_view(), name="admin_login"),
    path("concentrate-list/", ConcentrateListApi.as_view(), name="concentrate-list"),
    path("concentrate-create/", ConcentrateCreateApi.as_view(), name="concentrate-create"),
    path("concentrate-update/<int:pk>/", ConcentrateUpdateApi.as_view(), name="concentrate-update"),
    path("concentrate-delete/<int:pk>/", ConcentrateDeleteApi.as_view(), name="concentrate-delete"),
    # path("resend-otp/",ResendOTp.as_view())

    path("update-avatar/",UpdateAvatarView.as_view(),name="send-mobile-otp"),
    path("send-mobile-otp/",SendMobileOtpApi.as_view(),name="send-mobile-otp"),
    path("verify-mobile-otp/",verifyMobileApi.as_view(),name='verify-mobile-otp'),
    path("send-email-otp/",SendEmailOtpApi.as_view(),name="send-email-otp"),
    path("verify-email-otp/",VerifyEmailOtpApi.as_view(),name="verify-email-otp"),
     path('', include(router.urls)),
     path("user-list",UserList.as_view(), name="user-list"),
    path('change-password/', ChangePasswordApi.as_view(), name='change_password'),


    path('feature-toggles/', FeatureTogglesListCreateView.as_view(), name='feature-toggles-list-create'),
    path('feature-toggles/<int:pk>/', FeatureTogglesRetrieveUpdateDestroyView.as_view(), name='feature-toggles-detail'),
    path('feature-toggles-get-all/', FeatureTogglesGetAllView.as_view(), name='feature-toggles-get-all'),



]

