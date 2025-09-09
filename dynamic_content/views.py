
from rest_framework import viewsets, filters,views, generics, permissions
from .models import DynamiContent
from .serializers import DynamiContentSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from utils.filter_utils import filter_utils
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import make_aware
from datetime import datetime


class DynamicContentPagination(PageNumberPagination):
    page_size = 1  
    page_size_query_param = 'page_size'
    max_page_size = 100  

class DynamiContentViewSet(viewsets.ModelViewSet):
    queryset = DynamiContent.objects.all()
    serializer_class = DynamiContentSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter]  
    search_fields = ['name', 'content', 'create_date']
    pagination_class = DynamicContentPagination

    @swagger_auto_schema(
        operation_description="List of dynamic content with optional search",
        manual_parameters=[
            openapi.Parameter(
                'name', openapi.IN_QUERY,
                description="Filter by name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'content', openapi.IN_QUERY,
                description="Filter by content",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'create_date', openapi.IN_QUERY,
                description="Filter dynamic content from this created_date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            # If you want search in general, add it as a parameter too
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search for dynamic content by name, content, or create date",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(description="List of dynamic content"),
            404: openapi.Response(description="No dynamic content found."),
        }
    )
    def list(self, request, *args, **kwargs):
        

        return super().list(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update','destroy','create']:
            return [permissions.IsAdminUser()]  
        return super().get_permissions() 
      
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        list_filter = {
            "name": "name__icontains", 
            "content": "content__icontains", 
            "create_date": "create_date__date"
        } 
 
        queryset = filter_utils(queryset=queryset, filter_dict=list_filter, obj=self)  
        return queryset
    


class Tech(views.APIView):
    authentication_classes = []
    def get(self,request):
        return Response({"list":["pranav","jay","praveen","sta",'Tech']})
    

