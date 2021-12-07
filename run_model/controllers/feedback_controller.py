from run_model.models import Case, Feedback
import numpy as np
import os
from django.http import HttpResponse


def update_feedback(request):
    # POST
    if request.method == 'POST':
        case = Case.objects.get(pk=request.POST['id'])
        is_correct = True if int(request.POST['is_correct']) == 1 else False
        is_difficult = True if int(
            request.POST['is_difficult']) == 1 else False

        # check if Feedback exist
        feedbacks = Feedback.objects.filter(case=case)

        if(len(feedbacks) == 0):  # if not exist, create
            Feedback(case=case, comment=request.POST['comment'],
                     is_incorrect=not is_correct, is_difficult=is_difficult).save()
        else:
            feedbacks[0].comment = request.POST['comment']
            feedbacks[0].is_incorrect = not is_correct
            feedbacks[0].is_difficult = is_difficult
            feedbacks[0].save()

        return HttpResponse('Update Feedback success')
