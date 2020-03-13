from django.views.generic import CreateView, TemplateView
from .forms import *


class ServiceApplyCreateView1(CreateView):
    model = ServiceApply
    form_class = ServiceApplyForm1
    template_name_suffix = '/add_serviceapply_1'
    success_url = '/page/success/'


class ServiceApplyCreateView2(CreateView):
    model = ServiceApply
    form_class = ServiceApplyForm2
    template_name_suffix = '/add_serviceapply_2'
    success_url = '/page/success/'


class InsuranceApplyCreateView1(CreateView):
    model = InsuranceApply
    form_class = InsuranceApplyForm1
    template_name_suffix = '/add_insuranceapply_1'
    success_url = '/page/success/'


class InsuranceApplyCreateView2(CreateView):
    model = InsuranceApply
    form_class = InsuranceApplyForm2
    template_name_suffix = '/add_insuranceapply_2'
    success_url = '/page/success/'


class InsuranceApplyCreateView3(CreateView):
    model = InsuranceApply
    form_class = InsuranceApplyForm3
    template_name_suffix = '/add_insuranceapply_3'
    success_url = '/page/success/'


class PartnerApplyCreateView(CreateView):
    model = PartnerApply
    form_class = PartnerApplyForm
    template_name_suffix = '/add_partnerapply'
    success_url = '/page/success/'


class SuccessView(TemplateView):
    template_name = 'success.html'
