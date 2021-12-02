from django.shortcuts import render
from run_model.models import Case, Modelquery, Modelpredict
import numpy as np
import os


def history(request):
    # get table content
    image_path, inference_status, image_name, description, nodule_prob, upload_time, difficult_case, ids = [
    ], [], [], [], [], [], [], []

    # get all the cases
    all_cases = Case.objects.all()

    # now get all the informations
    for a_case in all_cases:
        # get prediction
        mp = Modelpredict.objects.filter(case=a_case)

        # append informations
        ids.append(a_case.pk)
        image_path.append(os.path.join(
            a_case.file_path[9:], a_case.inner_uuid) + '.' + a_case.file_type)
        print(os.path.join(
            a_case.file_path[9:], a_case.inner_uuid) + '.' + a_case.file_type)
        image_name.append(a_case.origin_file_name)
        description.append(a_case.description)
        upload_time.append(a_case.upload_time.strftime("%m/%d/%Y, %H:%M:%S"))

        # check if inference done
        if len(mp) == 0:
            inference_status.append('inferencing')
            nodule_prob.append(' ')
        else:
            inference_status.append('Done')
            nodule_prob.append(' ')

        difficult_case.append('Unknown')

    template_dict = {"image_path": image_path, "inference_status": inference_status, "image_name": image_name,
                     "description": description, "nodule_prob": nodule_prob, "upload_time": upload_time, "difficult_case": difficult_case, "ids": ids}

    return render(request, 'run_model/history.html', template_dict)
