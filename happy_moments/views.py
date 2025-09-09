from django.shortcuts import render

# Create your views here.
from gc import is_finalized
from rest_framework import status, generics, permissions,filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# from Voice_of_the_day.serializers import VoiceOfTheDaySerializer
from .serializers import HappyMomentsSerializer,HappyMomentReportSerializer,HappyMomentSerializer
import logging
# from Voice_of_the_day.models import *
from .models import HappyMoments,HappyMomentReport
from rest_framework.pagination import PageNumberPagination
from Acoounts.models import Accounts,TeenagerAndParent
from utils.filter_utils import filter_utils
from datetime import timedelta
from django.utils.dateparse import parse_date
from Acoounts.apps import BLOCKLIST
logger = logging.getLogger(__name__)
from utils.trigger_notification import send_notification


class HAppyCreateApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create Voice of the Day",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, description='Title of the voice of the day.',
                              type=openapi.TYPE_STRING),
            
            openapi.Parameter('file', openapi.IN_FORM,
                              description='Image related to the voice of the day. This should be an image file.',
                              type=openapi.TYPE_FILE),
        ],
        responses={201: openapi.Response('Voice Created.'), 400: openapi.Response('Bad Request')}
    )
    def post(self, request):
        data = request.data
        serializer = HappyMomentsSerializer(data=data,context={"user":request.user,})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class VoiceUpdateApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Update Voice of the Day",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, description='Title of the voice of the day.',
                              type=openapi.TYPE_STRING),
            openapi.Parameter('content', openapi.IN_FORM,
                              description='Content or description for the voice of the day.', type=openapi.TYPE_STRING),
            openapi.Parameter('image', openapi.IN_FORM,
                              description='Image related to the voice of the day. This should be an image file.',
                              type=openapi.TYPE_FILE),
            openapi.Parameter('concentrates', openapi.IN_FORM,
                              description='List of related concentrate primary keys as integers.',
                              type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            openapi.Parameter('person_likes', openapi.IN_FORM,
                              description='List of teens/parent primary keys who liked the voice as integers.',
                              type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            openapi.Parameter('total_likes', openapi.IN_FORM, description='Total number of likes for this voice.',
                              type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Response('Voice Updated.'), 400: openapi.Response('Bad Request')}
    )
    def put(self, request, pk):
        try:
            voice = HappyMomentsSerializer.objects.get(pk=pk)
        except HappyMoments.DoesNotExist:
            return Response({'error': 'Voice Not Found.'}, status=status.HTTP_404_NOT_FOUND)

        concentrates = request.data.get('concentrates', [])
        person_likes = request.data.get('person_likes', [])

        if isinstance(concentrates, str):
            concentrates = list(int(pk) for pk in concentrates.split(',') if pk.isdigit())

        if isinstance(person_likes, str):
            person_likes = list(int(pk) for pk in person_likes.split(',') if pk.isdigit())

        # Create a mutable copy of request.data and update fields
        data = request.data.copy()

        data.setlist('concentrates', concentrates)  # Assign the flat list of integers
        data.setlist('person_likes', person_likes)  # Assign the flat list of integers

        # Use the serializer to update the VoiceOfTheDay object
        serializer = HappyMomentsSerializer(voice, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class HappyPagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'page_size'
    max_page_size = 100


class HappyList(generics.ListAPIView):

    queryset = HappyMoments.objects.filter(block=False).order_by('-create_date')  
    pagination_class = HappyPagination
    serializer_class = HappyMomentsSerializer 

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  
        return context
    def list(self, request, *args, **kwargs):
        if "HAPPYMOMENTS" in BLOCKLIST:
            return Response ("message : Work in progress",status=status.HTTP_426_UPGRADE_REQUIRED)

        return super().list(request, *args, **kwargs)
    
class HappyListForAdmin(generics.ListAPIView):
    queryset = HappyMoments.objects.all().order_by('-create_date')
    serializer_class = HappyMomentsSerializer
    pagination_class = HappyPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @swagger_auto_schema(
        operation_description="Happy Moments List For Admin with optional search and sorting",
        responses={
            200: openapi.Response(description="Happy Moments List"),
            404: openapi.Response(description="No Happy Moments Found.")
        },
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY, description="Filter by title.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'publish_by', openapi.IN_QUERY, description="Filter by publish by.", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'total_likes', openapi.IN_QUERY, description="Filter by total likes.", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'create_date', openapi.IN_QUERY, description="Filter by created date (YYYY-MM-DD).", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'sortby', openapi.IN_QUERY, description="Sort by 'asc' or 'desc' for total likes.", type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_queryset(self):
        list_filter = {
            "title": "title__icontains",
            "publish_by": "publish_by__nick_name__icontains",
            "total_likes": "total_likes",
            "create_date": "create_date__gte",
        }
        queryset = super().get_queryset()

        # Filter by create_date range
        if created_date_last := self.request.query_params.get("create_date", None):
            input_date = parse_date(created_date_last)
            last_date = input_date + timedelta(days=1)
            queryset = queryset.filter(create_date__lte=last_date)
        
        # Apply filters
        queryset = filter_utils(queryset=queryset, filter_dict=list_filter, obj=self)

        # Apply sorting
        sortby = self.request.query_params.get("sortby", None)
        if sortby:
            if sortby.lower() == "asc":
               queryset = queryset.order_by("total_likes")
            elif sortby.lower() == "desc":
               queryset = queryset.order_by("-total_likes")
        else:
           queryset = queryset.order_by("-create_date")

        return queryset



class VoiceDeleteApi(generics.DestroyAPIView):
    queryset = HappyMoments.objects.all()
    serializer_class = HappyMomentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Voice of the Day deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except HappyMoments.DoesNotExist:
            return Response(
                {"message": "Voice of the Day not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class HappyLikePost(APIView):
  
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='Post Id'),
                
            }
        ),
        responses={200: openapi.Response('success'), 400: openapi.Response('Bad Request')}
    )
    def post(self,request):
        id = request.data.get("id")
        try:
            happy_obj = HappyMoments.objects.prefetch_related("person_likes").get(id=id)
        except HappyMoments.DoesNotExist:
            return Response({"msg":"post with this id not found"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("unknow error in finding id of voice of the day",exc_info=True)
            return Response({"msg":"Unknow error"},status=status.HTTP_400_BAD_REQUEST)

        try:
            teens_obj = TeenagerAndParent.objects.get(account=request.user)
        except TeenagerAndParent.DoesNotExist:
            logger.error(f"unknow error in finding User from id {request.user.id}",exc_info=True)
            return Response({"msg":"User is not Teens or Parent"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"unknow error in finding User from id {request.user.id}",exc_info=True)
            return Response({"msg":"Unknow error"},status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            teens_obj = TeenagerAndParent.objects.get(account=request.user)
            logger.debug(f"{teens_obj.__dict__}")
            # user = Accounts.objects.get()
            # logger.debug(f"{user=}")
            # send_notification(user, "You have checked the doclist!")
            logger.debug("a")
        except Exception as e :
            logger.debug("a")
        
        if teens_obj in happy_obj.person_likes.all():
            happy_obj.person_likes.remove(teens_obj)
            
            happy_obj.total_likes = max(0,happy_obj.total_likes - 1) 
            happy_obj.save()
            
        else:
            happy_obj.person_likes.add(teens_obj)
            happy_obj.total_likes = happy_obj.total_likes + 1
            happy_obj.save()
        return Response({"success":True},status=status.HTTP_200_OK)
    




class ListHappyMomentReportsView(generics.ListAPIView):
    serializer_class = HappyMomentSerializer
    pagination_class = HappyPagination
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Filter HappyMoments that have associated reports (no reports = exclude)
        queryset = HappyMoments.objects.filter(reports__isnull=False,block = False).distinct().order_by('-create_date')

        # Optionally, apply other filters if needed
        list_filter = {
            "title": "title__icontains",
            "create_date": "create_date__date",
        }

        # Apply filter logic if required (filter_utils is assumed to handle query filtering)
        queryset = filter_utils(queryset=queryset, filter_dict=list_filter, obj=self)

        return queryset




class ReportHappyMomentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'happy_moment': openapi.Schema(type=openapi.TYPE_INTEGER, description='The ID of the happy moment being reported'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the report'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the report'),
            },
            required=['happy_moment', 'title', 'description'],  # Specify the required fields
        ),
        responses={
            201: openapi.Response('Report created successfully.'),
            400: openapi.Response('Bad Request'),
        }
    )
    def post(self, request):
        report_data = {
            'happy_moment': request.data.get('happy_moment'),
            'title': request.data.get('title'),
            'description': request.data.get('description'),
        }

        serializer = HappyMomentReportSerializer(data=report_data,context={'user': request.user})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"detail": "Report created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    

class BlockHappyMomentView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        try:
            # Find the HappyMoment instance based on the provided pk
            happy_moment = HappyMoments.objects.get(pk=pk)
        except HappyMoments.DoesNotExist:
            # Return a 404 error if the HappyMoment with the provided pk is not found
            return Response({"detail": "HappyMoment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Block the HappyMoment by setting its block field to True
        happy_moment.block = True
        happy_moment.save()

        # Return a success response
        return Response({"detail": "Happy Moment has been blocked."}, status=status.HTTP_200_OK)