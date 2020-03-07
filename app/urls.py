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
    re_path(r'^token/$', AppTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 下拉筛选模块接口
    re_path(r'^service_packages/$', ServicePackageListView.as_view(), name='service_packages'),
    re_path(r'^store_infos/$', StoreInfoListView.as_view(), name='store_infos'),
    # 线上提交接口
    re_path(r'^service_applies/$', ServiceApplyListView.as_view(), name='service_applies'),
    re_path(r'^insurance_applies/$', InsuranceApplyListView.as_view(), name='insurance_applies'),
])
