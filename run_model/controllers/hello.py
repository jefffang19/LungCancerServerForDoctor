from django.http import HttpResponse
from django.shortcuts import render
from ..forms import UploadFileForm
import os
import shutil

# hello world of django


def hello(request):
    return HttpResponse("hello world")

# test show img


def hello_img(request):
    return render(request, 'run_model/test_show_img.html')

# handle an uploaded file


def handle_uploaded_file(f, fname):
    with open(os.path.join('run_model/static/run_model/uploaded_files/', fname + '.png'), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def hello_template(request):
    # test upload file
    context = {"Hello": 'Hello'}

    # POST (show file)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        # handle upload file
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.POST['title'])

            # filename for template to display
            shutil.copyfile(os.path.join('run_model/static/run_model/uploaded_files',
                                         request.POST['title']) + '.png', 'run_model/static/run_model/uploaded_files/uploaded.png')
            return render(request, 'run_model/test_show_uploaded_img.html')
        else:
            return HttpResponse("form is not valid")
    # GET (to upload file)
    else:
        form = UploadFileForm()
        context['form'] = form

        return render(request, 'run_model/test_index.html', context)
