from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import mixins, viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Accounts,StoreOtpForEmail,TeenagerAndParent,Concentrate,StoreOtpForPhone,Avatar
from rest_framework import status, generics
from .models import Accounts,StoreOtpForEmail,TeenagerAndParent,Concentrate,StoreOtpForPhone,FeatureToggles
from django.core.mail import send_mail, EmailMultiAlternatives
import random
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from TEENS_TOGETHER.settings import EMAIL_HOST_USER
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth import authenticate
from django.db.models import Q
from django.db import transaction
import logging
from django.db import IntegrityError
from .schemas import *
from .serializer import ConcentrateSerializer,AvatarSerializer,TeensAndParentSerializer, UserCountSerializer,ProfileSerializer,UpdateAvatarSerializer,FeatureTogglesSerializer
from Doctor_Module.serializers import AccountSerializer
from utils.filter_utils import filter_utils
from datetime import timedelta,datetime
from django.db.models import Count
import calendar
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from appointment.models import Appointment

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve or update profile information for the logged-in user.",
        responses={
            200: ProfileSerializer,
            400: "Invalid input.",
            401: "Unauthorized access.",
            404: "Profile not found."
        }
    )
    def get_object(self):
        return TeenagerAndParent.objects.get(account=self.request.user)


class LoginApi(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            }
        ),
        responses={200: 'Login', 400: 'Bad Request',401:"401_UNAUTHORIZED"}
    )
    def post(self,request):
        email= request.data.get("email")
        password = request.data.get("password")
        try:
            user = Accounts.objects.get(email=email)
            authenticate = user.check_password(password)
            if authenticate:

                try:
                    teenager_and_parent = TeenagerAndParent.objects.get(account=user)
                    avatar_url = teenager_and_parent.avatar.image.url if teenager_and_parent.avatar else None
                except TeenagerAndParent.DoesNotExist:
                    avatar_url = None
                except Exception:
                   avatar_url = None
                   logger.critical("Issue is Sending in Avatar",exc_info=True)    
                refresh = RefreshToken.for_user(user)
                return Response({
                            "msg": "Customer login",
                            "id": user.id,
                             "avatar": avatar_url,
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }, status=status.HTTP_200_OK)
            
            return Response({"message":"Invalid username or password"},status=status.HTTP_401_UNAUTHORIZED)
        except Accounts.DoesNotExist as e:
            
            return Response({"message":"Invalid username or password"},status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error("unknow error in user login",exc_info=True)
            return Response({"message":"error"},status=status.HTTP_400_BAD_REQUEST)

class UpdateAvatarView(generics.UpdateAPIView):
    queryset = TeenagerAndParent.objects.all()
    serializer_class = UpdateAvatarSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update user avatar",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={200: "Avatar updated successfully", 400: "Bad Request"}
    )
    def get_object(self):
        return TeenagerAndParent.objects.get(account=self.request.user)

class ConcentrateListApi(generics.ListAPIView):
    queryset = Concentrate.objects.all().order_by("id")
    serializer_class = ConcentrateSerializer
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List Of Concentrates",
        responses={
            200: openapi.Response(
                description="List of Concentrates",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'concentrates': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'Id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Concentrate Id'),
                                    'Name': openapi.Schema(type=openapi.TYPE_STRING, description='Concentrate Name')
                                }
                            )
                        )
                    }
                )
            ),
            404: 'No Concentrate Found.'
        }
    )
    def get(self, request, *args, **kwargs):
        data =  super().get(request, *args, **kwargs)
        print(data.data)
        data.data = {"concentrates":data.data}
        return data

class ConcentrateCreateApi(APIView):
    @swagger_auto_schema(
        operation_description="Select Concentrate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Concentrate Name'),
            }
        ),
        responses={201: 'Concentrate Created', 400: 'Bad Request'}
    )
    def post(self,request):
        serializers = ConcentrateSerializer(data=request.data, context={"request": request})
        if serializers.is_valid():
            serializers.save()
            return Response({"data":serializers.data},status=status.HTTP_201_CREATED)
        return Response({'error': serializers.errors}, status=status.HTTP_400_BAD_REQUEST)


class ConcentrateUpdateApi(APIView):
    @swagger_auto_schema(
        operation_description="Update a Concentrate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Concentrate Name'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Concentrate Updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'Id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Concentrate Id'),
                                'Name': openapi.Schema(type=openapi.TYPE_STRING, description='Concentrate Name')
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Concentrate Not Found.'
        }
    )
    def put(self, request, pk):
        name = request.data.get('name')

        if not name:
            return Response({"message": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            concentrate = Concentrate.objects.get(pk=pk)
            concentrate.name = name
            concentrate.save()
            return Response({"data": {"Id":concentrate.id,"Name":concentrate.name}, "message": "Concentrate Updated."}, status=status.HTTP_200_OK)
        except Concentrate.DoesNotExist:
            return Response({"message": "Concentrate Not Found."}, status=status.HTTP_404_NOT_FOUND)


class ConcentrateDeleteApi(APIView):
    @swagger_auto_schema(
        operation_description="Delete a Concentrate",
        responses={
            200: openapi.Response(
                description="Concentrate Deleted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message')
                    }
                )
            ),
            404: openapi.Response(
                description="Concentrate Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        }
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            concentrate = Concentrate.objects.get(pk=pk)
            concentrate.delete()
            return Response({"message": "Concentrate Deleted."}, status=status.HTTP_200_OK)
        except Concentrate.DoesNotExist:
            return Response({"message": "Concentrate Not Found."}, status=status.HTTP_404_NOT_FOUND)


logger = logging.getLogger(__name__)


class SignupAPi(APIView):
    @swagger_auto_schema(
       
        request_body=signup_request_body,  
        responses={
            status.HTTP_201_CREATED: signup_response_schema, 
            status.HTTP_400_BAD_REQUEST: signup_response_schema,
        },
        operation_description="Create a new user account",
        operation_id="signupUser",
        operation_summary="Sign up a new user",
    )
    def post(self, request):
        try:
            user_type = request.data.get("user_type")
            concentrate = request.data.get("concentrate", [])
            date_of_birth = request.data.get("date_of_birth")
            phone_number = request.data.get("phone_number")
            email = request.data.get("email")
            gender = request.data.get("gender")
            password = request.data.get("password")
            mobile_key = request.data.get("mobile_key")
            email_key = request.data.get("email_key")
            avatar_id = request.data.get("avatar_id")
            nick_name = request.data.get("nick_name")
            email_key_obj = StoreOtpForEmail.objects.filter(unique_key=email_key)
            mobile_key_obj = StoreOtpForPhone.objects.filter(unique_key=mobile_key)
            if email_key_obj.exists() and mobile_key_obj.exists():
                if not email_key_obj[0].email == email and not mobile_key_obj[0].number == phone_number:
                    return Response({"msg":"email or phone number doesn't match"},status=status.HTTP_400_BAD_REQUEST)
                avatar = Avatar.objects.filter(id=avatar_id)
                if not avatar.exists():
                        return Response({"msg":"Avatar Doesn't exist"},status=status.HTTP_400_BAD_REQUEST)
                with transaction.atomic():

                    
                    user = Accounts.objects.create_user(username=email, email=email, phone_number=f"+91 {phone_number}",
                                                        first_name=None, last_name=None, designation=user_type,
                                                        password=password)
                    user.is_active = True
                    user.save()

                    
                    

                    concentrate_data = Concentrate.objects.filter(id__in=concentrate)

                    teens_parent = TeenagerAndParent(account=user, date_of_birth=date_of_birth, gender=gender,avatar=avatar[0],nick_name=nick_name)
                    teens_parent.save()
                    teens_parent.concentrate_on.add(*concentrate_data)
                    
                   
                    return Response({"message": "User Created",}, status=status.HTTP_201_CREATED)


            else:
                return Response({"msg":"invalid key"},status=status.HTTP_400_BAD_REQUEST)

        except  IntegrityError :
            logger.error("error duplicate in email or mobile",exc_info=True)
            return Response({"msg":"Phone no or email already exists"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("error signup",exc_info=True)
            return Response({"msg":"unexpected error occured"},status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=signup_request_body,  # Reuse signup request body schema here
        responses={
            status.HTTP_200_OK: signup_response_schema,  # Assuming the response schema is the same
            status.HTTP_400_BAD_REQUEST: signup_response_schema,
        },
        operation_description="Update user account details",
        operation_id="editUser",
        operation_summary="Edit user details",
    )
    def put(self, request):
            try:
                user_id = request.data.get("user_id")
                teen_parent = TeenagerAndParent.objects.filter(id=user_id).first()
                if not teen_parent:
                    return Response({"msg": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

                # Get the details to be updated from the request data
                concentrate = request.data.get("concentrate", [])
                date_of_birth = request.data.get("date_of_birth")
                phone_number = request.data.get("phone_number")
                email = request.data.get("email")
                gender = request.data.get("gender")
                password = request.data.get("password")
                avatar_id = request.data.get("avatar_id")
                nick_name = request.data.get("nick_name")

                # Fetch related data (avatar)
                avatar = Avatar.objects.filter(id=avatar_id)
                if not avatar.exists():
                    return Response({"msg": "Avatar doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

                # Start updating the TeenagerAndParent data
                with transaction.atomic():
                    # Update phone_number and other details directly on TeenagerAndParent
                    if phone_number:
                        teen_parent.account.phone_number = f"+91 {phone_number}"
                        teen_parent.account.save()  # Save the updated account details

                    if email:
                        teen_parent.account.email = email  # Update email
                        teen_parent.account.save()  # Save the updated account email

                    if password:
                        teen_parent.account.set_password(password)  # Update password
                        teen_parent.account.save()  # Save the updated account password

                    # Update TeenagerAndParent specific details
                    if date_of_birth:
                        teen_parent.date_of_birth = date_of_birth

                    if gender:
                        teen_parent.gender = gender

                    if avatar.exists():
                        teen_parent.avatar = avatar[0]  # Update avatar if provided

                    if nick_name:
                        teen_parent.nick_name = nick_name  # Update nickname

                    teen_parent.save()

                    # Update the concentrate information
                    if concentrate:
                        concentrate_data = Concentrate.objects.filter(id__in=concentrate)
                        teen_parent.concentrate_on.set(concentrate_data)

                    return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

            except IntegrityError:
                logger.error("Error: Duplicate email or mobile", exc_info=True)
                return Response({"msg": "Phone number or email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error("Error while updating user", exc_info=True)
                return Response({"msg": "Unexpected error occurred"}, status=status.HTTP_400_BAD_REQUEST)





class AdminLoginApi(APIView):
    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            }
        ),
        responses={200: 'Login', 400: 'Bad Request'}
    )
    def post(self,request):
        email= request.data.get("email")
        password = request.data.get("password")
        try:
            user = Accounts.objects.get(email=email)
            authenticate = user.check_password(password)
            if authenticate:
                if user.designation == "DOC" and not user.is_delete:

                        
                        refresh = RefreshToken.for_user(user)
                        return Response({"msg":"DOC login",'refresh': str(refresh),
                                        "id": user.id,
                                        "first_name": user.first_name,
                            "last_name": user.last_name,
                            "email": email,
                                'access': str(refresh.access_token),},status=status.HTTP_200_OK)
                
                if user.is_admin:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                            "msg": "Admin Login",
                            "id": user.id,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "email": email,
                            
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }, status=status.HTTP_200_OK)
            
   
            return Response({"msg":"Invalid username or password 2"},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"msg":"Invalid username or password 3"},status=status.HTTP_400_BAD_REQUEST)










class SendMobileOtpApi(APIView):
    @swagger_auto_schema(
        request_body=send_otp_request_body,
        responses={
            status.HTTP_200_OK: send_otp_response_schema,
            status.HTTP_400_BAD_REQUEST: send_otp_response_schema
        },
        operation_description="Send an OTP to the given phone number.",
        operation_id="sendMobileOtp",
    )
    def post(self,request):
        # random_number = random.randint(1000, 9999)
        random_number = "123"

        """
        need to implement sending otp class here
        """
        if request.data.get("number") == None or len(request.data.get("number")) < 10 :
            return Response({"msg":"enter a valid number"},status=status.HTTP_400_BAD_REQUEST)
        try:
            ot_obj2 = StoreOtpForPhone.objects.get(number=request.data.get("number"))
            ot_obj2.otp = random_number
            ot_obj2.save()
             

        except StoreOtpForPhone.DoesNotExist:
            ot_obj2 = StoreOtpForPhone.objects.create(number=request.data.get("number"),otp=random_number)
        except Exception as e:
            logger.error("error in sending otp",exc_info=True)
            return Response({"msg":"unexpected error occured"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"otp send to the number"},status=status.HTTP_200_OK)

   
class verifyMobileApi(APIView):
    @swagger_auto_schema(
        request_body=verify_mobile_request_body,
        responses={
            status.HTTP_200_OK: otp_response_schema,
            status.HTTP_400_BAD_REQUEST: otp_response_schema,
        },
        operation_description="Verify OTP for a given phone number.",
        operation_id="verifyMobileOtp",
    )
    def post(self,request):

        try:
            otp_obj = StoreOtpForPhone.objects.get(otp=request.data.get("otp"),number=request.data.get("number"))
        except StoreOtpForPhone.DoesNotExist:
            return Response({"msg":"incorrect otp"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("error in sending otp",exc_info=True)
            return Response({"msg":"unexpected error occured"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"otp verification completed","otp_key":otp_obj.unique_key},status=status.HTTP_200_OK) 

class SendEmailOtpApi(APIView):
    @swagger_auto_schema(
        request_body=send_email_otp_request_body,
        responses={
            status.HTTP_200_OK: otp_response_schema,
            status.HTTP_400_BAD_REQUEST: otp_response_schema,
        },
        operation_description="Send OTP to a given email.",
        operation_id="sendEmailOtp",
    )
    def post(self,request):
        random_number = random.randint(1000, 9999)
        random_number = "123"
        """
        need to implement sending otp class here
        """
        try:
            ot_obj2 = StoreOtpForEmail.objects.get(email=request.data.get("email"))
            ot_obj2.otp = random_number
            ot_obj2.save()
        except StoreOtpForEmail.DoesNotExist:
            ot_obj2 = StoreOtpForEmail.objects.create(email=request.data.get("email"),otp=random_number)
        except Exception as e:
            logger.error("error in sending otp",exc_info=True)
            return Response({"msg":"unexpected error occured"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"otp send to the number"},status=status.HTTP_200_OK)
    

class VerifyEmailOtpApi(APIView):
    @swagger_auto_schema(
        request_body=verify_email_request_body,
        responses={
            status.HTTP_200_OK: otp_response_schema,
            status.HTTP_400_BAD_REQUEST: otp_response_schema,
        },
        operation_description="Verify OTP for a given email.",
        operation_id="verifyEmailOtp",
    )
    def post(self,request):
        
        try:
            otp_obj = StoreOtpForEmail.objects.get(otp=request.data.get("otp"),email=request.data.get("email"))
        except StoreOtpForEmail.DoesNotExist as e:
            print(e)
            return Response({"msg":"incorrect otp"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("error in sending otp",exc_info=True)
            return Response({"msg":"unexpected error occured"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"otp verification completed","otp_key":otp_obj.unique_key},status=status.HTTP_200_OK) 
    

class AvatarViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    parser_classes = [MultiPartParser, FormParser]
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100  


class UserList(generics.ListAPIView):
    queryset = TeenagerAndParent.objects.all()
    serializer_class = TeensAndParentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination  

    @swagger_auto_schema(
        operation_description="List of User with optional search",
        responses={
            200: openapi.Response(description="List of user"),
            404: 'No User Found.'
        },
            manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY, description="Search query to filter users.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'created_date', openapi.IN_QUERY, description="Filter by created date (YYYY-MM-DD).", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
          
            openapi.Parameter(
                'email', openapi.IN_QUERY, description="Filter by email address.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'mobile', openapi.IN_QUERY, description="Filter by mobile number.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'designation', openapi.IN_QUERY, description="Filter by designation.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'nickname', openapi.IN_QUERY, description="Filter by user's first name.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'gender', openapi.IN_QUERY, description="Filter by user's gender.", type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        get_super = super().get(request,*args, **kwargs)
        
        return get_super
    
    def get_queryset(self):
        list_filter = {"created_date": "account__date_joined__gte","email":"account__email__icontains","mobile":"account__phone_number__icontains","desigination":"account__designation__icontains","gender":"gender","nickname":"nick_name"}
        queryset = super().get_queryset()

        if  created_date_last := self.request.query_params.get("created_date", None):
            input_date = parse_date(created_date_last)
            last_date = input_date + timedelta(days=1)
            queryset = queryset.filter(account__date_joined__lte=last_date)

        #this is a filter function avilabile in utils. In that function there is filter working that function will be create the quray
        queryset = filter_utils(queryset=queryset,filter_dict=list_filter,obj=self)

        return queryset

class DashboardAPIView(generics.ListAPIView):
    serializer_class = UserCountSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Dashboard Api",
        responses={
            200: openapi.Response(description="Dashboard Data"),
            404: 'No Data Found.'
        },
        manual_parameters=[
            openapi.Parameter(
                'month', openapi.IN_QUERY, description="Enter Month (Numeric)", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY, description="Enter Year (Numeric)", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'appointment_month', openapi.IN_QUERY,
                description="Filter appointments by month (Numeric)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'appointment_year', openapi.IN_QUERY,
                description="Filter appointments by year (Numeric)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'designation', openapi.IN_QUERY, description="Filter by designation.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'teen_startdate', openapi.IN_QUERY, description="Filter by teen start date (YYYY-MM-DD)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'teen_enddate', openapi.IN_QUERY, description="Filter by teen end date (YYYY-MM-DD)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'parent_startdate', openapi.IN_QUERY, description="Filter by parent start date (YYYY-MM-DD)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'parent_enddate', openapi.IN_QUERY, description="Filter by parent end date (YYYY-MM-DD)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'doc_startdate', openapi.IN_QUERY, description="Filter by doctor start date (YYYY-MM-DD)", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'doc_enddate', openapi.IN_QUERY, description="Filter by doctor end date (YYYY-MM-DD)", type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):

        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)
        designation = request.query_params.get('designation', 'all').upper()
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

        result = []
        if designation == 'ALL':
            designations = ['TEENS', 'PARENTS', 'DOC']
        else:
            designations = [designation]

        filters = {'designation__in': designations}
        if month:
            filters['date_joined__month'] = month
        if year:
            filters['date_joined__year'] = year

        result = Accounts.objects.filter(**filters).annotate(created_date=TruncDate('date_joined')) \
                             .values('created_date') \
                             .annotate(user_count=Count('id')) \
                             .order_by('created_date')
        


        appointment_filters = {}
        if appointment_month:
            appointment_filters['created_date__month'] = appointment_month
        if appointment_year:
            appointment_filters['created_date__year'] = appointment_year

        appointment_data = Appointment.objects.filter(**appointment_filters) \
            .annotate(appointment_date=TruncDate('created_date')) \
            .values('appointment_date') \
            .annotate(appointment_count=Count('id')) \
            .order_by('appointment_date')

        teens_queryset = Accounts.objects.filter(designation="TEENS")
        teens_queryset = filter_utils(filter_dict={"teen_startdate": "date_joined__gte", "teen_enddate": "date_joined__lte"}, queryset=teens_queryset, obj=self)

        parents_queryset = Accounts.objects.filter(designation="PARENTS")
        parents_queryset = filter_utils(filter_dict={"parent_startdate": "date_joined__gte", "parent_enddate": "date_joined__lte"}, queryset=parents_queryset, obj=self)

        doctors_queryset = Accounts.objects.filter(designation="DOC")
        doctors_queryset = filter_utils(filter_dict={"doc_startdate": "date_joined__gte", "doc_enddate": "date_joined__lte"}, queryset=doctors_queryset, obj=self)

        data = {
            "total_teens": teens_queryset.count(),
            "total_parents": parents_queryset.count(),
            "total_doctors": doctors_queryset.count(),
            "daily_registration_data": result,
            "daily_appointment_data": appointment_data,
        }

        return Response(data)




class ChangePasswordApi(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'current_password': openapi.Schema(type=openapi.TYPE_STRING, description='Current Password'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New Password'),
            }
        ),
        responses={200: 'Password changed successfully', 400: 'Bad Request', 401: 'Unauthorized'}
    )
    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        try:
            user = Accounts.objects.get(id=request.user.id)
            authenticate = user.check_password(current_password)

            if not authenticate:
                return Response({"message": "Current password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        except Accounts.DoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error changing password", exc_info=True)
            return Response({"message": "An error occurred while changing the password"}, status=status.HTTP_400_BAD_REQUEST)


class FeatureTogglesListCreateView(generics.ListCreateAPIView):
    queryset = FeatureToggles.objects.all()
    serializer_class = FeatureTogglesSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all feature toggles or create a new feature toggle.",
        responses={
            200: FeatureTogglesSerializer(many=True),
            201: FeatureTogglesSerializer(),
            403: "Forbidden",
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new feature toggle.",
        request_body=FeatureTogglesSerializer,
        responses={
            201: FeatureTogglesSerializer(),
            400: "Bad Request",
            403: "Forbidden",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
class FeatureTogglesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset = FeatureToggles.objects.all()
    serializer_class = FeatureTogglesSerializer
    permission_classes = [IsAdminUser]

class FeatureTogglesGetAllView(generics.ListAPIView):

    queryset = FeatureToggles.objects.all()
    serializer_class = FeatureTogglesSerializer
    permission_classes = [IsAuthenticated] 
