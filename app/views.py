import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, Sum
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView
from django.utils.translation import gettext_lazy as _
from .forms import *


class AppListView(PermissionRequiredMixin, ListView):
    paginate_by = 10

    @staticmethod
    def get_required_object_permissions(model_cls):
        return '{0}.view_{1}'.format(getattr(model_cls, '_meta').app_label, getattr(model_cls, '_meta').model_name)

    def get_permission_required(self):
        if self.permission_required is None:
            if self.model is None:
                raise ImproperlyConfigured(
                    '{0} is missing the model attribute.'.format(self.__class__.__name__)
                )
            else:
                self.permission_required = self.get_required_object_permissions(self.model)
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms


class AppDetailView(PermissionRequiredMixin, DetailView):

    @staticmethod
    def get_required_object_permissions(model_cls):
        return '{0}.view_{1}'.format(getattr(model_cls, '_meta').app_label, getattr(model_cls, '_meta').model_name)

    def get_permission_required(self):
        if self.permission_required is None:
            if self.model is None:
                raise ImproperlyConfigured(
                    '{0} is missing the model attribute.'.format(self.__class__.__name__)
                )
            else:
                self.permission_required = self.get_required_object_permissions(self.model)
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms


class AppUpdateView(PermissionRequiredMixin, UpdateView):

    @staticmethod
    def get_required_object_permissions(model_cls):
        return '{0}.change_{1}'.format(getattr(model_cls, '_meta').app_label, getattr(model_cls, '_meta').model_name)

    def get_permission_required(self):
        if self.permission_required is None:
            if self.model is None:
                raise ImproperlyConfigured(
                    '{0} is missing the model attribute.'.format(self.__class__.__name__)
                )
            else:
                self.permission_required = self.get_required_object_permissions(self.model)
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms


class AppView(PermissionRequiredMixin, View):
    permission_required = None

    def get_permission_required(self):
        if self.permission_required:
            if isinstance(self.permission_required, str):
                perms = (self.permission_required,)
            else:
                perms = self.permission_required
        else:
            perms = ()
        return perms


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


class ServiceRecordView(AppListView):
    template_name = 'service_record_list.html'
    model = ServiceRecord
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = _('服务记录')
        context['total_count'] = self.get_queryset().count()
        return context


class ServiceStaticView(AppListView):
    template_name = 'service_static.html'
    model = ServiceItem
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(Q(served_by__name=q) | Q(served_by__mobile=q) | Q(name=q))
        date_start = self.request.GET.get('date_start')
        if date_start:
            date_start = date_value(date_start)
            if date_start:
                queryset = queryset.filter(datetime_created__gte=date_start).distinct()
        date_end = self.request.GET.get('date_end')
        if date_end:
            date_end = date_value(date_end)
            if date_end:
                queryset = queryset.filter(Q(
                    related_service_record__reserve_time__lte=date_end) | Q(
                    related_service_record__datetime_created__lte=date_end
                )).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = _('服务统计')
        context['total_count'] = self.get_queryset().count()
        static_by_sales_query = self.get_queryset().values(
            "served_by__name"
        ).annotate(Sum("price"), Sum("cost")).order_by()
        static_by_sales_data = []
        static_by_profits_data = []
        if static_by_sales_query:
            for item in static_by_sales_query:
                served_by__name = item['served_by__name']
                if not served_by__name:
                    served_by__name = '未知'
                if item['price__sum']:
                    sales = round(float(item['price__sum']), 2)
                else:
                    sales = 0
                if item['cost__sum']:
                    costs = round(float(item['cost__sum']), 2)
                else:
                    costs = 0
                static_by_sales_data.append({
                    'name': served_by__name,
                    'y': sales
                })
                static_by_profits_data.append({
                    'name': served_by__name,
                    'y': sales - costs
                })
        context['static_by_sales'] = json.dumps(static_by_sales_data)
        context['static_by_profits'] = json.dumps(static_by_profits_data)
        return context


class ServiceRecordDetailView(AppView):
    template_name = 'service_record_detail.html'
    permission_required = ('app.change_serviceitem', )

    def get(self, request, pk):
        obj = get_object_or_404(ServiceRecord, pk=pk)
        model_formset_cls = modelformset_factory(model=ServiceItem, form=ServiceItemForm, extra=0)
        queryset = ServiceItem.objects.filter(related_service_record_id=pk)
        min_pk = ServiceRecord.objects.values('pk').order_by('pk').first()
        max_pk = ServiceRecord.objects.values('pk').order_by('-pk').first()
        next_url = None
        has_next = False
        prev_url = None
        has_prev = False
        if max_pk:
            if int(pk) < int(max_pk['pk']):
                next_pk = str(int(pk) + 1)
                next_url = reverse('page:service_record_detail', args=[next_pk])
                has_next = True
        if min_pk:
            if int(pk) > int(min_pk['pk']):
                prev_pk = str(int(pk) - 1)
                prev_url = reverse('page:service_record_detail', args=[prev_pk])
                has_prev = True
        formset = model_formset_cls(queryset=queryset)
        if len(formset) > 0:
            has_data = True
        else:
            has_data = False
        context = {
            'object': obj,
            'formset': formset,
            'has_prev': has_prev,
            'prev_url': prev_url,
            'has_next': has_next,
            'next_url': next_url,
            'back': reverse('page:service_records'),
            'has_data': has_data
        }
        return render(request, self.template_name, context=context)

    def post(self, request, pk):
        model_formset_cls = modelformset_factory(model=ServiceItem, form=ServiceItemForm, extra=0)
        formset = model_formset_cls(request.POST)
        if formset.is_valid():
            formset.save()
        return redirect(request.path)
