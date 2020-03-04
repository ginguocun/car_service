from django.urls import re_path

from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns

from app.apps import AppConfig

from .views import *


API_TITLE = 'API Documents'
API_DESCRIPTION = 'API Information'

app_name = AppConfig.name


urlpatterns = format_suffix_patterns([
    re_path(r'', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    re_path(r'^wx_login/$', WxLoginView.as_view(), name='wx_login'),
])
