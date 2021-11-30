from django.db import models

# Create your models here.


class Case(models.Model):
    description = models.CharField(max_length=200)
    upload_time = models.DateTimeField()
    inference_time = models.DateTimeField()
    inner_uuid = models.CharField(max_length=50)
    file_path = models.CharField(max_length=50)
    origin_file_name = models.CharField(max_length=50)
