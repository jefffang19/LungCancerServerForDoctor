from django.shortcuts import render
from run_model.models import Case, Modelquery, Modelpredict, Feedback
import os
import numpy as np

# threshold of nodule probability
PROB_TRHESH = 0.7


def show_result(request, case_id):
    '''
    display model predict results
    '''
    # get wanted case
    case = Case.objects.get(pk=case_id)

    # get image information
    template_dict = {'id': case_id, 'description': case.description,
                     'upload_time': case.upload_time, 'image_name': case.origin_file_name,
                     'origin_image_path': os.path.join(case.file_path[9:], case.inner_uuid) + '.' + case.file_type}

    # get predict result
    mp = Modelpredict.objects.get(case=case)

    # get predict information
    template_dict['p0'], template_dict['p1'], template_dict['p2'], template_dict[
        'p3'] = mp.predict_prob_0, mp.predict_prob_1, mp.predict_prob_2, mp.predict_prob_3
    template_dict['p4'], template_dict['p5'], template_dict['p6'], template_dict[
        'p7'] = mp.predict_prob_4, mp.predict_prob_5, mp.predict_prob_6, mp.predict_prob_7
    template_dict['p8'], template_dict['p9'], template_dict['p10'], template_dict[
        'p11'] = mp.predict_prob_8, mp.predict_prob_9, mp.predict_prob_10, mp.predict_prob_11
    template_dict['p12'], template_dict['p13'], template_dict['p14'], template_dict[
        'p15'] = mp.predict_prob_12, mp.predict_prob_13, mp.predict_prob_14, mp.predict_prob_15

    # get patches saved location
    template_dict['patch_loc'] = mp.predict_path[9:].replace("\\", '/')

    # calculate model statistic
    prob = [mp.predict_prob_0, mp.predict_prob_1, mp.predict_prob_2, mp.predict_prob_3, mp.predict_prob_4, mp.predict_prob_5, mp.predict_prob_6, mp.predict_prob_7,
            mp.predict_prob_8, mp.predict_prob_9, mp.predict_prob_10, mp.predict_prob_11, mp.predict_prob_12, mp.predict_prob_13, mp.predict_prob_14, mp.predict_prob_15]
    template_dict['prob'] = prob
    prob = np.array(prob)

    template_dict['positive_count'] = np.where(prob > PROB_TRHESH, 1, 0).sum()
    template_dict['positive_count_rate'] = np.where(
        prob > PROB_TRHESH, 1, 0).sum() / 16 * 100
    template_dict['highest_prob'] = np.max(prob) * 100
    template_dict['average_prob'] = np.where(
        prob > PROB_TRHESH, prob, 0).sum() / np.where(prob > PROB_TRHESH, 1, 0).sum() * 100
    template_dict['pos_thresh'] = PROB_TRHESH * 100

    # get comment
    feedback = Feedback.objects.filter(case=case)

    if len(feedback) == 1:
        template_dict['comment'] = feedback[0].comment
        template_dict['is_incorrect'] = 1 if feedback[0].is_incorrect else 0
        template_dict['is_difficult'] = 1 if feedback[0].is_difficult else 0
        template_dict['report_missed'] = 1 if feedback[0].report_missed else 0
    else:
        template_dict['comment'] = ''
        template_dict['is_incorrect'] = 0
        template_dict['is_difficult'] = 0
        template_dict['report_missed'] = 0

    return render(request, 'run_model/show_result.html', template_dict)


def show_raw_origin_image(request, case_id):
    '''
    display raw origin  xray image
    '''
    # get wanted case
    case = Case.objects.get(pk=case_id)

    template_dict = {'path': os.path.join(
        case.file_path[9:], case.inner_uuid) + '.' + case.file_type}

    return render(request, 'run_model/origin_raw.html', template_dict)
