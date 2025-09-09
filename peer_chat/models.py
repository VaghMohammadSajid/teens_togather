from django.db import models

from django.db import models
from django.contrib.auth.models import User

# class Room(models.Model):
#     name = models.CharField(max_length=255)  
#     room_id = models.CharField(max_length=100, unique=True)  
#     users = models.ManyToManyField(User, related_name='rooms')  
#     created_at = models.DateTimeField(auto_now_add=True)


#     def __str__(self):
#         return self.name


# class ChatMessage(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)  
#     room = models.ForeignKey(Room, on_delete=models.CASCADE) 
#     message = models.TextField() 
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} ({self.timestamp}): {self.message[:50]}"