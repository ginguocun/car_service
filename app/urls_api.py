from django.urls import re_path

from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns

from app.apps import AppConfig

from .views_api import *


API_TITLE = 'API Documents'
API_DESCRIPTION = 'API Information'

app_name = AppConfig.name


urlpatterns = format_suffix_patterns([
    re_path(r'', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    re_path(r'^wx_login/$', WxLoginView.as_view(), name='wx_login'),
    re_path(r'^wx_login_gzh/$', WxGzhLoginView.as_view(), name='wx_login_gzh'),
    re_path(r'^token/$', AppTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 下拉筛选模块接口
    re_path(r'^service_package_types/$', ServicePackageTypeListView.as_view(), name='service_package_types'),
    re_path(r'^service_packages/$', ServicePackageListView.as_view(), name='service_packages'),
    re_path(r'^oil_packages/$', OilPackageListView.as_view(), name='oil_packages'),
    re_path(r'^store_infos/$', StoreInfoListView.as_view(), name='store_infos'),
    re_path(r'^insurance_companies/$', InsuranceCompanyListView.as_view(), name='insurance_companies'),
    # 线上提交接口
    re_path(r'^service_applies/$', ServiceApplyListView.as_view(), name='service_applies'),
    re_path(r'^insurance_applies/$', InsuranceApplyListView.as_view(), name='insurance_applies'),
    re_path(r'^partner_applies/$', PartnerApplyListView.as_view(), name='partner_applies'),
    # 积分和余额记录
    re_path(r'^amount_change_records/$', AmountChangeRecordListView.as_view(), name='amount_change_records'),
    re_path(r'^credit_change_records/$', CreditChangeRecordListView.as_view(), name='credit_change_records'),
    # 用户个人信息
    re_path(r'^user_info/$', UserInfoView.as_view(), name='user_info'),
    re_path(r'^update_mobile/$', UpdateMobileView.as_view(), name='update_mobile'),
    re_path(r'^get_code/$', GetCodeView.as_view(), name='get_code'),
])
