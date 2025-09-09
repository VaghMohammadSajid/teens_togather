from django.db import models

# Create your models here.


class DynamiContent(models.Model):
    name = models.CharField(max_length=254,db_index=True,unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to="dynamic_content/", blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name