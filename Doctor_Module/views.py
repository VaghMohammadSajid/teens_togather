from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status, generics
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from Acoounts.models import Accounts
from Doctor_Module.models import DoctorProfileModel, ReviewAndRating,AvailableTime,DoctorProfileModelEdit,DoctorProfileFieldEdit
from Acoounts.models import Accounts
from .serializers import DoctorSerializer,DocProfileSerializer,AddReviewSerializer,AvailableTimeSerializer,\
AddAvailableTimeSerializer,BlankSerilaizer,DoctorUpdateSerializer,DoctorProfileSerializer,AccountAdminSerializer,AppAvailbleSerializer,DoctorProfileModelEditSerializer,DeactivateDoctorSerializer

from django.db import transaction, IntegrityError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import generate_pas
from rest_framework.views import APIView
from .permission import IsDocUser,IsAdminOrDocUser
from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer
from utils.pagination import BasePagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from utils.filter_utils import filter_utils
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from urllib.parse import unquote
from django.db.models import Count
from django.db.models.functions import TruncDate
from Acoounts.apps import BLOCKLIST
from utils.trigger_notification import send_notification
class DocPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

logger = logging.getLogger(__name__)

class DocListApi(generics.ListAPIView):
    queryset = DoctorProfileModel.objects.filter(accounts__is_delete = False).order_by("-created_at")
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DocPagination
    # filter_backends = [filters.SearchFilter]  
    # search_fields = ['accounts__first_name', 'accounts__last_name', 'accounts__email', 'accounts__phone_number']

    @swagger_auto_schema(
        operation_description="Doctor List with optional search",
        responses={
            200: openapi.Response(description="Doctor List"),
            404: openapi.Response(description="No Doctor Found.")
        },
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY, description="Search query to filter doctor details.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'first_name', openapi.IN_QUERY, description="Filter by doctor's first name.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'price', openapi.IN_QUERY, description="Filter by price.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'designation', openapi.IN_QUERY, description="Filter by designation.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'email', openapi.IN_QUERY, description="Filter by doctor's email.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'mobile', openapi.IN_QUERY, description="Filter by doctor's mobile number.", type=openapi.TYPE_STRING
            ),
      
            openapi.Parameter(
                'created_date', openapi.IN_QUERY, description="Filter by created date (YYYY-MM-DD).", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            )
        ]
    )

    def list(self, request, *args, **kwargs):
        if "DOCLIST" in BLOCKLIST:
            return Response ("message : Work in progress",status=status.HTTP_426_UPGRADE_REQUIRED)
        return super().list(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response
    
    def get_queryset(self):
        list_filter = {"first_name":"accounts__first_name__icontains","price":"amount__icontains","desigination":"accounts__designation__icontains","email":"accounts__email__icontains","mobile":"accounts__phone_number__icontains","created_date":"created_at__gte"}
        queryset = super().get_queryset()

        if  created_date_last := self.request.query_params.get("created_date", None):
            input_date = parse_date(created_date_last)
            last_date = input_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lte=last_date)
        
        queryset = filter_utils(queryset=queryset,filter_dict=list_filter,obj=self)
        # user = Accounts.objects.get(id = 4)
        # logger.debug(f"{user=}")
        # send_notification(user, "You have checked the doclist!")

        return queryset





class DocCreatedApi(generics.CreateAPIView):
    queryset = DoctorProfileModel.objects.all()
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = BlankSerilaizer 

    @swagger_auto_schema(
        operation_description="Doctor Profile of Created",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Email'),
            openapi.Parameter('phone_number', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Phone_number'),
            # openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Password'),
            openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='first_name'),
            openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='last_name'),
            openapi.Parameter('doctor_type	', openapi.IN_FORM, type=openapi.TYPE_STRING, description='doctor_type	'),
            openapi.Parameter('amount', openapi.IN_FORM, type=openapi.TYPE_STRING, description='amount'),
            openapi.Parameter('experience', openapi.IN_FORM, type=openapi.TYPE_STRING, description='experience'),
            openapi.Parameter('about', openapi.IN_FORM, type=openapi.TYPE_STRING, description='about'),
            openapi.Parameter('profile_pic', openapi.IN_FORM, type=openapi.TYPE_FILE, description='profile_pic'),    
        ]
    )
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            # password = request.data.get('password')
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")

            doctor_type = request.data.get('doctor_type')
            amount = request.data.get('amount')
            experience = request.data.get('experience')
            about = request.data.get('about')
            if "profile_pic" not in request.FILES:
                return Response({"msg":"profile pic is mandatory"},status=status.HTTP_400_BAD_REQUEST)
            profile_pic = request.FILES['profile_pic']
            

            if Accounts.objects.filter(email=email).exists() or Accounts.objects.filter(
                    phone_number=phone_number).exists():
                return Response({"message": "Email or Phone Number Already Exists."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            password = generate_pas()

            with transaction.atomic():
                user = Accounts.objects.create_user(
                    username=email, email=email, phone_number=f"+91 {phone_number}",
                     designation="DOC", password=password,first_name =first_name,last_name=last_name
                )
                user.is_active = True
                user.save()

                doctor_profile_data = DoctorProfileModel.objects.create(
                    accounts=user, doctor_type=doctor_type,
                    amount=amount, experience=experience,
                    about=about,
                    profile_pic=profile_pic
                )
                doctor_profile_data.save()

                return Response({"message": "Doctor Created."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"message": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"message": "Integrity Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "Unexpected Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DoctorUpdateAPIView(generics.UpdateAPIView):
    queryset = DoctorProfileModel.objects.all()
    serializer_class = DoctorUpdateSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


# class DocUpdateApi(generics.UpdateAPIView):
#     queryset = DoctorProfileModel.objects.all()
#     serializer_class = DoctorSerializer
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Doctor Profile of Updated",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'accounts': openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email Address"),
#                         'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description="Phone Number"),
#                         'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
#                     },
#                     description='Account details for the doctor'),
#                 'doctor_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of Doctor'),
#                 'amount': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor Fees'),
#                 'experience': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor Experience'),
#                 'reviews': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor Reviews'),
#                 'about': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor About'),
#                 'available_date': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor Available Date'),
#                 'available_time': openapi.Schema(type=openapi.TYPE_STRING, description='Doctor Available Time'),
#             },
#             responses={200: openapi.Response('Doctor Updated.'), 400: openapi.Response('Bad Request')}
#         )
#     )
#     def update(self, request, *args, **kwargs):
#         doctor_profile = self.get_object()

#         try:
#             accounts_data = request.data.get('accounts', {})
#             email = accounts_data.get('email', doctor_profile.accounts.email)
#             phone_number = accounts_data.get('phone_number', doctor_profile.accounts.phone_number)
#             password = accounts_data.get('password', None)

#             with transaction.atomic():
#                 doctor_profile.accounts.email = email
#                 doctor_profile.accounts.phone_number = phone_number
#                 if password:
#                     doctor_profile.accounts.set_password(password)
#                 doctor_profile.accounts.save()

#                 doctor_profile.doctor_type = request.data.get('doctor_type', doctor_profile.doctor_type)
#                 doctor_profile.amount = request.data.get('amount', doctor_profile.amount)
#                 doctor_profile.experience = request.data.get('experience', doctor_profile.experience)
#                 doctor_profile.reviews = request.data.get('reviews', doctor_profile.reviews)
#                 doctor_profile.about = request.data.get('about', doctor_profile.about)
#                 doctor_profile.available_date = request.data.get('available_date', doctor_profile.available_date)
#                 doctor_profile.available_time = request.data.get('available_time', doctor_profile.available_time)
#                 doctor_profile.save()

#                 return Response({"message": "Doctor Updated."}, status=status.HTTP_200_OK)

#         except ValidationError as e:
#             return Response({"message": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except IntegrityError as e:
#             return Response({"message": "Integrity Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"message": "Unexpected Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class DocDeleteApi(generics.DestroyAPIView):
#     queryset = DoctorProfileModel.objects.all()
#     serializer_class = DoctorSerializer
#     permission_classes = [IsAuthenticated]

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response({"message": "Doctor deleted."}, status=status.HTTP_200_OK)
#         except NotFound:
#             return Response({"message": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"message": "Doctor not deleted. Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DocProfileAdminApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            doctor_profile = DoctorProfileModel.objects.get(accounts=request.user)
            serializer = DoctorProfileSerializer(doctor_profile)
            return Response(serializer.data)

        except DoctorProfileModel.DoesNotExist:
            if request.user.is_admin: 
                serializer = AccountAdminSerializer(request.user)
                return Response(serializer.data)
            
            return Response({"error": "You do not have a profile."}, status=403)

class DocProfileApi(generics.RetrieveAPIView):
    queryset = DoctorProfileModel.objects.all()
    serializer_class = DocProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve Doctor Profile by ID",
        manual_parameters=[
            openapi.Parameter(
                'year', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING,
                
            ),
            openapi.Parameter(
                'month', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING,
                
            ),
        ],
        responses={200: DoctorSerializer},
    )
    def get(self, request, *args, **kwargs):
        doctor_profile = self.get_object()
        serializer = self.get_serializer(
            doctor_profile,
            context={
                'request': request,  
                'year': request.query_params.get('year'),
                'month': request.query_params.get('month'),
            }
        )
        return Response(serializer.data)

class AddReviewView(generics.CreateAPIView):
    queryset = ReviewAndRating.objects.all()
    serializer_class = AddReviewSerializer
    permission_classes = [IsAuthenticated]


class AvailableTimeCreateView(APIView):
    queryset = AvailableTime.objects.all()
    serializer_class = AddAvailableTimeSerializer
    permission_classes = [IsDocUser]



    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'time_slots': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'from_time': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format='date-time',
                                description='Start time of the time slot (ISO 8601 format)'
                            ),
                            'to_time': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format='date-time',
                                description='End time of the time slot (ISO 8601 format)'
                            ),
                        },
                        required=['from_time', 'to_time']
                    ),
                    description='List of time slots'
                ),
            },
            required=['time_slots']
        ),
        responses={
            201: openapi.Response('Available time updated successfully'),
            400: openapi.Response('Bad Request')
        }
    )
    def post(self, request, *args, **kwargs):
        
        
        add_available_obj = AddAvailableTimeSerializer(data=request.data['time_slots'],context={"user": request.user},many=True)
        if add_available_obj.is_valid():
            add_available_obj.save()
            return Response({"msg":"available time updated"},status=status.HTTP_201_CREATED)
        
        return Response({"error":add_available_obj.error_messages},status=status.HTTP_400_BAD_REQUEST)


class DocAppointmeantDocView(APIView):
    permission_classes = [IsAdminOrDocUser]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            name="from_date",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING

        ),
        openapi.Parameter(
            name="to_date",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
                name="created_date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Filter by created date (YYYY-MM-DD format)"
        ),
        openapi.Parameter(
            name="page_size",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
         openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
  
        
    ])

    
    def get(self,request):
        user = request.user
        queryset = AvailableTime.objects.filter(doctor__accounts=user)

        list_filter = {"from_date":"from_time","to_date":"to_time__lte","created_date": "created_at__gte"}

        if  created_date_last := self.request.query_params.get("created_date", None):
            
            try : 
                input_date = parse_date(created_date_last)
                last_date = input_date + timedelta(days=1)
                queryset = queryset.filter(created_at__lte=last_date)
            except TypeError  :
                return Response({"error": "Invalid date format. Please provide only the date in the correct format."}, status=status.HTTP_400_BAD_REQUEST)
            except:
                logger.error("error in doc-date-doc-list",exc_info=True)
                return Response({"error": "error."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = filter_utils(queryset=queryset,filter_dict=list_filter,obj=self)


        
        pagination = BasePagination()
        paginated_query = pagination.paginate_queryset(queryset,request=request)
        appointmeant_data = AppAvailbleSerializer(paginated_query,many=True).data
        return pagination.get_paginated_response(appointmeant_data)
    

class AvailableDelete(APIView):
    permission_classes = [IsDocUser]
    def delete(self,request,id):
        try:
            user = request.user
            AvailableTime.objects.filter(doctor__accounts=user,id=id).delete()
        except :
            logger.error("erro in available delete api",exc_info=True)
            return Response({"error":"error in delete api"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"success":True},status=status.HTTP_200_OK)


class DoctorProfileEditView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    permission_classes = [IsDocUser]
    @swagger_auto_schema(
        operation_description="Doctor Profile of Created",
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Email'),
            openapi.Parameter('phone_number', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Phone_number'),
            # openapi.Parameter('password', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Password'),
            openapi.Parameter('first_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='first_name'),
            openapi.Parameter('last_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='last_name'),
            openapi.Parameter('doctor_type	', openapi.IN_FORM, type=openapi.TYPE_STRING, description='doctor_type	'),
            openapi.Parameter('amount', openapi.IN_FORM, type=openapi.TYPE_STRING, description='amount'),
            openapi.Parameter('experience', openapi.IN_FORM, type=openapi.TYPE_STRING, description='experience'),
            openapi.Parameter('about', openapi.IN_FORM, type=openapi.TYPE_STRING, description='about'),
            openapi.Parameter('profile_pic', openapi.IN_FORM, type=openapi.TYPE_FILE, description='profile_pic'),    
        ]
    )  
  
    def post(self, request):

        try:
            with transaction.atomic():
                user = Accounts.objects.get(id=request.user.id)
                doctor_profile = DoctorProfileModel.objects.get(accounts = user)

                edit_session = DoctorProfileModelEdit.objects.create(
                    accounts=doctor_profile,
                    status='pending'
                )

                expected_fields = {
                    "email": request.data.get("email"),
                    "phone_number": request.data.get("phone_number"),
                    "first_name": request.data.get("first_name"),
                    "last_name": request.data.get("last_name"),
                    "doctor_type": request.data.get("doctor_type"),
                    "amount": request.data.get("amount"),
                    "experience": request.data.get("experience"),
                    "about": request.data.get("about"),
                }

                profile_pic = request.FILES['profile_pic']
              

                field_edits = [
                    DoctorProfileFieldEdit(
                        doctor_profile_edit=edit_session,
                        field_name=field_name,
                        field_value=field_value
                    )
                    for field_name, field_value in expected_fields.items() if field_value
                ]
                if profile_pic :
              
                    if len(profile_pic.name) > 400 :
                        return  Response({"error": "Length of image name can't be greater than 400."},status=status.HTTP_400_BAD_REQUEST)
                    upload_path = os.path.join(settings.MEDIA_ROOT)
                    if not os.path.exists(upload_path):
                        os.makedirs(upload_path)
                  
                    fs = FileSystemStorage(location=upload_path)
                    filename = fs.save(f"profile_pics/{profile_pic.name}", profile_pic)  
                    file_url = fs.url(filename)
                    doc_ob = DoctorProfileFieldEdit(field_name="profile_pic",field_value=file_url,doctor_profile_edit=edit_session)
                    field_edits = field_edits + [doc_ob]
                DoctorProfileFieldEdit.objects.bulk_create(field_edits)

            return Response({"message": "Edit session created successfully.", "edit_id": edit_session.id},status=status.HTTP_201_CREATED)

        except DoctorProfileModel.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcceptRejectAPIView(APIView):
    permission_classes = [IsAdminUser]  

    @swagger_auto_schema(
        operation_description="Accept or reject a doctor's profile edit request. Only requests with 'pending' status can be processed.",
        manual_parameters=[
            openapi.Parameter(
                'edit_id', openapi.IN_PATH, description="ID of the edit request to process.", type=openapi.TYPE_INTEGER
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Action to perform: 'accept' or 'reject'.",
                    enum=['accept', 'reject']
                ),
                'rejection_reason': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Reason for rejecting the edit request. Required if action is 'reject'.",
                    nullable=True
                )
            },
            required=['action'], 
        ),
        responses={
            200: openapi.Response(
                description="Action performed successfully.",
                examples={
                    "application/json": {
                        "message": "Profile edit accepted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input or bad request.",
                examples={
                    "application/json": {
                        "error": "Action is required (accept or reject)."
                    }
                }
            ),
            404: openapi.Response(
                description="Edit request not found.",
                examples={
                    "application/json": {
                        "error": "Edit request not found."
                    }
                }
            ),
            500: openapi.Response(
                description="Server error.",
                examples={
                    "application/json": {
                        "error": "An error occurred while processing the request.",
                        "details": "Detailed error message."
                    }
                }
            ),
        }
    )
    def post(self, request, edit_id):

        doctor_profile_edit = get_object_or_404(DoctorProfileModelEdit,id=edit_id)

        if doctor_profile_edit.status != 'pending':
            return Response({'error': 'Only pending requests can be processed.'}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action') 

        if not action:
            return Response({'error': 'Action is required (accept or reject).'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                if action == 'accept':
                    doctor_profile_edit.status = 'verified'
                    doctor_profile_edit.rejection_reason = None 
                    doctor_profile_edit.save()

                    for field_edit in doctor_profile_edit.field_edits.all():
                        field_name = field_edit.field_name
                        field_value = field_edit.field_value

                        if hasattr(DoctorProfileModel, field_name):


                            if field_name == 'profile_pic':
                                decoded_field_value = unquote(field_value.lstrip('/media/'))

                                upload_path = os.path.join(settings.MEDIA_ROOT,decoded_field_value)
                              
                                try:
                                    with open(upload_path, 'rb') as image_file:
                                        doctor_profile_edit.accounts.profile_pic.save(
                                            upload_path,  
                                            File(image_file),   
                                            save=False        
                                        )
                                except FileNotFoundError:
                                    logger.error(f"Image not found at {upload_path}")
                                except Exception as e:
                                    logger.exception(f"An error occurred while saving the image: {e}")

                            else:
                                setattr(doctor_profile_edit.accounts, field_name, field_value)
                                            


                        elif hasattr(Accounts, field_name):
                            setattr(doctor_profile_edit.accounts.accounts, field_name, field_value)

                    doctor_profile_edit.accounts.save()  
                    doctor_profile_edit.accounts.accounts.save()

                elif action == 'reject':
                    doctor_profile_edit.status = 'rejected'

                    rejection_reason = request.data.get('rejection_reason')
                    if not rejection_reason:
                        return Response({'error': 'Rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

                    doctor_profile_edit.rejection_reason = rejection_reason
                    doctor_profile_edit.save()

                else:
                    return Response({'error': 'Invalid action. It must be "accept" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)

                return Response({'message': f'Profile edit {action}ed successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing the request.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DoctorProfileEditListAPIView(generics.ListAPIView):
    queryset = DoctorProfileModelEdit.objects.all().prefetch_related('field_edits').order_by('-created_at')
    serializer_class = DoctorProfileModelEditSerializer
    permission_classes = [IsAdminUser]
    pagination_class = DocPagination

    @swagger_auto_schema(
        operation_description="Retrieve all doctor profile edit requests with optional filters.",
        responses={
            200: openapi.Response(description="List of doctor profile edit requests with their field edits."),
            403: openapi.Response(description="Forbidden. Only admins can access this endpoint."),
        },
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY, description="Filter by status (e.g., pending, approved, rejected).", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'created_at', openapi.IN_QUERY, description="Filter by creation date (YYYY-MM-DD).", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'unique_id', openapi.IN_QUERY, description="Filter by unique_id (e.g., #5dNkJCrs73Fk).", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'accounts_username', openapi.IN_QUERY, description="Filter by doctor's username.", type=openapi.TYPE_STRING
            )
        ]
    )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_queryset(self):
        list_filter = {"status":"status","created_date":"created_at__gte","unique_id" : "request_id"}
        queryset = super().get_queryset()

        if  created_date_last := self.request.query_params.get("created_date", None):
            input_date = parse_date(created_date_last)
            last_date = input_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lte=last_date)
        
        queryset = filter_utils(queryset=queryset,filter_dict=list_filter,obj=self)

        return queryset

    

class DoctorProfileEditDetailAPIView(APIView):
    permission_classes = [IsDocUser]  

    @swagger_auto_schema(
        operation_description="Retrieve specific doctor profile edit requests for the logged-in user.",
        responses={
            200: openapi.Response(
                description="List of doctor profile edit requests for the logged-in user.",
                examples={
                    "application/json": {
                        "doctor_profile_edits": [
                            {
                                "id": 1,
                                "accounts_username": "doctor_user",
                                "status": "pending",
                                "rejection_reason": None,
                                "created_at": "2025-01-01T12:00:00Z",
                                "field_edits": [
                                    {
                                        "field_name": "email",
                                        "field_value": "new_email@example.com"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            404: openapi.Response(description="Doctor profile not found."),
        },
    )
    def get(self, request):
        user = request.user
        try:
            doctor_profile = DoctorProfileModel.objects.get(accounts=user)
        except DoctorProfileModel.DoesNotExist:
            return Response({'error': 'Doctor profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        doctor_profile_edits = DoctorProfileModelEdit.objects.filter(accounts=doctor_profile).prefetch_related('field_edits')
        
        serializer = DoctorProfileModelEditSerializer(doctor_profile_edits, many=True)

        return Response({"doctor_profile_edits": serializer.data}, status=status.HTTP_200_OK)
    

class DeactivateDoctorApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = DeactivateDoctorSerializer

    @swagger_auto_schema(
        operation_description="Deactivate a doctor by setting is_active to False",
        request_body=DeactivateDoctorSerializer,
        responses={
            200: "Success",
            400: "Invalid Doctor ID",
            403: "Permission Denied"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        doctor_id = serializer.validated_data['doctor_id']

        try:
            doc = DoctorProfileModel.objects.get(id=doctor_id)
            doctor = Accounts.objects.get(id=doc.accounts.id, designation="DOC")
            doctor.is_delete = True
            
            
            doctor.save()
            return Response({"message": "Doctor deactivated successfully."}, status=status.HTTP_200_OK)

        except Accounts.DoesNotExist:
            return Response({"message": "Doctor with the provided ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        




# doc dash test 
class DocDashboardAPIView(generics.ListAPIView):
    permission_classes = [IsDocUser]
    @swagger_auto_schema(
        operation_description="Fetch the doctor's dashboard data including appointment counts and statuses.",
        manual_parameters=[
            openapi.Parameter(
                'month', openapi.IN_QUERY, description="Month to filter the data (1-12)", 
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY, description="Year to filter the data (e.g., 2024)", 
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'appointment_month', openapi.IN_QUERY, 
                description="Month to filter the appointments (1-12)", 
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'appointment_year', openapi.IN_QUERY, 
                description="Year to filter the appointments (e.g., 2024)", 
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful Response",
                examples={
                    "application/json": {
                        "total_pending_appointment": 5,
                        "total_confirm_appointment": 10,
                        "total_declined_appointment": 3,
                        "daily_appointment_data": [
                            {"appointment_date": "2024-01-01", "appointment_count": 2},
                            {"appointment_date": "2024-01-02", "appointment_count": 3}
                        ]
                    }
                }
            ),
            404: openapi.Response(description="User or Doctor profile not found."),
            400: openapi.Response(description="Invalid month or year format."),
        }
    )  


    def get(self, request, *args, **kwargs):
        logger.debug("Inside Dashboard API")
        try:
            user = Accounts.objects.get(id=request.user.id)
        except Accounts.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        try:
            doctor_profile = DoctorProfileModel.objects.get(accounts=user)
            docid = doctor_profile.id

        except DoctorProfileModel.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=404)


        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)
        appointment_month = request.query_params.get('appointment_month', None)
        appointment_year = request.query_params.get('appointment_year', None)
        try:
            if month:
                month = int(month)
            if year:
                year = int(year)
            if appointment_month:
                appointment_month = int(appointment_month)
            if appointment_year:
                appointment_year = int(appointment_year)    
        except (ValueError, TypeError):
            return Response({"error": "Invalid month or year format."}, status=400)

        

        appointment_filters = {'doctor_id': docid}
        if appointment_month:
            appointment_filters['created_date__month'] = appointment_month
        if appointment_year:
            appointment_filters['created_date__year'] = appointment_year

        appointment_data = Appointment.objects.filter(**appointment_filters) \
            .annotate(appointment_date=TruncDate('created_date')) \
            .values('appointment_date') \
            .annotate(appointment_count=Count('id')) \
            .order_by('appointment_date')
        
        # appointment_data_perday = Appointment.objects.filter(**appointment_filters) \
        #     .annotate(appointment_date=TruncDate('created_date')) \
        #     .values('appointment_date') \
        #     .annotate(
        #         appointment_count=Count('id'), 
        #         user_count=Count('user', distinct=True) 
        #     ) \
        #     .order_by('appointment_date')

        # user__account__designation="TEENS",
        pending_queryset = Appointment.objects.filter(payment_status = 'PENDING',doctor_id = docid)
        pending_queryset = filter_utils(filter_dict={"start_date": "created_date__gte", "end_date": "created_date__lte"}, queryset=pending_queryset, obj=self)

        confirm_queryset = Appointment.objects.filter(payment_status = 'CONFIRM',doctor_id = docid)
        confirm_queryset = filter_utils(filter_dict={"start_date": "created_date__gte", "end_date": "created_date__lte"}, queryset=confirm_queryset, obj=self)

        declined_queryset = Appointment.objects.filter(payment_status = 'DECLINED',doctor_id = docid)
        declined_queryset = filter_utils(filter_dict={"start_date": "created_date__gte", "end_date": "created_date__lte"}, queryset=declined_queryset, obj=self)

       

        data = {
            "total_pending_appointment": pending_queryset.count(),
            "total_confirm_appointment": confirm_queryset.count(),
            "total_declined_appointment": declined_queryset.count(),
            # "appointment_data_perday" : appointment_data_perday,        
            "daily_appointment_data": appointment_data,
        }

        return Response(data)
    

# class Note(APIView):
#     pass
