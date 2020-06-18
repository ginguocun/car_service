import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from app.models import *
from car.utils import export_excel

admin.site.site_header = '24h车服务后台管理系统'
admin.site.site_title = '24h车服务'
admin.site.index_title = '24h车服务后台管理系统'


class SimpleModelAdmin(admin.ModelAdmin):
    view_on_site = False


class GeneralModelAdmin(admin.ModelAdmin):
    view_on_site = False
    date_hierarchy = 'datetime_created'


class AutoUpdateUserModelAdmin(admin.ModelAdmin):
    view_on_site = False
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
class UserLevelAdmin(SimpleModelAdmin):
    list_display = ['pk', 'level_code', 'level_name', 'desc']
    list_display_links = ['pk', 'level_code']
    search_fields = ['level_code', 'level_name', 'desc']


@admin.register(Department)
class DepartmentAdmin(AutoUpdateUserModelAdmin):
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']
    search_fields = ['name']


@admin.register(Superior)
class SuperiorAdmin(AutoUpdateUserModelAdmin):
    list_display = ['pk', 'name', 'department', 'position', 'mobile', 'desc', 'user']
    list_display_links = ['pk', 'name']
    search_fields = ['name', 'mobile', 'position', 'desc']
    autocomplete_fields = ['user', 'department']
    list_filter = ['is_active', 'department']


@admin.register(WxUser)
class WxUserAdmin(UserAdmin):
    readonly_fields = (
        'last_login', 'date_joined', 'nick_name', 'city', 'province', 'country', 'avatar_url',
    )
    list_display = [
        'pk', 'username', 'full_name', 'nick_name', 'mobile',
        'is_staff', 'is_superuser', 'date_joined', 'last_login']
    list_display_links = ['pk', 'username', 'full_name', 'nick_name', 'mobile']
    search_fields = [
        'username', 'openid', 'email', 'mobile', 'full_name', 'first_name', 'last_name', 'nick_name']
    autocomplete_fields = ['user_level']
    list_filter = ('is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (_('基础信息'), {'fields': ('username', 'password', 'openid')}),
        (_('个人信息'), {'fields': (
            'nick_name', 'first_name', 'last_name', 'full_name', 'avatar_url', 'gender', 'date_of_birth', 'desc'
        )}),
        (_('联络信息'), {'fields': ('mobile', 'email',)}),
        (_('地址信息'), {'fields': ('city', 'province', 'country')}),
        (_('分类信息'), {'fields': ('user_level', 'is_partner', 'is_client', 'is_manager')}),
        (_('权限管理'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        (_('登录信息'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(PayedRecord)
class PayedRecordAdmin(AutoUpdateUserModelAdmin):
    date_hierarchy = 'payed_date'
    readonly_fields = [
        'credit_change', 'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated',
        'related_service_record',
        'related_insurance_record',
    ]
    list_display = [
        'pk', 'payed_date', 'related_store', 'customer',
        'total_price', 'total_payed', 'amount_payed', 'credit_payed', 'cash_payed', 'is_confirmed',
        'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated']
    list_display_links = ['pk', 'related_store', 'customer', 'total_price', 'total_payed', 'amount_payed']
    search_fields = ['customer__name', 'customer__mobile', 'notes']
    autocomplete_fields = ['related_store', 'customer']
    list_filter = ['is_confirmed']
    list_editable = ['is_confirmed']
    fieldsets = (
        (_('基础信息'), {'fields': (
            'payed_date', 'related_store', 'customer',
            'total_price', 'total_payed', 'amount_payed', 'credit_payed', 'cash_payed', 'is_confirmed')}),
        (_('操作记录'), {'fields': (
            'notes', 'related_service_record', 'related_insurance_record',
            'credit_change', 'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')})
    )

    def save_execl(self, request, queryset):
        filename = 'media/{0}_{1}.xls'.format('payed_record', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        headers = [
            'ID', '姓名', '手机号', '应收金额', '实收金额', '余额抵扣', '积分抵扣',
            '现金支付', '积分变更', '已确认',
            '创建人员', '最后变更人员', '创建日期', '最后更新时间']
        columns = [
            'pk', 'customer__name', 'customer__mobile', 'total_price', 'total_payed', 'amount_payed', 'credit_payed',
            'cash_payed', 'credit_change', 'is_confirmed',
            'created_by__full_name', 'confirmed_by__full_name', 'datetime_created', 'datetime_updated']
        return export_excel(queryset, headers, columns, filename)

    save_execl.short_description = "导出Excel"

    actions = [save_execl]


@admin.register(AmountChangeRecord)
class AmountChangeRecordAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = [
        'current_amounts', 'related_payed_record',
        'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated']
    list_display = [
        'pk', 'customer', 'amounts', 'current_amounts', 'change_type', 'notes',
        'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated']
    list_display_links = ['pk', 'customer', 'amounts', 'current_amounts', 'notes']
    search_fields = ['customer__name', 'customer__mobile']
    list_filter = ['change_type']
    autocomplete_fields = ['customer']
    fieldsets = (
        (_('基础信息'), {'fields': ('change_type', 'customer', 'amounts', 'current_amounts', 'related_payed_record', 'notes')}),
        (_('操作记录'), {'fields': ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')})
    )

    def save_execl(self, request, queryset):
        filename = 'media/{0}_{1}.xls'.format('amounts', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        headers = [
            'ID', '姓名', '手机号', '金额变更', '变更后余额', '变更类型', '创建人员', '最后变更人员', '创建日期', '最后更新时间']
        columns = [
            'pk', 'customer__name', 'customer__mobile', 'amounts', 'current_amounts', 'change_type',
            'created_by__full_name', 'confirmed_by__full_name', 'datetime_created', 'datetime_updated']
        return export_excel(queryset, headers, columns, filename)

    save_execl.short_description = "导出Excel"

    actions = [save_execl]


@admin.register(CreditChangeRecord)
class CreditChangeRecordAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = [
        'current_credits', 'related_payed_record',
        'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated']
    list_display = [
        'pk', 'customer', 'credits', 'current_credits', 'change_type', 'notes',
        'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated']
    list_display_links = ['pk', 'customer', 'credits', 'current_credits', 'notes']
    search_fields = ['customer__name', 'customer__mobile']
    list_filter = ['change_type']
    autocomplete_fields = ['customer']
    fieldsets = (
        (_('基础信息'), {
            'fields': ('customer', 'credits', 'current_credits', 'change_type', 'related_payed_record', 'notes')}),
        (_('操作记录'), {'fields': ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')})
    )

    def save_execl(self, request, queryset):

        filename = 'media/{0}_{1}.xls'.format('credits', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        headers = [
            'ID', '姓名', '手机号', '积分变更', '变更后积分', '变更类型', '创建人员', '最后变更人员', '创建日期', '最后更新时间']
        columns = [
            'pk', 'customer__name', 'customer__mobile', 'credits', 'current_credits', 'change_type',
            'created_by__full_name', 'confirmed_by__full_name', 'datetime_created', 'datetime_updated']
        return export_excel(queryset, headers, columns, filename)

    save_execl.short_description = "导出Excel"

    actions = [save_execl]


@admin.register(CustomerLevel)
class CustomerLevelAdmin(SimpleModelAdmin):
    list_display = ['pk', 'level_code', 'level_name', 'desc']
    list_display_links = ['pk', 'level_code']
    search_fields = ['level_code', 'level_name', 'desc']


@admin.register(Customer)
class CustomerAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = [
        'total_consumption', 'total_consumption_1', 'total_consumption_2', 'total_price', 'total_payed',
        'current_amounts', 'total_credits', 'current_credits', 'created_by', 'confirmed_by',
        'datetime_created', 'datetime_updated']
    list_display = [
        'pk', 'name', 'mobile', 'total_consumption_1', 'total_consumption_2', 'total_price', 'total_payed',
        'current_amounts', 'current_credits', 'customer_level',
        'is_partner', 'related_superior']
    list_display_links = ['pk', 'name', 'mobile']
    search_fields = ['name', 'mobile']
    list_filter = ['related_superior', 'customer_level', 'is_partner']
    autocomplete_fields = ['related_superior', 'customer_level']
    filter_horizontal = ['related_user']
    fieldsets = (
        (_('基础信息'), {'fields': ('name', 'mobile', 'related_superior', 'related_user', 'customer_level')}),
        (_('城市合伙人'), {'fields': ('is_partner',)}),
        (_('余额/积分'), {'fields': (
            'total_consumption', 'total_consumption_1', 'total_consumption_2', 'total_credits',
            'total_price', 'total_payed',
            'current_amounts', 'current_credits')}),
        (_('银行卡'), {'fields': ('bank_account_name', 'bank_account_no', 'bank_name')}),
        (_('操作记录'), {'fields': ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')})
    )


@admin.register(Partner)
class PartnerAdmin(SimpleModelAdmin):
    list_display = ['pk', 'name', 'mobile', 'related_customer']
    search_fields = ['name', 'mobile']
    list_display_links = ['pk', 'name', 'mobile']


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
        (_('车辆详情'), {
            'fields': ('car_brand', 'car_model', 'car_price', )}),
        (_('保险详情'), {
            'fields': ('insurance_company', 'insurance_date', 'bought_date', 'annual_inspection_date',)}),
        (_('状态'), {'fields': ('is_confirmed', 'is_active')})
    )


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(SimpleModelAdmin):
    list_display = ['pk', 'name', 'desc', 'display', 'is_active']
    search_fields = ['name', 'desc']
    list_display_links = ['pk', 'name', 'desc']
    list_filter = ['is_active', 'display']


@admin.register(BelongTo)
class BelongToAdmin(AutoUpdateUserModelAdmin):
    list_display = ['pk', 'name', 'related_to', 'notes']
    search_fields = ['name', 'notes', 'related_to__name']
    list_display_links = ['pk', 'name']


@admin.register(InsuranceRecord)
class InsuranceRecordAdmin(AutoUpdateUserModelAdmin):
    list_display = [
        'pk', 'car', 'record_date', 'insurance_date', 'total_price', 'receiver', 'belong_to', 'insurance_company',
        'tax', 'has_payback', 'payback_percent', 'payback_amount',
        'ic_payback_percent', 'ic_payback_amount', 'profits',
        'is_payed', 'notes'
    ]
    list_display_links = ['pk', 'car']
    list_filter = ['has_payback', 'belong_to', 'insurance_company', 'record_date']
    date_hierarchy = 'record_date'
    search_fields = ['car__car_number', 'car__customer__name', 'car__customer__mobile']
    autocomplete_fields = ['car', 'related_partner', 'receiver', 'belong_to', 'insurance_company']
    fieldsets = (
        (_('基础'), {'fields': ('car', 'record_date', 'insurance_date')}),
        (_('金额'), {'fields': (
            'total_price', 'tax',
            'payback_percent', 'payback_amount',
            'ic_payback_percent', 'ic_payback_amount', 'profits',
            'has_payback', 'is_payed')}),
        (_('保险详情'), {'fields': (
            'insurance_jqx', 'insurance_csx', 'insurance_fdjss', 'insurance_zrss', 'insurance_dqx', 'insurance_pl',
            'insurance_cshx', 'insurance_dsxr', 'insurance_sj', 'insurance_ck', 'insurance_hw')}),
        (_('人员'), {'fields': ('receiver', 'belong_to', 'insurance_company', 'related_partner')}),
        (_('备注'), {'fields': ('notes',)})
    )


class ServicePackageInline(admin.TabularInline):
    model = ServicePackage
    extra = 0
    fields = ['name', 'desc', 'price', 'is_active']


@admin.register(ServicePackageType)
class ServicePackageTypeAdmin(SimpleModelAdmin):
    list_display = ['pk', 'name', 'desc', 'is_active']
    search_fields = ['name', 'desc']
    list_display_links = ['pk', 'name']
    list_filter = ['is_active']
    inlines = [ServicePackageInline]


@admin.register(ServicePackage)
class ServicePackageAdmin(SimpleModelAdmin):
    list_display = ['pk', 'name', 'price']
    search_fields = ['name']
    list_display_links = ['pk', 'name']
    autocomplete_fields = ['service_type']


@admin.register(StoreInfo)
class StoreInfoAdmin(SimpleModelAdmin):
    list_display = ['pk', 'name', 'address', 'is_active']
    search_fields = ['name']
    list_display_links = ['pk', 'name']
    list_filter = ['is_active']


class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 0
    autocomplete_fields = ('served_by',)
    fields = ['name', 'served_by', 'item_price', 'item_count', 'notes']


class ServiceFeedbackInline(admin.TabularInline):
    model = ServiceFeedback
    extra = 1
    fields = ['feedback_date', 'feedback_by', 'notes']
    autocomplete_fields = ['feedback_by']


@admin.register(ServiceItem)
class ServiceItemAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated', 'related_service_record')
    list_display = ['pk', 'related_service_record', 'name', 'price', 'cost', 'notes']
    search_fields = ['name']
    list_display_links = ['pk', 'related_service_record', 'name']
    fieldsets = (
        (_('基础信息'), {'fields': ('related_service_record', 'name', 'price', 'cost', 'notes')}),
        (_('操作记录'), {'fields': ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')}),
    )


@admin.register(ServiceFeedback)
class ServiceFeedbackAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated', 'related_service_record')
    list_display = ['pk', 'related_service_record', 'feedback_date', 'feedback_by', 'notes']
    search_fields = ['notes']
    list_display_links = ['pk', 'related_service_record', 'feedback_date']
    fieldsets = (
        (_('基础信息'), {'fields': ('related_service_record', 'feedback_date', 'feedback_by', 'notes')}),
        (_('操作记录'), {'fields': ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')}),
    )
    autocomplete_fields = ['feedback_by']


@admin.register(ServiceRecord)
class ServiceRecordAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated', 'total_price', 'total_cost')
    list_display = [
        'pk', 'car', 'reserve_type', 'is_reversed', 'reserve_time', 'reserve_address', 'related_store',
        'total_price', 'total_payed',
        'checked_by', 'is_checked', 'is_served', 'notes'
    ]
    list_display_links = ['pk', 'car']
    list_filter = [
        'is_reversed', 'checked_by', 'is_checked', 'is_served', 'is_payed', 'related_store', 'service_package', 'reserve_time']
    date_hierarchy = 'reserve_time'
    search_fields = ['car__car_number', 'car__customer__name', 'car__customer__mobile']
    autocomplete_fields = ['car', 'checked_by', 'related_partner', 'related_store', 'service_package', 'oil_package']
    fieldsets = (
        (_('基础信息'), {'fields': (
            'reserve_type', 'car', 'reserve_time', 'finish_time',
            'reserve_address', 'vehicle_mileage', 'month_mileage')}),
        (_('服务信息'), {
            'fields': (
                'related_store',  'total_price', 'total_payed',
                'is_served', 'is_payed', ('checked_by', 'is_checked'), 'related_partner')}),
        (_('预约信息'), {
            'fields': (
                'is_reversed', 'service_package', 'oil_package', 'service_info'),
            'classes': ('collapse',)
        }),
        (_('备注'), {
            'fields': ('notes', 'datetime_created', 'datetime_updated'),
            'classes': ('collapse',)
        })
    )

    inlines = [ServiceItemInline, ServiceFeedbackInline]

    def save_execl(self, request, queryset):
        filename = 'media/{0}_{1}.xls'.format('service', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        headers = [
            'ID', '姓名', '手机号', '车牌号', '进厂时间', '服务地点', '维修门店', '应收金额', '实收金额', '总成本']
        columns = [
            'pk', 'car__customer__name', 'car__customer__mobile', 'car__car_number', 'reserve_time',
            'reserve_address', 'related_store__name', 'total_price', 'total_payed', 'total_cost'
        ]
        return export_excel(queryset, headers, columns, filename)

    save_execl.short_description = "导出Excel"

    actions = [save_execl]


@admin.register(ServiceApply)
class ServiceApplyAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'datetime_created', 'car_number', 'name', 'mobile', 'is_checked', 'data_import', 'service_package', 'service_info',
        'reserve_type', 'reserve_time', 'reserve_address', 'related_store', 'notes'
    ]
    list_display_links = ['pk', 'car_number']
    list_filter = ['is_checked', 'reserve_type', 'data_import', 'service_package', 'related_store', 'checked_by']
    date_hierarchy = 'datetime_created'
    search_fields = ['car_number', 'name', 'mobile']
    autocomplete_fields = ['service_package', 'oil_package', 'related_store', 'related_record', 'checked_by']
    fieldsets = (
        (_('车辆信息'), {'fields': ('car_number', 'car_brand', 'car_model', 'name', 'mobile')}),

        (_('服务类型'), {'fields': ('reserve_type', )}),
        (_('服务信息'), {
            'fields': (
                'related_store', 'service_info', 'service_package', 'oil_package',
                'reserve_time', 'reserve_address')}),
        (_('审核信息'), {'fields': ('checked_by', 'is_checked', 'data_import', 'related_record')}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )


@admin.register(InsuranceApply)
class InsuranceApplyAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'datetime_created', 'car_number', 'name', 'mobile', 'service_type', 'is_checked', 'data_import', 'checked_by',
        'insurance_date',  'related_record', 'notes'
    ]
    list_display_links = ['pk', 'car_number']
    list_filter = ['is_checked', 'data_import', 'service_type', 'checked_by']
    date_hierarchy = 'datetime_created'
    search_fields = ['car_number', 'name', 'mobile']
    autocomplete_fields = ['checked_by', 'related_record']
    fieldsets = (
        (_('车辆信息'), {'fields': (
            'car_number', 'car_brand', 'car_model', 'name', 'mobile', 'insurance_date')}),
        (_('服务类型'), {'fields': ('service_type',)}),
        (_('车辆续保'), {'fields': (
            'insurance_jqx', 'insurance_csx', 'insurance_fdjss', 'insurance_zrss', 'insurance_dqx', 'insurance_pl',
            'insurance_cshx', 'insurance_dsxr', 'insurance_sj', 'insurance_ck', 'insurance_hw')}),
        (_('车辆贷款'), {'fields': ('changed_times', 'money_needed')}),
        (_('保险分期'), {'fields': ('money_jqx', 'money_ccs', 'money_syx', 'stages', 'down_payment', 'stage_payment')}),
        (_('审核信息'), {'fields': ('checked_by', 'is_checked', 'data_import', 'related_record')}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )


@admin.register(OilPackage)
class OilPackageAdmin(SimpleModelAdmin):
    list_display = ['pk', 'name', 'price']
    search_fields = ['name']
    list_display_links = ['pk', 'name']


@admin.register(PartnerApply)
class PartnerApplyAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'name', 'mobile', 'address', 'professional', 'reason', 'is_checked', 'is_confirmed', 'notes'
    ]
    list_display_links = ['pk', 'name', 'mobile']
    list_filter = ['is_checked', 'checked_by', 'is_confirmed']
    date_hierarchy = 'datetime_created'
    search_fields = ['name', 'mobile', 'address']
    autocomplete_fields = ['checked_by']
    fieldsets = (
        (_('基本信息'), {'fields': ('name', 'mobile', 'address', 'professional', 'reason')}),
        (_('审核信息'), {'fields': ('checked_by', 'is_checked', 'is_confirmed')}),
        (_('备注'), {'fields': ('notes', 'datetime_created', 'datetime_updated')})
    )


@admin.register(InsuranceRecordUpload)
class InsuranceRecordUploadAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = (
        'total_count', 'created_count', 'updated_count', 'failed_count', 'file_name',
        'is_processed', 'created_by', 'confirmed_by',  'datetime_created', 'datetime_updated')
    list_display = [
        'pk', 'file_name', 'is_confirmed', 'is_processed',
        'total_count', 'created_count', 'updated_count', 'failed_count',
        'created_by', 'confirmed_by',
        'datetime_created', 'datetime_updated'
    ]
    list_display_links = ['pk', 'file_name']
    list_filter = ['is_confirmed', 'is_processed']
    date_hierarchy = 'datetime_created'
    search_fields = ['file']
    fieldsets = (
        (_('基本信息'), {'fields': ('file', 'is_confirmed', 'notes')}),
        (_('导入信息'), {'fields': ('total_count', 'created_count', 'updated_count', 'failed_count', )}),
        (_('备注'), {'fields': ('created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')})
    )


@admin.register(ReportMake)
class ReportMakeAdmin(AutoUpdateUserModelAdmin):
    list_display = ['pk', 'report_type', 'file', 'date_start', 'date_end', 'notes', 'created_by', 'datetime_created']
    list_display_links = ['pk', 'report_type']
    list_filter = ['report_type']


@admin.register(MsgSendRecord)
class MsgSendRecordAdmin(AutoUpdateUserModelAdmin):
    readonly_fields = (
        'mobile', 'code', 'paras', 'msg_type', 'created_by', 'confirmed_by', 'datetime_created', 'datetime_updated')
    list_display = ['pk', 'mobile', 'code', 'paras', 'msg_type', 'notes']
    search_fields = ['mobile', 'code', 'paras']
    list_display_links = ['pk', 'mobile', 'paras']
    list_filter = ['msg_type']
