from django.http import HttpResponse
from django.shortcuts import render

# hello world of django


def hello(request):
    return HttpResponse("hello world")


def hello_template(request):
    context = {"Hello": 'Hello'}

    return render(request, 'run_model/test_index.html', context)
