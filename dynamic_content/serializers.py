from rest_framework import serializers
from .models import DynamiContent

class DynamiContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamiContent
        fields = ['id', 'name', 'content', 'image','create_date']