from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import VoiceCreatedApi, VoiceUpdateApi, VoiceOfTheDayListView, VoiceDeleteApi,VoiceLikePost,VoiceOfTheDayRetrieveView,VoiceOfTheDayListForAdminView

urlpatterns = [
    path('voice/<int:pk>/', VoiceOfTheDayRetrieveView.as_view(), name='voice-retrieve'),
    path('voice-create/', VoiceCreatedApi.as_view(), name="voice-create"),
    path('voice-update/<int:pk>/', VoiceUpdateApi.as_view(), name="voice-update"),
    path('voice-list-admin/', VoiceOfTheDayListForAdminView.as_view(), name="voice-list"),
    path('voice-list/', VoiceOfTheDayListView.as_view(), name="voice-list"),
    path('voice-delete/<int:pk>/', VoiceDeleteApi.as_view(), name="voice-delete"),
    path('voice-like/', VoiceLikePost.as_view(), name="voice-like"),
    # Add other paths here
]

