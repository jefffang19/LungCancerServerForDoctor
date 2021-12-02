from django.urls import path

from . import views

urlpatterns = [
    # test url###########
    path('test', views.hello, name='test'),
    # path('test_template', views.hello_template, name='test_template'),
    path('test_img', views.hello_img, name='test_img'),
    ##################
    # upload file
    path('upload_page', views.upload_page, name='upload_page'),
    # get csrf token
    path('get_csrf_token', views.get_csrf_token, name='get_csrf_token'),
    # update model query
    path('update_query', views.update_query, name='update_query'),
    # save model predict result
    path('save_result', views.save_result, name='save_result'),
    # template controller
    path('', views.index, name='index'),
    path('history', views.history, name='history'),
    path('upload_case', views.upload_case, name='upload_case'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
]
