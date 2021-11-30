from django.urls import path

from . import views

urlpatterns = [
    path('test', views.hello, name='test'),
    path('test_template', views.hello_template, name='test_template'),
    path('test_img', views.hello_img, name='test_img'),
    # upload file
    path('upload_page', views.upload_page, name='upload_page'),
]
