from django.http import HttpResponse

# hello world of django


def hello(request):
    return HttpResponse("hello world")
