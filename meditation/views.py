from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import MeditationAudio,MeditationCategory
from .serializers import MeditationAudioSerializer,MeditationCategorySerializer
import os
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.filter_utils import filter_utils
from datetime import timedelta
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework import status
from Acoounts.utils import CustomPagination
from Acoounts.apps import BLOCKLIST

class MeditationCategoryCreateView(generics.CreateAPIView):
    queryset = MeditationCategory.objects.all()
    serializer_class = MeditationCategorySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]  
    @swagger_auto_schema(
    operation_description=(
       
       
        "**Example Figma Design:**\n\n"
        "![Figma Screenshot](https://adminoneupv1.stackerbee.com/media/cache/bf/6c/bf6c480479daa6c9604f7ffb19b3e683.jpg)\n\n"
        "### Parameters:\n"
        "- `name`: Name of the doctor.\n"
        "- `about`: Short bio of the doctor.\n"
        "- `image`: Upload a profile picture (e.g., JPG, PNG).\n"
    ),
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                
            },
            required=['name', 'age'],
        ),
    examples={
        "multipart/form-data": {
            "name": "Dr. John Doe",
            "about": "A specialist in dermatology with 10 years of experience.",
            "image": ""
        }
    }
)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeditationCategoryUpdateView(APIView):
    @swagger_auto_schema(
        operation_description="Update a Meditation Category",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Meditation Category Name'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Meditation Category Updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'Id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Meditation Category Id'),
                                'Name': openapi.Schema(type=openapi.TYPE_STRING, description='Meditation Category Name')
                            }
                        )
                    }
                )
            ),
            400: 'Bad Request',
            404: 'Meditation Category Not Found.'
        }
    )
    def put(self, request, pk):
        name = request.data.get('name')

        if not name:
            return Response({"message": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            meditation_category = MeditationCategory.objects.get(pk=pk)
            meditation_category.name = name
            meditation_category.save()
            return Response(
                {"data": {"Id": meditation_category.id, "Name": meditation_category.name},
                 "message": "Meditation Category Updated."},
                status=status.HTTP_200_OK)
        except MeditationCategory.DoesNotExist:
            return Response({"message": "Meditation Category Not Found."}, status=status.HTTP_404_NOT_FOUND)
        except :
            return Response({"message": "Meditation name already exist"}, status=status.HTTP_404_NOT_FOUND)


class MeditationAudioCreateView(generics.CreateAPIView):
    queryset = MeditationAudio.objects.all()
    serializer_class = MeditationAudioSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Upload a new meditation audio file.",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Title of the audio.'),
            openapi.Parameter('audio', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Audio file to upload.'),
            openapi.Parameter('category', openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='Category ID of the audio.'),
        ],
        required=['title', 'audio', 'category'],
        responses={
            201: openapi.Response('Audio created successfully'),
            400: openapi.Response('Bad Request'),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class  MeditationAudioListView(generics.ListAPIView):
    queryset = MeditationAudio.objects.all()
    serializer_class = MeditationAudioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


    @swagger_auto_schema(
        operation_description="Retrieve a list of meditation audio files, optionally filtered by category.",
        manual_parameters=[

            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Current page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter audio files by category ID",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={200: MeditationAudioSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        if "MEDITATION-AUDIO-LIST" in BLOCKLIST:
            return Response ("message : Work in progress",status=status.HTTP_426_UPGRADE_REQUIRED)
        return super().list(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.query_params.get('category', None)
        queryset = super().get_queryset()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset


class  MeditationAudioListForAdminView(generics.ListAPIView):
    queryset = MeditationAudio.objects.all()
    serializer_class = MeditationAudioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


    @swagger_auto_schema(
        operation_description="Retrieve a list of meditation audio files, optionally filtered by category.",
        manual_parameters=[
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Current page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="Filter by title",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter by category",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'created_by',
                openapi.IN_QUERY,
                description="Filter by created by",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'uploaded_at',
                openapi.IN_QUERY,
                description="Filter by created date (YYYY-MM-DD).",
                 type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
            ),
        ],
        responses={200: MeditationAudioSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        list_filter = {"title":"title__icontains","category":"category__name__icontains","created_by":"created_by__username__icontains","uploaded_at":"uploaded_at__gte"}
        queryset = super().get_queryset()

        if  created_date_last := self.request.query_params.get("uploaded_at", None):
            input_date = parse_date(created_date_last)
            last_date = input_date + timedelta(days=1)
            queryset = queryset.filter(uploaded_at__lte=last_date)
        
        queryset = filter_utils(queryset=queryset,filter_dict=list_filter,obj=self)

        return queryset
     






class MeditationAudioStreamInMemoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Stream an audio file by its ID. Supports HTTP Range requests for partial content.",
        manual_parameters=[
            openapi.Parameter(
                'Range',
                openapi.IN_HEADER,
                description="HTTP Range header for partial content requests (e.g., 'bytes=0-').",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: 'Full audio file streamed',
            206: 'Partial audio content',
            404: 'Audio file not found',
        }
    )
    def get(self, request, pk):
        try:
            audio_file = MeditationAudio.objects.get(pk=pk)
        except MeditationAudio.DoesNotExist:
            raise Http404("Audio file not found")

        file_path = audio_file.audio.path
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('Range', '').strip()

        # Create a generator to stream the file in chunks
        def file_iterator(path, start=0, chunk_size=8192):
            with open(path, 'rb') as f:
                f.seek(start)
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield data

        # Handle HTTP Range requests (for seeking)
        if range_header and 'bytes=' in range_header:
            start_range = int(range_header.split('=')[1].split('-')[0])
            response = StreamingHttpResponse(
                file_iterator(file_path, start=start_range),
                status=206
            )
            response['Content-Range'] = f'bytes {start_range}-{file_size - 1}/{file_size}'
        else:
            response = StreamingHttpResponse(file_iterator(file_path), status=200)

        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = file_size
        response['Content-Type'] = 'audio/mpeg'  # Adjust this based on the audio file type
        return response
    

class MeditationCateList(generics.ListAPIView):
    queryset = MeditationCategory.objects.all()
    serializer_class = MeditationCategorySerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination


    @swagger_auto_schema(
        operation_description="Retrieve a list of meditation audio files, optionally filtered by category.",
        manual_parameters=[


        ],
        responses={200: MeditationCategorySerializer(many=True)}
    )

    def list(self, request, *args, **kwargs):
        if "MEDITATION-CATE-LIST" in BLOCKLIST:
            return Response ("message : Work in progress",status=status.HTTP_426_UPGRADE_REQUIRED)
        return super().list(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    def get_queryset(self):
        # category_id = self.request.query_params.get('category', None)
        queryset = super().get_queryset()


        # if category_id:
        #     queryset = queryset.filter(category_id=category_id)

        return queryset

class MeditatioCateDeleteApi(generics.DestroyAPIView):
    queryset = MeditationCategory.objects.all()
    serializer_class = MeditationCategorySerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)

            return Response(
                {"message": "Meditation Category deleted successfully."},
                status=status.HTTP_200_OK
            )
        except MeditationCategory.DoesNotExist:
            return Response(
                {"message": "Meditation Category does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        


class DummyApi(APIView):

    def get(self,request):
        data = [x for x in range(100)]
        return Response({"data":data},status=status.HTTP_200_OK)