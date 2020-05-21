from django.urls import re_path

from app.apps import AppConfig
from app.views import *


app_name = AppConfig.name


urlpatterns = [
    re_path(r'^success/$', SuccessView.as_view(), name='success'),
    re_path(r'^service_records/$', ServiceRecordView.as_view(), name='service_records'),
    re_path(r'^service_records/(?P<pk>\d+)/$', ServiceRecordDetailView.as_view(), name='service_record_detail'),
    re_path(r'^service_static/$', ServiceStaticView.as_view(), name='service_static'),
    re_path(r'^insurance_static/$', InsuranceStaticView.as_view(), name='insurance_static'),
    #
    re_path(r'^service_apply_1/$', ServiceApplyCreateView1.as_view(), name='service_apply_1'),  # 上门服务预约
    re_path(r'^service_apply_2/$', ServiceApplyCreateView2.as_view(), name='service_apply_2'),  # 到店服务预约
    re_path(r'^insurance_apply_1/$', InsuranceApplyCreateView1.as_view(), name='insurance_apply_1'),  # 车辆续保
    re_path(r'^insurance_apply_2/$', InsuranceApplyCreateView2.as_view(), name='insurance_apply_2'),  # 保险分期
    re_path(r'^insurance_apply_3/$', InsuranceApplyCreateView3.as_view(), name='insurance_apply_3'),  # 购车贷款
    re_path(r'^partner_apply/$', PartnerApplyCreateView.as_view(), name='partner_apply'),  # 购车贷款
    ]
