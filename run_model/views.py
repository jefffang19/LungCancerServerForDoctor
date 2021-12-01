from django.shortcuts import render
from .controllers.hello import *
from .controllers.upload_file import *
from .controllers.model_query import *

# Create your views here.


def get_csrf_token(request):
    return render(request, 'run_model/get_csrf_token.html')
