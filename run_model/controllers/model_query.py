from run_model.models import Case, Modelquery
from datetime import datetime
from django.http import HttpResponse
import subprocess
import os


def create_query(list_of_cases, show_output=True):
    '''
    list_of_cases: a list of Case object
    '''
    # create query of cases in Modelquery table
    for case in list_of_cases:
        Modelquery(case=case, state=1, start_time=datetime.now(),
                   end_time=datetime.now()).save()

        # run the subprocess of inference.py, and DON't wait
        process = subprocess.Popen(
            ['python', 'run_model/pytorch/inference.py', os.path.join(case.file_path, case.inner_uuid + '.' + case.file_type), str(case.pk)])


def update_query(request):
    # POST
    if request.method == 'POST':
        # get the query that i want to upate
        mq = Modelquery.objects.get(case__pk=request.POST['case_id'])
        # update
        mq.state = request.POST['state']
        mq.end_time = datetime.now()

        mq.save()

        return HttpResponse('query update complete')
    else:
        return HttpResponse('wrong method')
