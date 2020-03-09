from django.urls import re_path

from app.apps import AppConfig
from app.views import *


app_name = AppConfig.name


urlpatterns = [
    re_path(r'^success/$', SuccessView.as_view(), name='success'),
    re_path(r'^service_apply_1/$', ServiceApplyCreateView1.as_view(), name='service_apply_1'),
    re_path(r'^service_apply_2/$', ServiceApplyCreateView2.as_view(), name='service_apply_2'),
    ]
