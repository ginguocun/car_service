from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from app.models import *

admin.site.site_header = '24h车服务后台管理系统'
admin.site.site_title = '24h车服务'
admin.site.index_title = '24h车服务后台管理系统'


class GeneralModelAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime_created'


class AutoUpdateUserModelAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by')
    date_hierarchy = 'datetime_created'

    def save_model(self, request, instance, form, change):
        user = request.user
        instance = form.save(commit=False)
        if not change or not instance.created_by:
            instance.created_by = user
        instance.confirmed_by = user
        instance.save()
        form.save_m2m()
        return instance


@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'level_code', 'level_name', 'desc']
    list_display_links = ['pk', 'level_code']
    search_fields = ['level_code', 'level_name', 'desc']


@admin.register(Superior)
class SuperiorAdmin(AutoUpdateUserModelAdmin):
    list_display = ['pk', 'name', 'mobile', 'desc', 'user']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'mobile', 'desc']
    autocomplete_fields = ['user']


@admin.register(WxUser)
class WxUserAdmin(UserAdmin):
    readonly_fields = (
        'last_login', 'date_joined',
        'nick_name', 'city', 'province', 'country', 'avatar_url'
    )
    search_fields = [
        'username', 'openid', 'email', 'full_name', 'first_name', 'last_name', 'nick_name']
    autocomplete_fields = ['user_level']
    list_filter = ('is_partner', 'is_client', 'is_manager', 'is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (_('基础信息'), {'fields': ('username', 'password', 'openid')}),
        (_('个人信息'), {'fields': (
            'nick_name', 'first_name', 'last_name', 'full_name', 'avatar_url',
            'gender', 'date_of_birth', 'desc'
        )}),
        (_('联络信息'), {'fields': ('mobile', 'email',)}),
        (_('地址信息'), {'fields': ('city', 'province', 'country')}),
        (_('分类信息'), {'fields': ('user_level', 'current_credits', 'is_partner', 'is_client', 'is_manager')}),
        (_('权限管理'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        (_('登录信息'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Customer)
class CustomerAdmin(AutoUpdateUserModelAdmin):
    list_display = ['pk', 'name', 'mobile', 'related_superior', 'related_user']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'mobile']
    list_filter = ['related_superior']
    autocomplete_fields = ['related_superior', 'related_user']


@admin.register(CarInfo)
class CarInfoAdmin(AutoUpdateUserModelAdmin):
    list_display = [
        'pk', 'car_number', 'car_brand', 'car_model', 'car_price', 'bought_date', 'desc',
        'is_confirmed', 'is_active', 'customer', 'created_by']
    list_display_links = ['pk', 'car_number']
    list_filter = ['is_active', 'is_confirmed']
    search_fields = ['car_number', 'car_brand', 'car_model', 'customer__name', 'customer__mobile']
    autocomplete_fields = ['customer']
    fieldsets = (
        (_('基础'), {
            'fields': ('car_number', 'customer', 'desc')}),
        (_('车辆详情'), {'fields': ('car_brand', 'car_model', 'car_price', 'bought_date', )}),
        (_('状态'), {'fields': ('is_confirmed', 'is_active')})
    )


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'display', 'is_active']
    search_fields = ['name']
    list_display_links = ['pk', 'name']
    list_filter = ['is_active']


@admin.register(BelongTo)
class BelongToAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    search_fields = ['name']
    list_display_links = ['pk', 'name']


@admin.register(InsuranceRecord)
class InsuranceRecordAdmin(AutoUpdateUserModelAdmin):
    list_display = [
        'pk', 'car', 'record_date', 'insurance_date', 'total_price', 'receiver', 'belong_to', 'insurance_company',
        'tax', 'has_payback', 'payback_percent', 'payback_amount', 'is_payed', 'notes'
    ]
    list_display_links = ['pk', 'car']
    list_filter = ['has_payback', 'belong_to', 'insurance_company']
    date_hierarchy = 'record_date'
    search_fields = ['car__car_number', 'car__customer__name', 'car__customer__mobile']
    autocomplete_fields = ['car', 'receiver', 'belong_to', 'insurance_company']
    fieldsets = (
        (_('基础'), {'fields': ('car', 'record_date', 'insurance_date')}),
        (_('金额'), {'fields': ('total_price', 'tax', 'payback_percent', 'payback_amount', 'has_payback', 'is_payed')}),
        (_('人员'), {'fields': ('receiver', 'belong_to', 'insurance_company')}),
        (_('备注'), {'fields': ('notes',)})
    )


class ServicePackageInline(admin.TabularInline):
    model = ServicePackage
    extra = 0
    fields = ['name', 'desc', 'price', 'is_active']


@admin.register(ServicePackageType)
class ServicePackageTypeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'desc', 'is_active']
    search_fields = ['name', 'desc']
    list_display_links = ['pk', 'name']
    list_filter = ['is_active']
    inlines = [ServicePackageInline]


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'price']
    search_fields = ['name']
    list_display_links = ['pk', 'name']
    autocomplete_fields = ['service_type']


@admin.register(StoreInfo)
class StoreInfoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'address', 'is_active']
    search_fields = ['name']
    list_display_links = ['pk', 'name']
    list_filter = ['is_active']


@admin.register(ServiceRecord)
class ServiceRecordAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'car', 'reserve_type', 'is_reversed', 'reserve_time', 'reserve_address', 'related_store',
        'checked_by', 'is_checked', 'served_by', 'is_served', 'notes'
    ]
    list_display_links = ['pk', 'car']
    list_filter = [
        'is_reversed', 'checked_by', 'served_by', 'is_checked', 'is_served', 'related_store', 'service_package']
    date_hierarchy = 'reserve_time'
    search_fields = ['car__car_number', 'car__customer__name', 'car__customer__mobile']
    autocomplete_fields = ['car', 'checked_by', 'served_by', 'related_store', 'service_package', 'oil_package']
    fieldsets = (
        (_('基础信息'), {'fields': ('car', 'reserve_type', 'reserve_time', 'reserve_address', 'is_reversed')}),
        (_('服务信息'), {
            'fields': (
                'related_store', 'service_package', 'oil_package',
                ('checked_by', 'is_checked'), ('served_by', 'is_served'))}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )


@admin.register(ServiceApply)
class ServiceApplyAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'car_number', 'name', 'mobile', 'is_checked', 'data_import', 'service_package',
        'reserve_type', 'reserve_time', 'reserve_address', 'related_store', 'notes'
    ]
    list_display_links = ['pk', 'car_number']
    list_filter = ['is_checked', 'data_import', 'service_package', 'related_store', 'checked_by']
    date_hierarchy = 'datetime_created'
    search_fields = ['car_number', 'name', 'mobile']
    autocomplete_fields = ['service_package', 'oil_package', 'related_store', 'related_record', 'checked_by']
    fieldsets = (
        (_('车辆信息'), {'fields': ('car_number', 'car_brand', 'car_model', 'name', 'mobile')}),
        (_('审核信息'), {'fields': ('checked_by', 'is_checked', 'data_import')}),
        (_('服务信息'), {
            'fields': (
                'related_store', 'service_package', 'oil_package', 'reserve_type', 'reserve_time',
                'reserve_address', 'related_record')}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )


@admin.register(InsuranceApply)
class InsuranceApplyAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'car_number', 'name', 'mobile',  'is_checked', 'data_import', 'checked_by',
        'insurance_date',  'related_record', 'notes'
    ]
    list_display_links = ['pk', 'car_number']
    list_filter = ['is_checked', 'data_import', 'service_type', 'checked_by']
    date_hierarchy = 'datetime_created'
    search_fields = ['car_number', 'name', 'mobile']
    autocomplete_fields = ['checked_by']
    fieldsets = (
        (_('车辆信息'), {'fields': ('car_number', 'car_brand', 'car_model', 'name', 'mobile', 'insurance_date')}),
        (_('审核信息'), {'fields': ('checked_by', 'is_checked', 'data_import')}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )


@admin.register(OilPackage)
class OilPackageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'price']
    search_fields = ['name']
    list_display_links = ['pk', 'name']


@admin.register(PartnerApply)
class PartnerApplyAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'name', 'mobile', 'address', 'professional', 'reason', 'is_checked', 'notes'
    ]
    list_display_links = ['pk', 'name', 'mobile']
    list_filter = ['is_checked', 'checked_by']
    date_hierarchy = 'datetime_created'
    search_fields = ['name', 'mobile', 'address']
    autocomplete_fields = ['checked_by']
    fieldsets = (
        (_('基本信息'), {'fields': ('name', 'mobile', 'address', 'professional', 'reason')}),
        (_('审核信息'), {'fields': ('checked_by', 'is_checked')}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )
