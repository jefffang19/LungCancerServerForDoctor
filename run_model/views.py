from django.shortcuts import render
from .controllers.upload_file import *
from .controllers.model_query import *
from .controllers.template_controller import *
from .controllers.history_controller import *
from .controllers.result_controller import *
from .controllers.feedback_controller import *

# Create your views here.


def get_csrf_token(request):
    return render(request, 'run_model/get_csrf_token.html')
