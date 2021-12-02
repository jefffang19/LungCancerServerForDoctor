from django.shortcuts import render
from run_model.models import Case, Modelquery, Modelpredict


def show_result(request, case_id):
    # get wanted case
    case = Case.objects.get(pk=case_id)

    # get image information
    template_dict = {'id': case_id, 'description': case.description,
                     'upload_time': case.upload_time, 'image_name': case.origin_file_name}

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
    template_dict['patch_loc'] = mp.predict_path

    return render(request, 'run_model/show_result.html', template_dict)
