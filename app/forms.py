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

    class Meta:
        model = ServiceApply
        fields = [
            'car_number', 'car_brand', 'car_model', 'name', 'mobile',
            'service_package', 'reserve_type', 'reserve_time', 'reserve_address'
        ]


class ServiceApplyForm2(AppModelForm):

    class Meta:
        model = ServiceApply
        fields = [
            'car_number', 'car_brand', 'car_model', 'name', 'mobile',
            'service_package', 'reserve_type', 'reserve_time', 'related_store'
        ]