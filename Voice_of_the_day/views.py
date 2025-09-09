from gc import is_finalized

from rest_framework import status, generics, permissions,filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from Voice_of_the_day.serializers import VoiceOfTheDaySerializer,VoiceOfTheDayUpdateSerializer,VoiceOfTheDayLimitedSerializer
import logging
from Voice_of_the_day.models import *
from rest_framework.pagination import PageNumberPagination
from utils.filter_utils import filter_utils
from django.utils.dateparse import parse_date

logger = logging.getLogger(__name__)


class VoiceCreatedApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create Voice of the Day",
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
                              type=openapi.TYPE_ARRAY,items=openapi.Items(type=openapi.TYPE_INTEGER)),
            

            
        ],
        responses={201: openapi.Response('Voice Created.'), 400: openapi.Response('Bad Request')}
    )
    def post(self, request):
        data = request.data

        try:
            concentrates_data = data.pop('concentrates')
        except:
            concentrates_data = None
        
        try:
            if concentrates_data is not None:
                concentrate_int_list = [int(x) for x in concentrates_data]
            else:
                concentrate_int_list = []
        except KeyError:
            if concentrates_data is not None:
                concentrate_int_list = [int(x) for x in concentrates_data[0].split(',')]
            else:
                concentrate_int_list = []
        except ValueError:
            if concentrates_data is not None:
                concentrate_int_list = [int(x) for x in concentrates_data[0].split(',')]
            else:
                concentrate_int_list = []
        serializer = VoiceOfTheDaySerializer(data=data,context={"user":request.user,"concentratesss":concentrate_int_list})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response('enter valid data for concentrate', status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class VoiceOfTheDayRetrieveView(generics.RetrieveAPIView):
    queryset = VoiceOfTheDay.objects.all()
    serializer_class = VoiceOfTheDayLimitedSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve Voice of the Day by ID",
        responses={
            200: VoiceOfTheDaySerializer,
            404: openapi.Response(description="Voice Not Found."),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



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
            
            
        ],
        responses={200: openapi.Response('Voice Updated.'), 400: openapi.Response('Bad Request')}
    )
    def put(self, request, pk):
        try:
            voice = VoiceOfTheDay.objects.get(pk=pk)
        except VoiceOfTheDay.DoesNotExist:
            return Response({'error': 'Voice Not Found.'}, status=status.HTTP_404_NOT_FOUND)

        concentrates = request.data.get('concentrates', [])
        person_likes = request.data.get('person_likes', [])

        if isinstance(concentrates, str):
            concentrates = list(int(pk) for pk in concentrates.split(',') if pk.isdigit())

        if isinstance(person_likes, str):
            person_likes = list(int(pk) for pk in person_likes.split(',') if pk.isdigit())

        
        data = request.data.copy()

        data.setlist('concentrates', concentrates)  
        data.setlist('person_likes', person_likes)  

        
        serializer = VoiceOfTheDayUpdateSerializer(voice, data=data, partial=True, context={'request': request,"user":request.user})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VoiceOfTheDayPagination(PageNumberPagination):
    page_size = 1  
    page_size_query_param = 'page_size'
    max_page_size = 100

class VoiceOfTheDayListView(generics.ListAPIView):
    queryset = VoiceOfTheDay.objects.all().order_by('-create_date')
    serializer_class = VoiceOfTheDayLimitedSerializer
    pagination_class = VoiceOfTheDayPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content", "create_date"]

    @swagger_auto_schema(
        operation_description="List of voices with optional search",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search query to filter by Voice of day details",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'title', openapi.IN_QUERY,
                description="Filter by title",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'content', openapi.IN_QUERY,
                description="Filter by content",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'create_date', openapi.IN_QUERY,
                description="Filter voice of day from this created_date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            )
        ],
        responses={
            200: openapi.Response(description="List of voices"),
            404: openapi.Response(description="No Voice Data Found."),
        }
    )
    def get(self, request, *args, **kwargs):
       
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  
        return context

    def get_queryset(self):
        list_filter = {"title": "title__icontains", "content": "content__icontains", "create_date": "create_date"}
        queryset = super().get_queryset()

        queryset = filter_utils(queryset=queryset, filter_dict=list_filter, obj=self)

        return queryset


class VoiceOfTheDayListForAdminView(generics.ListAPIView):
    queryset = VoiceOfTheDay.objects.all().order_by('-create_date')
    serializer_class = VoiceOfTheDaySerializer
    pagination_class = VoiceOfTheDayPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content", "create_date"]

    @swagger_auto_schema(
        operation_description="List of voices with optional search",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search query to filter by Voice of day details",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'title', openapi.IN_QUERY,
                description="Filter by title",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'content', openapi.IN_QUERY,
                description="Filter by content",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'create_date', openapi.IN_QUERY,
                description="Filter voice of day from this created_date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            )
        ],
        responses={
            200: openapi.Response(description="List of voices"),
            404: openapi.Response(description="No Voice Data Found."),
        }
    )
    def get(self, request, *args, **kwargs):
       
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  
        return context

    def get_queryset(self):
        list_filter = {"title": "title__icontains", "content": "content__icontains", "create_date": "create_date"}
        queryset = super().get_queryset()

        queryset = filter_utils(queryset=queryset, filter_dict=list_filter, obj=self)

        return queryset


class VoiceDeleteApi(generics.DestroyAPIView):
    queryset = VoiceOfTheDay.objects.all()
    serializer_class = VoiceOfTheDaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Voice of the Day deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        except VoiceOfTheDay.DoesNotExist:
            return Response(
                {"message": "Voice of the Day not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class VoiceLikePost(APIView):
    
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
            voice_of_the_daya_obj = VoiceOfTheDay.objects.prefetch_related("person_likes").get(id=id)
        except VoiceOfTheDay.DoesNotExist:
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
        
        if teens_obj in voice_of_the_daya_obj.person_likes.all():
            voice_of_the_daya_obj.person_likes.remove(teens_obj)
            
            voice_of_the_daya_obj.total_likes = max(0,voice_of_the_daya_obj.total_likes - 1) 
            voice_of_the_daya_obj.save()
            
        else:
            voice_of_the_daya_obj.person_likes.add(teens_obj)
            voice_of_the_daya_obj.total_likes = voice_of_the_daya_obj.total_likes + 1
            voice_of_the_daya_obj.save()
        return Response({"success":True},status=status.HTTP_200_OK)


