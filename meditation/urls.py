from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from django.urls import path
from .views import MeditationAudioCreateView,MeditationAudioListView,MeditationAudioStreamInMemoryView,MeditationCategoryCreateView,MeditationCategoryUpdateView,\
MeditationCateList,MeditatioCateDeleteApi,MeditationAudioListForAdminView,DummyApi


urlpatterns = [

path("create-cate/",MeditationCategoryCreateView.as_view(), name="create-cate"),
path("update-cate/<int:pk>/",MeditationCategoryUpdateView.as_view(), name="update-cate"),
path("create/",MeditationAudioCreateView.as_view(), name="create-audio"),
path("list/",MeditationAudioListView.as_view(), name="list-audio"),
path("list-admin/",MeditationAudioListForAdminView.as_view(), name="list-audio-admin"),
path("stream/<int:pk>/",MeditationAudioStreamInMemoryView.as_view(), name="stream"),
path("cate-list/",MeditationCateList.as_view(), name="cate-list"),
 path('meditation-cate/<int:pk>/delete/', MeditatioCateDeleteApi.as_view(), name='your-model-delete'),

 path('dummy/', DummyApi.as_view(), name='your-model-delete'),



]