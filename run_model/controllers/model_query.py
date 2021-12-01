from run_model.models import Case, Modelquery
from django.utils import timezone
from django.http import HttpResponse
import subprocess
import os


def create_query(list_of_cases, show_output=True):
    '''
    list_of_cases: a list of Case object
    '''
    # create query of cases in Modelquery table
    for case in list_of_cases:
        Modelquery(case=case, state=1, start_time=timezone.now(),
                   end_time=timezone.now()).save()

        # run the subprocess of inference.py, and DON't wait
        process = subprocess.Popen(
            ['python', 'run_model/pytorch/inference.py', os.path.join(case.file_path, case.inner_uuid + '.' + case.file_type), str(case.pk)])
