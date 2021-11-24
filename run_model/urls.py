from django.urls import path

from . import views

urlpatterns = [
    path('test', views.hello, name='test'),
    path('test_template', views.hello_template, name='test_template'),
]
