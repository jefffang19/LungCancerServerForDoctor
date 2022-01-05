from django.http import HttpResponse
from django.shortcuts import render
from run_model.forms import UploadFileForm
from run_model.models import Case
import os
import shutil
from django.utils import timezone
import uuid
from .model_query import *
from .history_controller import *

SAVE_FILE_PATH = 'run_model/static/run_model/uploaded_files/'


def handle_uploaded_file(f, fname):
    with open(os.path.join(SAVE_FILE_PATH, fname), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def upload_page(request):

    # POST (show file)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        # handle upload file
        if form.is_valid():
            # generate UUID
            generated_UUID = uuid.uuid4().hex
            file_type = request.FILES['file'].name.split('.')[-1]

            # save image file
            handle_uploaded_file(
                request.FILES['file'], generated_UUID + '.' + file_type)

            # save this record
            SEX_CHOICE = (
                "Female",
                "Male",
                "Other",
            )
            description = "<p>Age:{}</p><p>Gender:{}</p><p>Tumer Location:{}</p>".format(
                request.POST['age'], SEX_CHOICE[int(request.POST['gender'])], request.POST['tumer_location'])

            case = Case(description=description, upload_time=timezone.now(
            ), inference_time=timezone.now(), inner_uuid=generated_UUID, origin_file_name=request.FILES['file'].name, file_path=SAVE_FILE_PATH, file_type=file_type)
            case.save()

            # create a model query
            create_query([case])

            # redirect to history page
            return history(request)
        else:
            return HttpResponse("form is not valid")
    # GET (to upload file)
    else:
        form = UploadFileForm()

        return render(request, 'run_model/upload_case.html', {'form': form})


def download_sample(request, filenum):
    '''
    A controller to let you download sample input image file
    '''
    import os

    file_paths = [
        'sample_images/0.jpg',
        'sample_images/1.jpg',
        'sample_images/2.png',
    ]

    with open(file_paths[filenum], 'rb') as fh:
        response = HttpResponse(
            fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + \
            os.path.basename(file_paths[filenum])
        return response
