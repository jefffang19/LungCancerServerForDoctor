from django.db import models

# Create your models here.


class Case(models.Model):
    description = models.CharField(max_length=200)
    upload_time = models.DateTimeField()
    inference_time = models.DateTimeField()
    inner_uuid = models.CharField(max_length=50)
    file_path = models.CharField(max_length=50)
    origin_file_name = models.CharField(max_length=50)
    file_type = models.CharField(max_length=10)


class Modelquery(models.Model):
    case = models.OneToOneField(
        Case, on_delete=models.CASCADE, primary_key=True)
    state = models.IntegerField()  # 0 idle, 1 pendding, 2 finsih, 3 run model error
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
