from django.shortcuts import render


def index(request):
    return render(request, 'run_model/index.html')


def login(request):
    return render(request, 'run_model/login.html')


def register(request):
    return render(request, 'run_model/register.html')
