import hashlib

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserLevel(models.Model):
    level_code = models.SmallIntegerField(
        verbose_name=_('等级编号'), null=True, unique=True, blank=True)
    level_name = models.CharField(
        verbose_name=_('等级名称'), max_length=100, null=True, unique=True)
    desc = models.TextField(
        verbose_name=_('等级描述'), max_length=1000, null=True, blank=True)
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('用户等级')
        verbose_name_plural = _('用户等级')

    def __str__(self):
        return "{0} {1}".format(
            self.level_code,
            self.level_name,
        )


class Superior(models.Model):
    name = models.CharField(
        verbose_name=_('名字'), max_length=100, unique=True, null=True)
    mobile = models.CharField(
        verbose_name=_('手机号'), max_length=100, null=True, blank=True, unique=True)
    desc = models.TextField(
        verbose_name=_('描述'), max_length=1000, null=True, blank=True)
    user = models.ForeignKey(
        "WxUser",
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联账号')
    )
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='superior_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='superior_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('管理人员')
        verbose_name_plural = _('管理人员')

    def __str__(self):
        return "{0} {1}".format(
            self.name,
            self.mobile,
        )


class WxUser(AbstractUser):
    """
    用户列表
    """
    # 微信同步的用户信息
    openid = models.CharField(
        verbose_name=_('微信OpenID'), max_length=100, unique=True, null=True, blank=True)
    avatar_url = models.URLField(
        verbose_name=_('头像'), null=True, blank=True)
    nick_name = models.CharField(
        verbose_name=_('昵称'), max_length=100, null=True, blank=True, unique=True)
    gender = models.SmallIntegerField(
        verbose_name=_('性别'), choices=((1, '男'), (2, '女'), (0, '未知')), null=True, blank=True)
    language = models.CharField(verbose_name=_('语言'), max_length=100, null=True, blank=True)
    city = models.CharField(verbose_name=_('城市'), max_length=200, null=True, blank=True)
    province = models.CharField(
        verbose_name=_('省份'), max_length=200, null=True, blank=True)
    country = models.CharField(
        verbose_name=_('国家'), max_length=200, null=True, blank=True)
    # 附加信息
    full_name = models.CharField(
        verbose_name=_('真实姓名'), max_length=100, null=True, blank=True
    )
    date_of_birth = models.DateField(
        verbose_name=_('出生日期'), null=True, blank=True)
    desc = models.TextField(
        verbose_name=_('描述'), max_length=2000, null=True, blank=True)
    mobile = models.CharField(
        verbose_name=_('手机号'), max_length=100, null=True, blank=True, unique=True)
    user_level = models.ForeignKey(
        UserLevel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('用户等级')
    )
    current_credits = models.BigIntegerField(
        verbose_name=_('当前积分'), null=True, blank=True, default=0
    )
    is_partner = models.BooleanField(verbose_name=_('是合伙人'), default=False)
    is_client = models.BooleanField(verbose_name=_('是客户'), default=True)
    is_manager = models.BooleanField(verbose_name=_('是管理员'), default=False)
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        if self.nick_name:
            res = self.nick_name
        else:
            res = self.username
        return "[{0}] {1}".format(
            self.pk,
            res
        )

    def create_username_password(self):
        if not self.username and not self.password and self.openid:
            key = settings.SECRET_KEY
            self.username = hashlib.pbkdf2_hmac(
                "sha256", getattr(self, 'openid').encode(encoding='utf-8'), key.encode(encoding='utf-8'), 10).hex()
            self.password = hashlib.pbkdf2_hmac(
                "sha256", self.username.encode(), getattr(self, 'openid').encode(encoding='utf-8'), 10).hex()

    def save(self, *args, **kwargs):
        self.create_username_password()
        super().save(*args, **kwargs)


class Customer(models.Model):
    name = models.CharField(
        verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(
        verbose_name=_('手机'), max_length=255, null=True)
    related_superior = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('客户归属')
    )
    related_user = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_related_user',
        verbose_name=_('关联用户')
    )
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        unique_together = ['name', 'mobile']
        verbose_name = _('客户列表')
        verbose_name_plural = _('客户列表')

    def __str__(self):
        return "{0} {1}".format(
            self.name,
            self.mobile,
        )


class CarInfo(models.Model):
    car_number = models.CharField(
        verbose_name=_('车牌'), max_length=100, null=True,  blank=True, unique=True)
    car_brand = models.CharField(
        verbose_name=_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(
        verbose_name=_('汽车型号'), max_length=255, null=True, blank=True)
    car_price = models.IntegerField(
        verbose_name=_('购买价格/万'), null=True, blank=True)
    bought_date = models.DateField(
        verbose_name=_('购买日期'), null=True, blank=True)
    desc = models.TextField(
        verbose_name=_('描述'), max_length=1000, null=True, blank=True)
    is_confirmed = models.BooleanField(verbose_name=_('已审核'), default=False)
    is_active = models.BooleanField(verbose_name=_('有效'), default=True)
    customer = models.ForeignKey(
        Customer,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('客户')
    )
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='car_info_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='car_info_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('车辆信息')
        verbose_name_plural = _('车辆信息')

    def __str__(self):
        return "{} {}".format(
            self.car_number,
            self.customer,
        )


class InsuranceCompany(models.Model):
    name = models.CharField(
        verbose_name=_('保险出单公司'), max_length=200, null=True,  blank=True, unique=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('保险出单公司')
        verbose_name_plural = _('保险出单公司')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class BelongTo(models.Model):
    name = models.CharField(
        verbose_name=_('名称'), max_length=200, null=True,  blank=True, unique=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('归属渠道')
        verbose_name_plural = _('归属渠道')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class InsuranceRecord(models.Model):
    car = models.ForeignKey(
        CarInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('车辆信息')
    )
    record_date = models.DateField(verbose_name=_('签单日期'), null=True)
    insurance_date = models.DateField(verbose_name=_('保单开始日期'), null=True, blank=True)
    total_price = models.DecimalField(
        verbose_name=_('含税总保费'), max_digits=10, decimal_places=2, null=True, blank=True)
    receiver = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('验车人')
    )
    belong_to = models.ForeignKey(
        BelongTo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('归属渠道')
    )
    insurance_company = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('保险公司')
    )
    tax = models.DecimalField(
        verbose_name=_('车船税'), max_digits=10, decimal_places=2, null=True, blank=True)
    has_payback = models.BooleanField(_('是否已返费'), default=False)
    payback_percent = models.PositiveSmallIntegerField(
        verbose_name=_('已返费率'), null=True, blank=True)
    payback_amount = models.DecimalField(
        verbose_name=_('已返金额'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_payed = models.BooleanField(verbose_name=_('已支付'), default=True)
    notes = models.TextField(
        verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('投保记录')
        verbose_name_plural = _('投保记录')

    def __str__(self):
        return "{} {}".format(
            self.record_date,
            self.car,
        )
