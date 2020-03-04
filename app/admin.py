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
class UserLevelAdmin(GeneralModelAdmin):
    list_display = ['pk', 'level_code', 'level_name', 'desc']
    search_fields = ['level_code', 'level_name', 'desc']


@admin.register(WxUser)
class WxUserAdmin(UserAdmin):
    readonly_fields = (
        'last_login', 'date_joined',
        'nick_name', 'city', 'province', 'country', 'avatar_url'
    )
    search_fields = [
        'username', 'openid', 'email', 'full_name', 'first_name', 'last_name', 'nick_name']
    autocomplete_fields = ['user_level']
    fieldsets = (
        (_('基础信息'), {'fields': ('username', 'password', 'openid')}),
        (_('个人信息'), {'fields': (
            'nick_name', 'first_name', 'last_name', 'full_name', 'current_credits', 'avatar_url',
            'gender', 'date_of_birth', 'desc'
        )}),
        (_('联络信息'), {'fields': ('mobile', 'email',)}),
        (_('地址信息'), {'fields': ('city', 'province', 'country', 'china_district')}),
        (_('分类信息'), {'fields': ('user_level', 'is_partner', 'is_client', 'is_manager')}),
        (_('登录信息'), {'fields': ('last_login', 'date_joined')}),
    )
