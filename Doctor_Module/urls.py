from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import DocCreatedApi,  DocListApi,DocProfileApi,AddReviewView,AvailableTimeCreateView,DocAppointmeantDocView,AvailableDelete,DoctorUpdateAPIView,DocProfileAdminApi,DoctorProfileEditView,AcceptRejectAPIView,DoctorProfileEditListAPIView,DoctorProfileEditDetailAPIView,DeactivateDoctorApi,DocDashboardAPIView

urlpatterns = [
    path('doc-list/', DocListApi.as_view(), name='doc-list'),
    path('doc-create/', DocCreatedApi.as_view(), name='doc-create'),
    path('doc-update/<int:pk>/', DoctorUpdateAPIView.as_view(), name='doc-update'),
    # path('doc-delete/<int:pk>/', DocDeleteApi.as_view(), name='doc-delete'),
    path('doc-profile/<int:pk>/', DocProfileApi.as_view(), name='doc-profile'),
    path('profile/', DocProfileAdminApi.as_view(), name='user-detail'),
    path('add-review',AddReviewView.as_view(), name="add-review"),
    path('add-availabletime',AvailableTimeCreateView.as_view(), name="add-availabletime"),
    path('doc-available-list-admin',DocAppointmeantDocView.as_view(), name="doc-available-list-admin"),
    path('doc-available-delete/<int:id>/',AvailableDelete.as_view(), name="doc-available-delete"),

    path('doctor-profile-edit/', DoctorProfileEditView.as_view(), name='doctor_profile_edit'),
    path('doctor_profile_edit/process/<int:edit_id>/', AcceptRejectAPIView.as_view(), name='process_doctor_profile_edit'),
    path('doctor-profile-edits/admin-list', DoctorProfileEditListAPIView.as_view(), name='doctor-profile-edit-list'),
    path('doctor-profile-edits/doc-list', DoctorProfileEditDetailAPIView.as_view(), name='doctor-profile-edit-detail'),

    path('deactivate-doctor/', DeactivateDoctorApi.as_view(), name='deactivate-doctor'),

   
    path('dashboard/', DocDashboardAPIView.as_view(), name='doctor-dashboard'),

   
]

