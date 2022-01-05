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


class Modelpredict(models.Model):
    case = models.OneToOneField(
        Case, on_delete=models.CASCADE, primary_key=True)
    # path of the image patch
    predict_path = models.CharField(max_length=100)
    # prediction confidence of each patch
    predict_prob_0 = models.FloatField()
    predict_prob_1 = models.FloatField()
    predict_prob_2 = models.FloatField()
    predict_prob_3 = models.FloatField()
    predict_prob_4 = models.FloatField()
    predict_prob_5 = models.FloatField()
    predict_prob_6 = models.FloatField()
    predict_prob_7 = models.FloatField()
    predict_prob_8 = models.FloatField()
    predict_prob_9 = models.FloatField()
    predict_prob_10 = models.FloatField()
    predict_prob_11 = models.FloatField()
    predict_prob_12 = models.FloatField()
    predict_prob_13 = models.FloatField()
    predict_prob_14 = models.FloatField()
    predict_prob_15 = models.FloatField()


class Feedback(models.Model):
    case = models.OneToOneField(
        Case, on_delete=models.CASCADE, primary_key=True)

    comment = models.CharField(max_length=500)
    is_incorrect = models.BooleanField()
    is_difficult = models.BooleanField()
    report_missed = models.BooleanField()
