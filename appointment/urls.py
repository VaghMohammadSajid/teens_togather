

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentApi,PaymentConfirm,AppointmeantList,AppointmeantListByDoc






urlpatterns = [

 path('apointmeant-create/',AppointmentApi.as_view(), name="appointment-create"),
 path('paymeant/',PaymentConfirm.as_view(), name="paymeant"),
 path("appointmeant-list",AppointmeantList.as_view(), name="appointmeant-list"),
  path('appointmeant-doc/',AppointmeantListByDoc.as_view(), name="appointmeant-doc")

]