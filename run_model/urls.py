from django.urls import path

from . import views

urlpatterns = [
    # upload file
    # path('upload_page', views.upload_page, name='upload_page'),
    # get csrf token
    path('get_csrf_token', views.get_csrf_token, name='get_csrf_token'),
    # update model query
    path('update_query', views.update_query, name='update_query'),
    # save model predict result
    path('save_result', views.save_result, name='save_result'),
    # save comment
    path('update_comment', views.update_feedback, name='update_comment'),
    # download sample images
    path('download_sample/<int:filenum>',
         views.download_sample, name='download_sample'),
    # template controller
    path('', views.index, name='index'),
    path('history', views.history, name='history'),
    path('history_data', views.history_data, name='history_data'),
    path('upload_case', views.upload_page, name='upload_case'),
    path('show_case/<int:case_id>', views.show_result, name='show_case_id'),
    path('show_raw/<int:case_id>', views.show_raw_origin_image),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
]
