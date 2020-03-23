import hashlib
import pandas as pd

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _

from car.utils import str_value, num_value, date_value


class UserLevel(models.Model):
    """
    用户等级
    """
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
    """
    工作人员
    """
    name = models.CharField(verbose_name=_('名字'), max_length=100, unique=True, null=True)
    mobile = models.CharField(verbose_name=_('手机号'), max_length=100, null=True, blank=True, unique=True)
    desc = models.TextField(verbose_name=_('描述'), max_length=1000, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('是否有效'), default=True)
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
    """
    客户
    """
    name = models.CharField(verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(verbose_name=_('手机'), max_length=255, null=True, unique=True)
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
        verbose_name = _('客户列表')
        verbose_name_plural = _('客户列表')

    def __str__(self):
        return "{0} {1}".format(
            self.name,
            self.mobile,
        )


class CarInfo(models.Model):
    """
    车辆信息
    """
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
    """
    保险出单公司
    """
    name = models.CharField(verbose_name=_('保险出单公司'), max_length=200, null=True, unique=True)
    display = models.BooleanField(verbose_name=_('用户是否可选'), default=True)
    is_active = models.BooleanField(verbose_name=_('是否有效'), default=True)

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
    """
    归属渠道
    """
    name = models.CharField(
        verbose_name=_('名称'), max_length=200, null=True,  blank=True, unique=True)
    related_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='belong_to_related_to',
        null=True,
        blank=True,
        verbose_name=_('相同渠道')
    )
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='belong_to_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='belong_to_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)
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
    """
    保险记录
    """
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
        limit_choices_to={'is_active': True},
        verbose_name=_('保险公司')
    )
    tax = models.DecimalField(verbose_name=_('车船税'), max_digits=10, decimal_places=2, null=True, blank=True)
    has_payback = models.BooleanField(verbose_name=_('是否已返费'), default=False)
    payback_percent = models.DecimalField(
        verbose_name=_('已返费率'), max_digits=7, decimal_places=4, null=True, blank=True)
    payback_amount = models.DecimalField(
        verbose_name=_('已返金额'), max_digits=10, decimal_places=2, null=True, blank=True)
    ic_payback_percent = models.DecimalField(
        verbose_name=_('保险公司返点'), max_digits=7, decimal_places=4, null=True, blank=True)
    ic_payback_amount = models.DecimalField(
        verbose_name=_('返费金额'), max_digits=10, decimal_places=2, null=True, blank=True)
    profits = models.DecimalField(
        verbose_name=_('利润'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_payed = models.BooleanField(verbose_name=_('已支付'), default=True)

    insurance_csx = models.BooleanField(
        verbose_name=_('机动车辆损失险'),
        help_text=_(
            '发生保险事故时，补偿您自己车辆的损失。例如车辆发生碰撞、倾覆、火灾、爆炸，或被外界物体倒塌、坠物砸坏，'
            '以及与别人车辆发生碰撞，造成自己的车辆受损等，保险公司将按照条款赔偿您的车辆维修费用'),
        default=True)
    insurance_fdjss = models.BooleanField(
        verbose_name=_('发动机涉水损失险'),
        help_text=_(
            '车辆在使用过程中，因发动机进水后导致的发动机的直接损毁，保险公司将按条款规定赔偿。'),
        default=False)
    insurance_zrss = models.BooleanField(
        verbose_name=_('自燃损失险'),
        help_text=_(
            '因本车电器、线路、油路、供油系统、供气系统、车载货物等自身发生问题，或者车辆运转摩擦引起火灾，造成本车的损失，'
            '以及为减少本车损失所支出的必要合理的施救费用，保险公司将按条款规定赔偿。'),
        default=False)
    insurance_dqx = models.BooleanField(
        verbose_name=_('盗抢险'),
        help_text=_(
            '如果车辆被盗窃、抢劫、抢夺，经公安机关立案证明，保险公司将按条款规定赔偿。'),
        default=False)
    insurance_pl = models.BooleanField(
        verbose_name=_('玻璃单独破碎险'),
        help_text=_(
            '如果发生挡风玻璃或车窗玻璃单独破碎，保险公司按实际损失进行赔偿。例如被高空坠物或飞石击碎挡风玻璃或车窗玻璃。'),
        default=False)
    insurance_cshx = models.BooleanField(
        verbose_name=_('车身划痕损失险'),
        help_text=_(
            '无明显碰撞痕迹的车身划痕损失，保险公司将按照条款规定赔偿。例如车辆停放期间，被人用尖锐物划伤。'),
        default=False)
    insurance_dsxr = models.CharField(
        verbose_name=_('第三责任险'),
        help_text=_(
            '发生保险事故，我们可以按条款代您对第三方（人或物）受到的损失进行赔偿。'
            '例如您不幸撞坏了别人的车或驾车致人伤亡，保险公司将按照条款规定赔偿。'),
        choices=(('20万', '20万'), ('30万', '30万'), ('50万', '50万'), ('100万', '100万')),
        max_length=100,
        null=True
    )
    insurance_sj = models.CharField(
        verbose_name=_('车上人员责任险-司机'),
        help_text=_(
            '发生意外事故，造成本车驾驶员本人的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。'),
        choices=(('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')),
        max_length=100,
        null=True,
        blank=True
    )
    insurance_ck = models.CharField(
        verbose_name=_('车上人员责任险-乘客'),
        help_text=_(
            '发生意外事故，造成本车乘客（非驾驶员）的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。'),
        choices=(('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')),
        max_length=100,
        null=True,
        blank=True
    )
    insurance_hw = models.CharField(
        verbose_name=_('车上货物责任险'),
        help_text=_(
            '发生意外事故，致使保险车辆所载货物遭受直接损毁，依法应由被保险人承担的经济赔偿责任，保险人负责赔偿。'),
        choices=(('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')),
        max_length=100,
        null=True,
        blank=True
    )

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
    """
    套餐归类
    """
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True, unique=True)
    icon = models.ImageField(verbose_name=_('图片'), upload_to='service_package_type', null=True, blank=True)
    desc = models.CharField(verbose_name=_('介绍'), max_length=200, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('是否有效'), default=True)

    objects = models.Manager()

    @property
    def service_packages(self):
        res = list()
        sps = ServicePackage.objects.filter(service_type_id=self.pk).order_by('name')
        for sp in sps:
            res.append(model_to_dict(sp))
        return res

    class Meta:
        ordering = ['id']
        verbose_name = _('套餐归类')
        verbose_name_plural = _('套餐归类')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class ServicePackage(models.Model):
    """
    服务套餐
    """
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True,  unique=True)
    price = models.DecimalField(verbose_name=_('价格'), max_digits=10, decimal_places=2, null=True, blank=True)
    desc = models.CharField(verbose_name=_('介绍'), max_length=200, null=True, blank=True)
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
        return "{} (￥{})".format(
            self.name,
            self.price
        )


class OilPackage(models.Model):
    """
    机油套餐
    """
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True,  unique=True)
    price = models.DecimalField(verbose_name=_('价格'), max_digits=10, decimal_places=2, null=True, blank=True)
    desc = models.CharField(verbose_name=_('介绍'), max_length=200, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('是否有效'), default=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('机油套餐')
        verbose_name_plural = _('机油套餐')

    def __str__(self):
        return "{} （￥ {}）".format(
            self.name,
            self.price
        )


class StoreInfo(models.Model):
    """
    门店信息
    """
    name = models.CharField(verbose_name=_('名称'), max_length=200, null=True, unique=True)
    contact = models.CharField(verbose_name=_('联系电话'), max_length=200, null=True, blank=True)
    address = models.TextField(verbose_name=_('地址'), max_length=1000, null=True, blank=True)
    image = models.ImageField(verbose_name=_('照片'), upload_to='', null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('有效'), default=True)
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
    """
    服务记录
    """
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
    oil_package = models.ForeignKey(
        OilPackage,
        on_delete=models.SET_NULL,
        limit_choices_to={'is_active': True},
        null=True,
        blank=True,
        verbose_name=_('机油套餐')
    )
    service_info = models.TextField(verbose_name=_('服务详情'), null=True, blank=True, max_length=200)
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


def get_car_info(obj):
    """
    存储及获取车辆信息
    :param obj: 数据对象
    :return: 返回车辆对象
    """
    # 数据格式化
    fields = ['name', 'mobile', 'car_number']
    data = dict()
    for f in fields:
        ori_value = getattr(obj, f)
        if f == 'car_number':
            data[f] = str_value(ori_value, upper=True)
        else:
            data[f] = str_value(ori_value)
    # 获取或创建客户信息
    if data['mobile']:
        customer, created = Customer.objects.get_or_create(
            mobile=data['mobile'],
            defaults={'name': data['name']})
    else:
        customer, created = Customer.objects.get_or_create(
            name=data['name'])
    # 获取或存储车辆信息
    car, car_created = CarInfo.objects.get_or_create(
        car_number=data['car_number'],
        defaults={'customer': customer, 'car_brand': obj.car_brand, 'car_model': obj.car_model})
    # 如果原始车信息为空，则进行更新
    if not car_created:
        if not car.customer:
            car.customer = customer
        if not car.car_brand:
            car.car_brand = obj.car_brand
        if not car.car_model:
            car.car_model = obj.car_model
        car.save()
    return car


class ServiceApply(models.Model):
    """
    服务申请
    """
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
        limit_choices_to={'is_active': True},
        null=True,
        blank=True,
        verbose_name=_('服务套餐')
    )
    oil_package = models.ForeignKey(
        OilPackage,
        on_delete=models.SET_NULL,
        limit_choices_to={'is_active': True},
        null=True,
        blank=True,
        verbose_name=_('机油套餐')
    )
    service_info = models.TextField(verbose_name=_('服务详情'), null=True, blank=True,  max_length=200)
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
    data_import = models.BooleanField(
        verbose_name=_('已导入服务记录'), help_text=_('勾选以后数据将会自动导入到【维修服务】列表'), default=False)
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
            # 获取或存储客户信息
            car = get_car_info(self)
            # 添加服务记录
            related_record, created = ServiceRecord.objects.update_or_create(
                car=car,
                service_package=self.service_package,
                reserve_type=self.reserve_type,
                service_info=self.service_info,
                is_reversed=True,
                reserve_time=self.reserve_time,
                reserve_address=self.reserve_address,
                related_store=self.related_store,
                created_by=self.created_by
            )
            self.related_record = related_record
        super(ServiceApply, self).save(*args, **kwargs)


class InsuranceApply(models.Model):
    """
    保险申请
    """
    car_number = models.CharField(verbose_name=_('车牌'), max_length=100, null=True)
    car_brand = models.CharField(verbose_name=_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(verbose_name=_('汽车型号'), max_length=255, null=True, blank=True)
    name = models.CharField(verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(verbose_name=_('手机'), max_length=255, null=True)
    service_type = models.IntegerField(
        verbose_name=_('类别'), null=True, blank=True, choices=[(1, '车辆续保'), (2, '保险分期'), (3, '购车贷款')])
    insurance_date = models.DateField(verbose_name=_('保单开始日期'), null=True, blank=True)
    insurance_csx = models.BooleanField(
        verbose_name=_('机动车辆损失险'),
        help_text=_(
            '发生保险事故时，补偿您自己车辆的损失。例如车辆发生碰撞、倾覆、火灾、爆炸，或被外界物体倒塌、坠物砸坏，'
            '以及与别人车辆发生碰撞，造成自己的车辆受损等，保险公司将按照条款赔偿您的车辆维修费用'),
        default=True)
    insurance_fdjss = models.BooleanField(
        verbose_name=_('发动机涉水损失险'),
        help_text=_(
            '车辆在使用过程中，因发动机进水后导致的发动机的直接损毁，保险公司将按条款规定赔偿。'),
        default=False)
    insurance_zrss = models.BooleanField(
        verbose_name=_('自燃损失险'),
        help_text=_(
            '因本车电器、线路、油路、供油系统、供气系统、车载货物等自身发生问题，或者车辆运转摩擦引起火灾，造成本车的损失，'
            '以及为减少本车损失所支出的必要合理的施救费用，保险公司将按条款规定赔偿。'),
        default=False)
    insurance_dqx = models.BooleanField(
        verbose_name=_('盗抢险'),
        help_text=_(
            '如果车辆被盗窃、抢劫、抢夺，经公安机关立案证明，保险公司将按条款规定赔偿。'),
        default=False)
    insurance_pl = models.BooleanField(
        verbose_name=_('玻璃单独破碎险'),
        help_text=_(
            '如果发生挡风玻璃或车窗玻璃单独破碎，保险公司按实际损失进行赔偿。例如被高空坠物或飞石击碎挡风玻璃或车窗玻璃。'),
        default=False)
    insurance_cshx = models.BooleanField(
        verbose_name=_('车身划痕损失险'),
        help_text=_(
            '无明显碰撞痕迹的车身划痕损失，保险公司将按照条款规定赔偿。例如车辆停放期间，被人用尖锐物划伤。'),
        default=False)
    insurance_dsxr = models.CharField(
        verbose_name=_('第三责任险'),
        help_text=_(
            '发生保险事故，我们可以按条款代您对第三方（人或物）受到的损失进行赔偿。'
            '例如您不幸撞坏了别人的车或驾车致人伤亡，保险公司将按照条款规定赔偿。'),
        choices=(('20万', '20万'), ('30万', '30万'), ('50万', '50万'), ('100万', '100万')),
        max_length=100,
        null=True
    )
    insurance_sj = models.CharField(
        verbose_name=_('车上人员责任险-司机'),
        help_text=_(
            '发生意外事故，造成本车驾驶员本人的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。'),
        choices=(('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')),
        max_length=100,
        null=True,
        blank=True
    )
    insurance_ck = models.CharField(
        verbose_name=_('车上人员责任险-乘客'),
        help_text=_(
            '发生意外事故，造成本车乘客（非驾驶员）的人身伤亡，如果本车负有责任，保险公司将按条款规定赔偿。'),
        choices=(('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')),
        max_length=100,
        null=True,
        blank=True
    )
    insurance_hw = models.CharField(
        verbose_name=_('车上货物责任险'),
        help_text=_(
            '发生意外事故，致使保险车辆所载货物遭受直接损毁，依法应由被保险人承担的经济赔偿责任，保险人负责赔偿。'),
        choices=(('5万', '5万'), ('20万', '20万'), ('30万', '30万'), ('50万', '50万')),
        max_length=100,
        null=True,
        blank=True
    )
    insurance_company = models.ForeignKey(
        InsuranceCompany,
        limit_choices_to={'display': True, 'is_active': True},
        on_delete=models.SET_NULL,
        related_name='insurance_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('保险公司')
    )
    changed_times = models.CharField(
        verbose_name=_('过户次数'),
        choices=(('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')),
        max_length=100,
        null=True,
        default='0'
    )
    money_needed = models.IntegerField(
        verbose_name=_('需求金额/元'),
        null=True,
        blank=True
    )
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
            car = get_car_info(self)
            # 添加保险记录
            related_record, created = InsuranceRecord.objects.get_or_create(
                car=car,
                insurance_date=self.insurance_date,
                created_by=self.created_by,
                is_payed=False
            )
            self.related_record = related_record
        super(InsuranceApply, self).save(*args, **kwargs)


class PartnerApply(models.Model):
    """
    城市合伙人申请
    """
    name = models.CharField(verbose_name=_('名字'), max_length=255, null=True)
    mobile = models.CharField(verbose_name=_('手机'), max_length=255, null=True)
    address = models.TextField(verbose_name=_('长期居住地'), max_length=1000, null=True, blank=True)
    professional = models.CharField(verbose_name=_('现就职业'), max_length=100, null=True, blank=True)
    reason = models.TextField(verbose_name=_('申请理由或资源'), max_length=1000, null=True, blank=True)
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='partner_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(verbose_name=_('已联系/已确认'), default=False)
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='partner_apply_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='partner_apply_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('城市合伙人')
        verbose_name_plural = _('城市合伙人')

    def __str__(self):
        return "{} {} {}".format(
            self.name,
            self.mobile,
            self.is_checked
        )


class InsuranceRecordUpload(models.Model):
    """
    保险业绩数据导入
    """
    file = models.FileField(verbose_name=_('文件'), null=True, blank=True)
    file_name = models.CharField(verbose_name=_('文件名'), null=True, blank=True, max_length=255)
    total_count = models.IntegerField(verbose_name=_('总条数'), null=True, blank=True)
    created_count = models.IntegerField(verbose_name=_('添加条数'), null=True, blank=True)
    updated_count = models.IntegerField(verbose_name=_('更新条数'), null=True, blank=True)
    failed_count = models.IntegerField(verbose_name=_('失败条数'), null=True, blank=True)
    is_confirmed = models.BooleanField(verbose_name=_('已确认'), default=True)
    is_processed = models.BooleanField(verbose_name=_('已执行'), default=False)
    notes = models.TextField(verbose_name=_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_upload_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        "WxUser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_upload_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(verbose_name=_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('保险业绩数据导入')
        verbose_name_plural = _('保险业绩数据导入')

    def __str__(self):
        return "{}".format(
            self.file_name
        )

    def import_insurance_data_from_excel(self):
        """
        数据导入模块
        """
        if self.file:
            self.is_processed = True
            df = pd.read_excel(getattr(self, 'file').path, keep_default_na=False)
            fields = {
                'car_number': '车牌号',
                'name': '被保险人名称',
                'mobile': '手机号',
                'record_date': '签单日期',
                'total_price': '含税总保费',
                'tax': '车船税',
                'payback_percent': '已返费率',
                'payback_amount': '已返金额',
                'ic_payback_percent': '保险公司返点',
                'ic_payback_amount': '返费金额',
                'profits': '利润',
                'insurance_company__name': '保险出单公司',
                'belong_to__name': '归属渠道',
            }
            foreign_keys = ['car_number', 'name', 'mobile', 'insurance_company__name', 'belong_to__name']
            str_fields = [
                'car_number', 'name', 'mobile', 'insurance_company__name', 'belong_to__name'
            ]
            num_fields_2 = [
                'total_price', 'tax', 'payback_amount', 'ic_payback_amount', 'profits'
            ]
            num_fields_4 = [
                'payback_percent', 'ic_payback_percent'
            ]
            date_fields = [
                'record_date'
            ]
            self.total_count = 0
            self.created_count = 0
            self.updated_count = 0
            self.failed_count = 0
            for r in df.itertuples():
                self.total_count += 1
                data = {}
                for k, v in fields.items():
                    try:
                        vl = getattr(r, v)
                        if k in str_fields:
                            data[k] = str_value(vl)
                        elif k in num_fields_2:
                            data[k] = num_value(vl, 2)
                        elif k in num_fields_4:
                            data[k] = num_value(vl, 4)
                        elif k in date_fields:
                            data[k] = date_value(vl)
                        else:
                            data[k] = vl
                    except AttributeError:
                        print(r)
                # 客户信息获取
                if data['mobile']:
                    customer, created = Customer.objects.get_or_create(
                        mobile=data['mobile'], defaults={'name': data['name']})
                else:
                    customer = Customer.objects.filter(name=data['name']).order_by('pk').last()
                    if not customer:
                        customer = Customer.objects.create(name=data['name'])
                # 车辆信息获取
                car, car_created = CarInfo.objects.update_or_create(
                    car_number=data['car_number'], defaults={'customer': customer})
                # 归属渠道
                belong_to, belong_to_created = BelongTo.objects.get_or_create(
                    name=data['belong_to__name']
                )
                # 保险出单公司
                insurance_company, insurance_company_created = InsuranceCompany.objects.get_or_create(
                    name=data['insurance_company__name']
                )
                for p in foreign_keys:
                    data.pop(p)
                ir, ir_created = InsuranceRecord.objects.update_or_create(
                    car=car,
                    belong_to=belong_to,
                    insurance_company=insurance_company,
                    has_payback=True,
                    is_payed=True,
                    notes='自动导入数据',
                    **data
                )
                if ir_created:
                    self.created_count += 1
                else:
                    self.updated_count += 1
            self.failed_count = self.total_count - self.created_count - self.updated_count

    def save(self, *args, **kwargs):
        super(InsuranceRecordUpload, self).save(*args, **kwargs)
        if self.is_confirmed is True and self.file and self.is_processed is False:
            # 更新文件名称
            self.file_name = getattr(self, 'file').name
            self.import_insurance_data_from_excel()
            super(InsuranceRecordUpload, self).save(
                update_fields=[
                    'file_name', 'is_processed', 'total_count', 'created_count', 'updated_count', 'failed_count'])
