from django.contrib import admin

# Register your models here.
from .models import MeditationCategory,MeditationAudio

admin.site.register(MeditationCategory)
admin.site.register(MeditationAudio)