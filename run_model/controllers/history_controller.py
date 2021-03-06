from django.shortcuts import render
from run_model.models import Case, Modelquery, Modelpredict, Feedback
import numpy as np
import os
from django.http import HttpResponse, JsonResponse


def history(request):
    # get table content
    image_path, inference_status, image_name, description, nodule_prob, upload_time, feedbacks, ids = [
    ], [], [], [], [], [], [], []
    need_refresh = 0

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
            need_refresh = 1  # template need need refresh
        else:
            inference_status.append('Done')
            # get probability
            # calculate model statistic
            prob = [mp[0].predict_prob_0, mp[0].predict_prob_1, mp[0].predict_prob_2, mp[0].predict_prob_3, mp[0].predict_prob_4, mp[0].predict_prob_5, mp[0].predict_prob_6, mp[0].predict_prob_7,
                    mp[0].predict_prob_8, mp[0].predict_prob_9, mp[0].predict_prob_10, mp[0].predict_prob_11, mp[0].predict_prob_12, mp[0].predict_prob_13, mp[0].predict_prob_14, mp[0].predict_prob_15]
            prob = np.array(prob)

            nodule_prob.append(prob.max())

        # check if has comment
        feedback = Feedback.objects.filter(case=a_case)

        # no comment
        if(len(feedback) == 0):
            feedbacks.append('No feedback')
        else:
            _feedback = "<p>difficult case: <strong>{}</strong></p><p>predict incorrect : <strong>{}</strong></p><p>report missed nodule: <strong>{}</strong></p><p>comment: <strong>{}</strong></p>".format(
                feedback[0].is_difficult, feedback[0].is_incorrect, feedback[0].report_missed, feedback[0].comment)
            feedbacks.append(_feedback)

    template_dict = {"image_path": image_path, "inference_status": inference_status, "image_name": image_name,
                     "description": description, "nodule_prob": nodule_prob, "upload_time": upload_time, "feedbacks": feedbacks, "ids": ids, "need_refresh": need_refresh}

    return render(request, 'run_model/history.html', template_dict)


def history_data(request):
    # GET
    if request.method == 'GET':
        # get table content
        image_path, inference_status, image_name, description, nodule_prob, upload_time, feedbacks, ids = [
        ], [], [], [], [], [], [], []
        need_refresh = 0

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
            upload_time.append(
                a_case.upload_time.strftime("%m/%d/%Y, %H:%M:%S"))

            # check if inference done
            if len(mp) == 0:
                inference_status.append('inferencing')
                nodule_prob.append(' ')
                need_refresh = 1  # template need need refresh
            else:
                inference_status.append('Done')
                # get probability
                # calculate model statistic
                prob = [mp[0].predict_prob_0, mp[0].predict_prob_1, mp[0].predict_prob_2, mp[0].predict_prob_3, mp[0].predict_prob_4, mp[0].predict_prob_5, mp[0].predict_prob_6, mp[0].predict_prob_7,
                        mp[0].predict_prob_8, mp[0].predict_prob_9, mp[0].predict_prob_10, mp[0].predict_prob_11, mp[0].predict_prob_12, mp[0].predict_prob_13, mp[0].predict_prob_14, mp[0].predict_prob_15]
                prob = np.array(prob)

                nodule_prob.append(prob.max())

            # check if has comment
            feedback = Feedback.objects.filter(case=a_case)

            # no comment
            if(len(feedback) == 0):
                feedbacks.append('No feedback')
            else:
                _feedback = "<p>difficult case: <strong>{}</strong></p><p>predict incorrect : <strong>{}</strong></p><p>report missed nodule: <strong>{}</strong></p><p>comment: <strong>{}</strong></p>".format(
                    feedback[0].is_difficult, feedback[0].is_incorrect, feedback[0].report_missed, feedback[0].comment)
                feedbacks.append(_feedback)

        template_dict = {"image_path": image_path, "inference_status": inference_status, "image_name": image_name,
                         "description": description, "nodule_prob": nodule_prob, "upload_time": upload_time, "feedbacks": feedbacks, "ids": ids, "need_refresh": need_refresh}

        return JsonResponse(template_dict, safe=False)
    # POST
    # filter out some datas
    # get table content
    if request.method == 'POST':
        image_path, inference_status, image_name, description, nodule_prob, upload_time, feedbacks, ids = [
        ], [], [], [], [], [], [], []
        need_refresh = 0

        # get all the cases
        all_cases = Case.objects.all()

        # now get all the informations
        for a_case in all_cases:
            # check if has comment
            feedback = Feedback.objects.filter(case=a_case)

            # no comment
            if(len(feedback) == 0):
                # if filter case condition is 2 (viewed case only)
                if int(request.POST['filter_case']) == 2:
                    continue

                feedbacks.append('No feedback')
            # has feedback, but filter condition is 1
            elif int(request.POST['filter_case']) == 1:
                continue
            else:
                _feedback = "<p>difficult case: <strong>{}</strong></p><p>predict incorrect : <strong>{}</strong></p><p>report missed nodule: <strong>{}</strong></p><p>comment: <strong>{}</strong></p>".format(
                    feedback[0].is_difficult, feedback[0].is_incorrect, feedback[0].report_missed, feedback[0].comment)
                feedbacks.append(_feedback)

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
            upload_time.append(
                a_case.upload_time.strftime("%m/%d/%Y, %H:%M:%S"))

            # check if inference done
            if len(mp) == 0:
                inference_status.append('inferencing')
                nodule_prob.append(' ')
                need_refresh = 1  # template need need refresh
            else:
                inference_status.append('Done')
                # get probability
                # calculate model statistic
                prob = [mp[0].predict_prob_0, mp[0].predict_prob_1, mp[0].predict_prob_2, mp[0].predict_prob_3, mp[0].predict_prob_4, mp[0].predict_prob_5, mp[0].predict_prob_6, mp[0].predict_prob_7,
                        mp[0].predict_prob_8, mp[0].predict_prob_9, mp[0].predict_prob_10, mp[0].predict_prob_11, mp[0].predict_prob_12, mp[0].predict_prob_13, mp[0].predict_prob_14, mp[0].predict_prob_15]
                prob = np.array(prob)

                nodule_prob.append(prob.max())

        template_dict = {"image_path": image_path, "inference_status": inference_status, "image_name": image_name,
                         "description": description, "nodule_prob": nodule_prob, "upload_time": upload_time, "feedbacks": feedbacks, "ids": ids, "need_refresh": need_refresh}

        return JsonResponse(template_dict, safe=False)
