import hashlib

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserLevel(models.Model):
    level_code = models.SmallIntegerField(verbose_name=_('等级编号'), null=True, unique=True)
    level_name = models.CharField(verbose_name=_('等级名称'), max_length=100, null=True, unique=True)
    desc = models.TextField(verbose_name=_('等级描述'), max_length=1000, null=True, blank=True)
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


class WxUser(AbstractUser):
    """
    用户列表
    """
    # 微信同步的用户信息
    openid = models.CharField(verbose_name=_('微信OpenID'), max_length=100, unique=True, null=True, blank=True)
    avatar_url = models.URLField(verbose_name=_('头像'), null=True, blank=True)
    nick_name = models.CharField(verbose_name=_('昵称'), max_length=100, null=True, blank=True, unique=True)
    gender = models.SmallIntegerField(
        verbose_name=_('性别'), choices=((1, '男'), (2, '女'), (0, '未知')), null=True, blank=True)
    language = models.CharField(verbose_name=_('语言'), max_length=100, null=True, blank=True)
    city = models.CharField(verbose_name=_('城市'), max_length=200, null=True, blank=True)
    province = models.CharField(verbose_name=_('省份'), max_length=200, null=True, blank=True)
    country = models.CharField(verbose_name=_('国家'), max_length=200, null=True, blank=True)
    # 附加信息
    full_name = models.CharField(verbose_name=_('真实姓名'), max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(verbose_name=_('出生日期'), null=True, blank=True)
    desc = models.TextField(verbose_name=_('描述'), max_length=2000, null=True, blank=True)
    mobile = models.CharField(verbose_name=_('手机号'), max_length=100, null=True, blank=True, unique=True)
    user_level = models.ForeignKey(
        UserLevel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('用户等级')
    )
    current_credits = models.BigIntegerField(verbose_name=_('当前积分'), null=True, blank=True, default=0)
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


class Superior(models.Model):
    name = models.CharField(verbose_name=_('名字'), max_length=100, unique=True, null=True)
    mobile = models.CharField(verbose_name=_('手机号'), max_length=100, null=True, blank=True, unique=True)
    desc = models.TextField(verbose_name=_('描述'), max_length=1000, null=True, blank=True)
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
        verbose_name = _('工作人员')
        verbose_name_plural = _('工作人员')

    def __str__(self):
        return "{0} {1}".format(
            self.name,
            self.mobile,
        )


class Customer(models.Model):
    name = models.CharField(verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(verbose_name=_('手机'), max_length=255, null=True)
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
    car_number = models.CharField(verbose_name=_('车牌'), max_length=100, null=True,  blank=True, unique=True)
    car_brand = models.CharField(verbose_name=_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(verbose_name=_('汽车型号'), max_length=255, null=True, blank=True)
    car_price = models.IntegerField(verbose_name=_('购买价格/万'), null=True, blank=True)
    bought_date = models.DateField(verbose_name=_('购买日期'), null=True, blank=True)
    desc = models.TextField(verbose_name=_('描述'), max_length=1000, null=True, blank=True)
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
        verbose_name=_('保险出单公司'), max_length=200, null=True, unique=True)

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
    total_price = models.DecimalField(verbose_name=_('含税总保费'), max_digits=10, decimal_places=2, null=True, blank=True)
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
    tax = models.DecimalField(verbose_name=_('车船税'), max_digits=10, decimal_places=2, null=True, blank=True)
    has_payback = models.BooleanField(_('是否已返费'), default=False)
    payback_percent = models.PositiveSmallIntegerField(verbose_name=_('已返费率'), null=True, blank=True)
    payback_amount = models.DecimalField(verbose_name=_('已返金额'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_payed = models.BooleanField(verbose_name=_('已支付'), default=True)
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
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


class ServicePackageType(models.Model):
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True, unique=True)
    desc = models.CharField(verbose_name=_('介绍'), max_length=200, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('是否有效'), default=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('套餐归类')
        verbose_name_plural = _('套餐归类')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class ServicePackage(models.Model):
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True,  unique=True)
    desc = models.CharField(verbose_name=_('介绍'), max_length=200, null=True, blank=True)
    price = models.DecimalField(verbose_name=_('价格'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('是否有效'), default=True)
    service_type = models.ForeignKey(
        ServicePackageType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('归类')
    )

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('服务套餐')
        verbose_name_plural = _('服务套餐')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class StoreInfo(models.Model):
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True, unique=True)
    contact = models.CharField(verbose_name=_('联系电话'), max_length=200, null=True, blank=True)
    address = models.TextField(verbose_name=_('地址'), max_length=1000, null=True, blank=True)
    desc = models.TextField(verbose_name=_('介绍'), max_length=2000, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('门店信息')
        verbose_name_plural = _('门店信息')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class ServiceRecord(models.Model):
    car = models.ForeignKey(
        CarInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('车辆信息')
    )
    service_package = models.ForeignKey(
        ServicePackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('服务套餐')
    )
    reserve_type = models.IntegerField(verbose_name=_('类型'), null=True, blank=True, choices=[(1, '上门'), (2, '到店')])
    is_reversed = models.BooleanField(verbose_name=_('是预约服务'), default=False)
    reserve_time = models.DateTimeField(verbose_name=_('服务时间'), null=True, blank=True)
    reserve_address = models.TextField(verbose_name=_('服务地点'), max_length=1000, null=True, blank=True)
    related_store = models.ForeignKey(
        StoreInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('门店')
    )
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='service_record_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(verbose_name=_('已联系/已确认'), default=False)
    served_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='service_record_served_by',
        null=True,
        blank=True,
        verbose_name=_('由谁服务')
    )
    is_served = models.BooleanField(verbose_name=_('服务已完成'), default=False)
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('服务记录')
        verbose_name_plural = _('服务记录')

    def __str__(self):
        return "{} {}".format(
            self.car,
            self.reserve_time,
        )


class ServiceApply(models.Model):
    car_number = models.CharField(verbose_name=_('车牌'), max_length=100, null=True)
    car_brand = models.CharField(verbose_name=_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(verbose_name=_('汽车型号'), max_length=255, null=True, blank=True)
    name = models.CharField(verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(verbose_name=_('手机'), max_length=255, null=True)
    related_store = models.ForeignKey(
        StoreInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('门店')
    )
    service_package = models.ForeignKey(
        ServicePackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('服务套餐')
    )
    reserve_type = models.IntegerField(verbose_name=_('类型'), null=True, blank=True, choices=[(1, '上门'), (2, '到店')])
    reserve_time = models.DateTimeField(verbose_name=_('服务时间'), null=True, blank=True)
    reserve_address = models.TextField(verbose_name=_('服务地点'), max_length=1000, null=True, blank=True)
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='service_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(verbose_name=_('已联系/已确认'), default=False)
    data_import = models.BooleanField(verbose_name=_('数据导入'), default=False)
    related_record = models.ForeignKey(
        ServiceRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('关联记录')
    )
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_apply_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_apply_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('维修服务申请')
        verbose_name_plural = _('维修服务申请')

    def __str__(self):
        return "{} {} {} {}".format(
            self.car_number,
            self.name,
            self.mobile,
            self.reserve_time,
        )

    def save(self, *args, **kwargs):
        if self.data_import:
            # 数据格式化
            name = getattr(self, 'name').replace(' ', '')
            mobile = getattr(self, 'mobile').replace(' ', '')
            car_number = getattr(self, 'car_number').replace(' ', '').upper()
            # 获取或存储客户信息
            customer, created = Customer.objects.get_or_create(name=name, mobile=mobile)
            # 获取或存储车辆信息
            car, car_created = CarInfo.objects.get_or_create(
                car_number=car_number,
                defaults={'customer': customer, 'car_brand': self.car_brand, 'car_model': self.car_model})
            # 如果原始车信息为空，则进行更新
            if not car_created:
                if not car.customer:
                    car.customer = customer
                if not car.car_brand:
                    car.car_brand = self.car_brand
                if not car.car_model:
                    car.car_model = self.car_model
                car.save()
            # 添加服务记录
            related_record, created = ServiceRecord.objects.update_or_create(
                car=car,
                service_package=self.service_package,
                reserve_type=self.reserve_type,
                is_reversed=True,
                reserve_time=self.reserve_time,
                reserve_address=self.reserve_address,
                related_store=self.related_store,
                created_by=self.created_by
            )
            self.related_record = related_record
        super(ServiceApply, self).save(*args, **kwargs)


class InsuranceApply(models.Model):
    car_number = models.CharField(verbose_name=_('车牌'), max_length=100, null=True)
    car_brand = models.CharField(verbose_name=_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(verbose_name=_('汽车型号'), max_length=255, null=True, blank=True)
    name = models.CharField(verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(verbose_name=_('手机'), max_length=255, null=True)
    service_type = models.IntegerField(
        verbose_name=_('类别'), null=True, blank=True, choices=[(1, '车辆续保'), (2, '保险分期'), (3, '购车贷款')])
    insurance_date = models.DateField(verbose_name=_('保单开始日期'), null=True, blank=True)
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='insurance_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(verbose_name=_('已联系/已确认'), default=False)
    data_import = models.BooleanField(verbose_name=_('数据导入'), default=False)
    related_record = models.ForeignKey(
        InsuranceRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('关联记录')
    )
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_apply_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_apply_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('保险服务申请')
        verbose_name_plural = _('保险服务申请')

    def __str__(self):
        return "{} {} {} {}".format(
            self.car_number,
            self.name,
            self.mobile,
            self.insurance_date,
        )

    def save(self, *args, **kwargs):
        if self.data_import:
            # 数据格式化
            name = getattr(self, 'name').replace(' ', '')
            mobile = getattr(self, 'mobile').replace(' ', '')
            car_number = getattr(self, 'car_number').replace(' ', '').upper()
            # 获取或存储客户信息
            customer, created = Customer.objects.get_or_create(name=name, mobile=mobile)
            # 获取或存储车辆信息
            car, car_created = CarInfo.objects.get_or_create(
                car_number=car_number,
                defaults={'customer': customer, 'car_brand': self.car_brand, 'car_model': self.car_model})
            # 如果原始车信息为空，则进行更新
            if not car_created:
                if not car.customer:
                    car.customer = customer
                if not car.car_brand:
                    car.car_brand = self.car_brand
                if not car.car_model:
                    car.car_model = self.car_model
                car.save()
            # 添加保险记录
            related_record, created = InsuranceRecord.objects.get_or_create(
                car=car,
                insurance_date=self.insurance_date,
                created_by=self.created_by,
                is_payed=False
            )
            self.related_record = related_record
        super(InsuranceApply, self).save(*args, **kwargs)
