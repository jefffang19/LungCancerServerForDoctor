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
            # get probability
            # calculate model statistic
            prob = [mp[0].predict_prob_0, mp[0].predict_prob_1, mp[0].predict_prob_2, mp[0].predict_prob_3, mp[0].predict_prob_4, mp[0].predict_prob_5, mp[0].predict_prob_6, mp[0].predict_prob_7,
            mp[0].predict_prob_8, mp[0].predict_prob_9, mp[0].predict_prob_10, mp[0].predict_prob_11, mp[0].predict_prob_12, mp[0].predict_prob_13, mp[0].predict_prob_14, mp[0].predict_prob_15]
            prob = np.array(prob)

            nodule_prob.append(prob.max())

        difficult_case.append('Unknown')

    template_dict = {"image_path": image_path, "inference_status": inference_status, "image_name": image_name,
                     "description": description, "nodule_prob": nodule_prob, "upload_time": upload_time, "difficult_case": difficult_case, "ids": ids}

    return render(request, 'run_model/history.html', template_dict)
