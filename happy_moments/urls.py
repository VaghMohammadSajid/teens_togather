
from rest_framework_simplejwt.views import TokenVerifyView
from django.urls import path
from .views import HAppyCreateApi,HappyList,HappyLikePost,HappyListForAdmin,ReportHappyMomentView,ListHappyMomentReportsView,BlockHappyMomentView

urlpatterns = [


path("create/",HAppyCreateApi.as_view(), name="create"),
path("list/",HappyList.as_view(), name="list"),
path("list-admin/",HappyListForAdmin.as_view(), name="list-admin"),
path('happy-like',HappyLikePost.as_view(), name="happy-like"),





 path('happy-report/', ListHappyMomentReportsView.as_view(), name='list-happy-moment-reports'),
 

path('happy-report',ReportHappyMomentView.as_view()),
path('block_happy_moment/<int:pk>/', BlockHappyMomentView.as_view(), name='block_happy_moment'),




]