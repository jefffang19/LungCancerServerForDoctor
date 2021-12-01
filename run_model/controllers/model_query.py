from run_model.models import Case, Modelquery, Modelpredict
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


def update_query(request):
    # POST
    if request.method == 'POST':
        # get the query that i want to upate
        mq = Modelquery.objects.get(case__pk=request.POST['case_id'])
        # update
        mq.state = request.POST['state']
        mq.end_time = timezone.now()

        mq.save()

        return HttpResponse('query update complete')
    else:
        return HttpResponse('wrong method')


def save_result(request):
    # POST
    if request.method == 'POST':
        # get the query that i want to upate
        case = Case.objects.get(pk=request.POST['case_id'])
        # save the predict confidence
        Modelpredict(case=case, predict_path=request.POST['path'],
                     predict_prob_0=request.POST['p0'], predict_prob_1=request.POST[
            'p1'], predict_prob_2=request.POST['p2'], predict_prob_3=request.POST['p3'],
            predict_prob_4=request.POST['p4'], predict_prob_5=request.POST[
            'p5'], predict_prob_6=request.POST['p6'], predict_prob_7=request.POST['p7'],
            predict_prob_8=request.POST['p8'], predict_prob_9=request.POST[
            'p9'], predict_prob_10=request.POST['p10'], predict_prob_11=request.POST['p11'],
            predict_prob_12=request.POST['p12'], predict_prob_13=request.POST['p13'], predict_prob_14=request.POST['p14'], predict_prob_15=request.POST['p15']).save()

        return HttpResponse('save result to DB complete')
    else:
        return HttpResponse('wrong method')
