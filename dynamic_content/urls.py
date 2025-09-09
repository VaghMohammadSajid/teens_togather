

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DynamiContentViewSet,Tech

router = DefaultRouter()
router.register(r'dynamic-contents', DynamiContentViewSet)




urlpatterns = [
  path('', include(router.urls)),
  path('tech',Tech.as_view()),
  # path('admin-dynamic-contents-list/', DynamiContentListAdminView.as_view()),
 

]