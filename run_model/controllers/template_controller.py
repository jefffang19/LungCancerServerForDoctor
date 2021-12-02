from django.shortcuts import render


def index(request):
    return render(request, 'run_model/index.html')


def history(request):
    return render(request, 'run_model/history.html')


def login(request):
    return render(request, 'run_model/login.html')


def register(request):
    return render(request, 'run_model/register.html')


def show_result(request):
    return render(request, 'run_model/show_result.html')
