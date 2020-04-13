from .models import *
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, Textarea, DateInput, CheckboxInput,\
    ModelMultipleChoiceField, Select, DateTimeInput, TimeInput


class AppModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AppModelForm, self).__init__(*args, **kwargs)
        if self.fields:
            for k, v in self.fields.items():
                v.widget.attrs.update({'class': 'form-control'})
                if isinstance(v.widget, DateTimeInput):
                    v.widget.attrs.update(
                        {'class': 'form-control datetime-auto'})
                if isinstance(v.widget, DateInput):
                    v.widget.attrs.update(
                        {'class': 'form-control date-auto', 'placeholder': '2020-01-01'})
                if isinstance(v.widget, Select):
                    v.widget.attrs.update(
                        {'class': 'selectpicker show-tick form-control', 'data-live-search': 'true'})
                if isinstance(v.widget, TimeInput):
                    v.widget.attrs.update(
                        {'class': 'form-control time-auto'})
                if isinstance(v.widget, Textarea):
                    v.widget.attrs.update({'class': 'form-control summernote'})
                if isinstance(v.widget, CheckboxInput):
                    v.widget.attrs.update({'type': 'checkbox'})

    def save(self, commit=True):
        return super(AppModelForm, self).save(commit)


class ServiceApplyForm1(AppModelForm):
    # 上门服务

    class Meta:
        model = ServiceApply
        fields = [
            'car_number', 'car_brand', 'car_model', 'name', 'mobile', 'oil_package',
            'service_package', 'reserve_type', 'reserve_time', 'reserve_address'
        ]


class ServiceApplyForm2(AppModelForm):
    # 到店服务

    class Meta:
        model = ServiceApply
        fields = [
            'car_number', 'car_brand', 'car_model', 'name', 'mobile', 'oil_package',
            'service_package', 'reserve_type', 'reserve_time', 'related_store'
        ]


class InsuranceApplyForm1(AppModelForm):
    # 车辆续保

    class Meta:
        model = InsuranceApply
        fields = [
            'car_number', 'car_brand', 'car_model',
            'name', 'mobile',
            'service_type', 'insurance_date',
            'insurance_csx', 'insurance_fdjss', 'insurance_zrss', 'insurance_dqx', 'insurance_pl',
            'insurance_cshx', 'insurance_dsxr', 'insurance_sj', 'insurance_ck', 'insurance_hw',
            'insurance_company',
            'notes'
        ]


class InsuranceApplyForm2(AppModelForm):
    # 保险分期

    class Meta:
        model = InsuranceApply
        fields = [
            'car_number', 'car_brand', 'car_model',
            'name', 'mobile',
            'service_type',
            'notes'
        ]


class InsuranceApplyForm3(AppModelForm):
    # 购车贷款

    class Meta:
        model = InsuranceApply
        fields = [
            'car_number', 'car_brand', 'car_model',
            'name', 'mobile',
            'service_type', 'changed_times', 'money_needed',
            'notes'
        ]


class PartnerApplyForm(AppModelForm):
    # 车辆续保

    class Meta:
        model = PartnerApply
        fields = [
            'name', 'mobile', 'address', 'professional', 'reason',
        ]


class ServiceRecordForm(AppModelForm):
    # 服务记录

    class Meta:
        model = ServiceRecord
        fields = [
            'car', 'reserve_type', 'reserve_time', 'finish_time', 'total_price',
            'total_payed', 'total_cost']


class ServiceItemForm(AppModelForm):
    # 服务记录明细

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        readonly_fields = ['name', 'served_by', 'item_price', 'item_count', 'price']
        for f in readonly_fields:
            self.fields[f].widget.attrs.update({'readonly': 'readonly', 'style': 'background-color: lightgrey'})
        self.fields['confirmed_by'].widget.attrs.update({'type': 'hidden'})

    class Meta:
        model = ServiceItem
        fields = ['name', 'served_by', 'item_price', 'item_count', 'price', 'cost', 'notes', 'confirmed_by']
