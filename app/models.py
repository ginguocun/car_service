import hashlib
import pandas as pd

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from car.utils import str_value, num_value, date_value


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


class UserLevel(models.Model):
    """
    用户等级
    """
    level_code = models.SmallIntegerField(_('等级编号'), null=True, unique=True)
    level_name = models.CharField(_('等级名称'), max_length=100, null=True, unique=True)
    desc = models.TextField(_('等级描述'), max_length=1000, null=True, blank=True)
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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
    openid = models.CharField(_('微信小程序OpenID'), max_length=100, unique=True, null=True, blank=True)
    openid_gzh = models.CharField(_('微信公众号OpenID'), max_length=100, unique=True, null=True, blank=True)
    avatar_url = models.URLField(_('头像'), null=True, blank=True)
    nick_name = models.CharField(_('昵称'), max_length=100, null=True, blank=True, unique=True)
    gender = models.SmallIntegerField(
        verbose_name=_('性别'), help_text=_('0-->未知, 1-->男, 2-->女'),
        choices=((1, '男'), (2, '女'), (0, '未知')), null=True, blank=True)
    language = models.CharField(_('语言'), max_length=100, null=True, blank=True)
    city = models.CharField(_('城市'), max_length=200, null=True, blank=True)
    province = models.CharField(_('省份'), max_length=200, null=True, blank=True)
    country = models.CharField(_('国家'), max_length=200, null=True, blank=True)
    # 附加信息
    full_name = models.CharField(_('真实姓名'), max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(_('出生日期'), null=True, blank=True)
    desc = models.TextField(_('描述'), max_length=2000, null=True, blank=True)
    mobile = models.CharField(_('手机号'), max_length=100, null=True, blank=True)
    user_level = models.ForeignKey(
        UserLevel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('用户等级')
    )
    is_partner = models.BooleanField(_('是合伙人'), default=False)
    is_client = models.BooleanField(_('是客户'), default=True)
    is_manager = models.BooleanField(_('是管理员'), default=False)
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        ordering = ['-id']

    def __str__(self):
        if self.nick_name:
            res = self.nick_name
        else:
            res = self.username
        return "[{0}] {1} {2}".format(
            self.pk,
            res,
            self.mobile
        )


class Superior(models.Model):
    """
    工作人员
    """
    name = models.CharField(_('名字'), max_length=100, unique=True, null=True)
    mobile = models.CharField(_('手机号'), max_length=100, null=True, blank=True, unique=True)
    desc = models.TextField(_('描述'), max_length=1000, null=True, blank=True)
    is_active = models.BooleanField(_('是否有效'), default=True)
    user = models.ForeignKey(
        WxUser,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('关联账号')
    )
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='superior_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='superior_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('工作人员')
        verbose_name_plural = _('工作人员')

    def __str__(self):
        return "{0} {1}".format(
            self.name,
            self.mobile if self.mobile else '',
        )


class Customer(models.Model):
    """
    客户，手机号作为唯一标识
    """
    name = models.CharField(_('名字'), help_text=_('请尽量填写真实姓名'), max_length=255, null=True)
    mobile = models.CharField(_('手机'), max_length=255, null=True, unique=True)
    # 银行卡信息
    bank_account_name = models.CharField(_('银行账户-姓名'), max_length=255, null=True, blank=True)
    bank_account_no = models.CharField(_('银行账户-卡号'), max_length=255, null=True, blank=True)
    bank_name = models.CharField(_('银行名称'), max_length=255, null=True, blank=True)
    is_partner = models.BooleanField(_('是合伙人'), default=False)
    current_amounts = models.DecimalField(
        verbose_name=_('当前余额（元）'),
        help_text=_('请到[积分/余额-->余额变更]添加记录'),
        max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    current_credits = models.BigIntegerField(
        verbose_name=_('当前积分'),
        help_text=_('请到[积分/余额-->积分变更]添加记录'),
        null=True, blank=True, default=0)
    related_superior = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('客户归属')
    )
    related_user = models.ManyToManyField(
        WxUser,
        blank=True,
        related_name='customer_related_user',
        verbose_name=_('关联用户')
    )
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('客户列表')
        verbose_name_plural = _('客户列表')

    def __str__(self):
        return "{0} {1} (余额:￥{2}; 积分:{3})".format(
            self.name,
            self.mobile if self.mobile else '',
            self.current_amounts if self.current_amounts else '0',
            self.current_credits if self.current_credits else '0',
        )


class Partner(models.Model):
    """
    城市合伙人，手机号作为唯一标识
    """
    name = models.CharField(_('名字'), max_length=255, null=True)
    mobile = models.CharField(_('手机'), max_length=255, null=True, unique=True)
    related_customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('城市合伙人')
        verbose_name_plural = _('城市合伙人')

    def __str__(self):
        return "{0} {1}".format(
            self.name,
            self.mobile if self.mobile else '',
        )


class StoreInfo(models.Model):
    """
    门店信息
    """
    name = models.CharField(_('名称'), max_length=200, null=True, unique=True)
    contact = models.CharField(_('联系电话'), max_length=200, null=True, blank=True)
    address = models.TextField(_('地址'), max_length=1000, null=True, blank=True)
    image = models.ImageField(_('照片'), upload_to='', null=True, blank=True)
    is_active = models.BooleanField(_('有效'), default=True)
    desc = models.TextField(_('介绍'), max_length=2000, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        ordering = ['id']
        verbose_name = _('门店信息')
        verbose_name_plural = _('门店信息')

    def __str__(self):
        return "{}".format(
            self.name,
        )


class CarInfo(models.Model):
    """
    车辆信息
    """
    car_number = models.CharField(_('车牌'), max_length=100, null=True,  blank=True, unique=True)
    car_brand = models.CharField(_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(_('汽车型号'), max_length=255, null=True, blank=True)
    car_price = models.IntegerField(_('购买价格/万'), null=True, blank=True)
    bought_date = models.DateField(_('购买日期'), null=True, blank=True)
    annual_inspection_date = models.DateField(_('车辆年检日期'), null=True, blank=True)
    insurance_date = models.DateField(_('交强险到期日'), null=True, blank=True)
    insurance_company = models.CharField(_('保险公司'), max_length=255, null=True, blank=True)
    desc = models.TextField(_('描述'), max_length=1000, null=True, blank=True)
    is_confirmed = models.BooleanField(_('已审核'), default=False)
    is_active = models.BooleanField(_('有效'), default=True)
    customer = models.ForeignKey(
        Customer,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('客户')
    )
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='car_info_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='car_info_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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
    name = models.CharField(_('保险出单公司'), max_length=200, null=True, unique=True)
    desc = models.CharField(_('显示名称'), max_length=200, null=True)
    display = models.BooleanField(_('用户是否可选'), default=True)
    is_active = models.BooleanField(_('是否有效'), default=True)

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
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='belong_to_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='belong_to_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)
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
    record_date = models.DateField(_('签单日期'), null=True)
    insurance_date = models.DateField(_('保单开始日期'), null=True, blank=True)
    total_price = models.DecimalField(
        verbose_name=_('含税总保费（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
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
    related_partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('城市合伙人')
    )
    tax = models.DecimalField(_('车船税（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
    has_payback = models.BooleanField(_('是否已返费'), default=False)
    payback_percent = models.DecimalField(
        verbose_name=_('已返费率'), max_digits=7, decimal_places=4, null=True, blank=True)
    payback_amount = models.DecimalField(
        verbose_name=_('已返金额（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
    ic_payback_percent = models.DecimalField(
        verbose_name=_('保险公司返点'), max_digits=7, decimal_places=4, null=True, blank=True)
    ic_payback_amount = models.DecimalField(
        verbose_name=_('返费金额（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
    profits = models.DecimalField(
        verbose_name=_('利润'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_payed = models.BooleanField(_('已支付'), default=True)

    insurance_jqx = models.BooleanField(
        verbose_name=_('交强险'),
        help_text=_(
            '中国首个由国家法律规定实行的强制保险制度。'
            '其保费是实行全国统一收费标准的，由国家统一规定的，但是不同的汽车型号的交强险价格也不同，主要影响因素是“汽车座位数”'),
        default=True)
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
        null=True,
        blank=True
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

    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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
    name = models.CharField(_('名称'), max_length=200, null=True, unique=True)
    icon = models.ImageField(_('图片'), upload_to='service_package_type', null=True, blank=True)
    desc = models.CharField(_('介绍'), max_length=200, null=True, blank=True)
    is_active = models.BooleanField(_('是否有效'), default=True)

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
    name = models.CharField(_('名称'), max_length=200, null=True,  unique=True)
    price = models.DecimalField(_('价格（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
    desc = models.CharField(_('介绍'), max_length=200, null=True, blank=True)
    is_active = models.BooleanField(_('是否有效'), default=True)
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
    name = models.CharField(_('名称'), max_length=200, null=True,  unique=True)
    price = models.DecimalField(_('价格（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
    desc = models.CharField(_('介绍'), max_length=200, null=True, blank=True)
    is_active = models.BooleanField(_('是否有效'), default=True)

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
    service_info = models.TextField(_('服务详情'), null=True, blank=True, max_length=200)
    reserve_type = models.IntegerField(_('服务类型'), null=True, blank=True, choices=[(1, '上门'), (2, '到店')])
    is_reversed = models.BooleanField(_('是预约服务'), default=False)
    reserve_time = models.DateTimeField(_('进厂时间'), null=True, blank=True)
    finish_time = models.DateTimeField(_('预计出厂时间'), null=True, blank=True)
    reserve_address = models.TextField(_('服务地点'), max_length=1000, null=True, blank=True)
    vehicle_mileage = models.IntegerField(_('当前行驶公里数'), null=True, blank=True)
    total_price = models.DecimalField(_('应收金额（元）'), default=0, decimal_places=2, max_digits=10)
    total_payed = models.DecimalField(_('实收金额（元）'), default=0, decimal_places=2, max_digits=10)
    total_cost = models.DecimalField(_('总成本（元）'), default=0, decimal_places=2, max_digits=10)
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='service_record_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(_('已联系/已确认'), default=False)
    related_partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('城市合伙人')
    )
    related_store = models.ForeignKey(
        StoreInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('维修门店')
    )
    is_served = models.BooleanField(_('服务已完成'), help_text=_('若服务已经完成，请勾选此项'), default=False)
    is_payed = models.BooleanField(_('已支付'), help_text=_('勾选此项会自动创建收银记录'), default=False)
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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


class ServiceItem(models.Model):
    related_service_record = models.ForeignKey(
        ServiceRecord,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('维修服务')
    )
    served_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('维修人员')
    )
    name = models.CharField(_('项目名称'), max_length=255, null=True, blank=True)
    item_price = models.DecimalField(_('单价（元）'), null=True, blank=True, decimal_places=2, max_digits=10)
    item_count = models.DecimalField(_('数量'), null=True, blank=True, default=1, decimal_places=2, max_digits=10)
    price = models.DecimalField(_('小计（元）'), null=True, blank=True, decimal_places=2, max_digits=10)
    cost = models.DecimalField(_('成本（元）'), null=True, blank=True, decimal_places=2, max_digits=10)
    notes = models.CharField(_('备注'), max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_item_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_item_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('维修项目')
        verbose_name_plural = _('维修项目')

    def __str__(self):
        return "{} {}".format(
            self.name,
            self.price,
        )


class ServiceFeedback(models.Model):
    related_service_record = models.ForeignKey(
        ServiceRecord,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('维修服务')
    )
    feedback_date = models.DateField(_('回访日期'), null=True, blank=True)
    feedback_by = models.ForeignKey(
        Superior,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('回访人员')
    )
    notes = models.CharField(_('备注'), max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_feedback_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_feedback_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('回访记录')
        verbose_name_plural = _('回访记录')

    def __str__(self):
        return "{} {}".format(
            self.related_service_record,
            self.feedback_by,
        )


class ServiceApply(models.Model):
    """
    服务申请
    """
    car_number = models.CharField(_('车牌'), max_length=100, null=True)
    car_brand = models.CharField(_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(_('汽车型号'), max_length=255, null=True, blank=True)
    name = models.CharField(_('名字'), max_length=255, null=True)
    mobile = models.CharField(_('手机'), max_length=255, null=True)
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
    service_info = models.TextField(_('服务详情'), null=True, blank=True,  max_length=200)
    reserve_type = models.IntegerField(_('类型'), null=True, blank=True, choices=[(1, '上门'), (2, '到店')])
    reserve_time = models.DateTimeField(_('服务时间'), null=True, blank=True)
    reserve_address = models.TextField(_('服务地点'), max_length=1000, null=True, blank=True)
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='service_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(_('已联系/已确认'), default=False)
    data_import = models.BooleanField(
        verbose_name=_('已导入维修服务'), help_text=_('勾选以后数据将会自动导入到【维修服务】列表'), default=False)
    related_record = models.ForeignKey(
        ServiceRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('关联记录')
    )
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_apply_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='service_apply_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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
            related_record, created = ServiceRecord.objects.get_or_create(
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
    保险申请，包括车辆续保
    """
    car_number = models.CharField(_('车牌'), max_length=100, null=True)
    car_brand = models.CharField(_('汽车品牌'), max_length=255, null=True, blank=True)
    car_model = models.CharField(_('汽车型号'), max_length=255, null=True, blank=True)
    name = models.CharField(_('名字'), max_length=255, null=True)
    mobile = models.CharField(_('手机'), max_length=255, null=True)
    service_type = models.IntegerField(
        verbose_name=_('类别'),
        help_text=_('1-->车辆续保, 2-->保险分期, 3-->车辆贷款'),
        null=True, blank=True, choices=[(1, '车辆续保'), (2, '保险分期'), (3, '车辆贷款')])
    insurance_date = models.DateField(_('保单开始日期'), null=True, blank=True)

    insurance_jqx = models.BooleanField(
        verbose_name=_('交强险'),
        help_text=_(
            '中国首个由国家法律规定实行的强制保险制度。'
            '其保费是实行全国统一收费标准的，由国家统一规定的，但是不同的汽车型号的交强险价格也不同，主要影响因素是“汽车座位数”'),
        default=True)
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
        null=True,
        blank=True
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
    insurance_company = models.CharField(
        verbose_name=_('保险公司'),
        max_length=100,
        null=True,
        blank=True
    )
    changed_times = models.CharField(
        verbose_name=_('过户次数'),
        choices=(('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')),
        max_length=100,
        null=True,
        blank=True,
        default='0'
    )
    money_needed = models.IntegerField(_('需求金额/元'), null=True, blank=True)

    money_jqx = models.DecimalField(_('交强险金额/元'), max_digits=10, decimal_places=2, null=True, blank=True)
    money_ccs = models.DecimalField(_('车船税金额/元'), max_digits=10, decimal_places=2, null=True, blank=True)
    money_syx = models.DecimalField(_('商业险金额/元'), max_digits=10, decimal_places=2, null=True, blank=True)
    stages = models.IntegerField(_('分期数'), null=True, blank=True, choices=[(3, 3), (6, 6), (9, 9)])
    down_payment = models.DecimalField(_('首付/元'), max_digits=10, decimal_places=2, null=True, blank=True)
    stage_payment = models.DecimalField(_('每期/元'), max_digits=10, decimal_places=2, null=True, blank=True)

    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='insurance_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(_('已联系/已确认'), default=False)
    data_import = models.BooleanField(
        verbose_name=_('已导入投保记录'), help_text=_('勾选以后数据将会自动导入到【投保记录】列表'), default=False)
    related_record = models.ForeignKey(
        InsuranceRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('关联记录')
    )
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_apply_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_apply_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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
        if self.data_import and self.service_type == 1:
            # 数据格式化
            car = get_car_info(self)
            # 添加保险记录
            fields = [
                'insurance_jqx', 'insurance_csx', 'insurance_fdjss', 'insurance_zrss', 'insurance_dqx', 'insurance_pl',
                'insurance_cshx', 'insurance_dsxr', 'insurance_sj', 'insurance_ck', 'insurance_hw',
                'created_by'
            ]
            data = {}
            for v in fields:
                data[v] = getattr(self, v)

            related_record, created = InsuranceRecord.objects.get_or_create(
                car=car,
                insurance_date=self.insurance_date,
                is_payed=False,
                **data
            )
            self.related_record = related_record
        super(InsuranceApply, self).save(*args, **kwargs)


class PartnerApply(models.Model):
    """
    城市合伙人申请
    """
    name = models.CharField(_('名字'), max_length=255, null=True)
    mobile = models.CharField(_('手机'), max_length=255, null=True)
    address = models.TextField(_('长期居住地'), max_length=1000, null=True, blank=True)
    professional = models.CharField(_('现就职业'), max_length=100, null=True, blank=True)
    reason = models.TextField(_('申请理由或资源'), max_length=1000, null=True, blank=True)
    checked_by = models.ForeignKey(
        Superior,
        on_delete=models.SET_NULL,
        related_name='partner_apply_check_by',
        null=True,
        blank=True,
        verbose_name=_('由谁联系')
    )
    is_checked = models.BooleanField(_('已联系/已确认'), default=False)
    is_confirmed = models.BooleanField(
        _('申请成功'),
        help_text=_('勾选此项，城市合伙人信息将自动与客户信息关联'),
        default=False)
    related_customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('关联客户')
    )
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='partner_apply_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='partner_apply_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('城市合伙人申请')
        verbose_name_plural = _('城市合伙人申请')

    def import_partner(self):
        if self.mobile:
            customer, created = Customer.objects.get_or_create(
                mobile=self.mobile, defaults={'name': self.name})
            customer.is_partner = True
            customer.save()
            self.related_customer = customer

    def __str__(self):
        return "{} {} {}".format(
            self.name,
            self.mobile,
            self.is_checked
        )

    def save(self, *args, **kwargs):
        if self.is_confirmed:
            self.import_partner()
        super(PartnerApply, self).save(*args, **kwargs)


class InsuranceRecordUpload(models.Model):
    """
    保险业绩数据导入
    """
    file = models.FileField(_('文件'), null=True, blank=True)
    file_name = models.CharField(_('文件名'), null=True, blank=True, max_length=255)
    total_count = models.IntegerField(_('总条数'), null=True, blank=True)
    created_count = models.IntegerField(_('添加条数'), null=True, blank=True)
    updated_count = models.IntegerField(_('更新条数'), null=True, blank=True)
    failed_count = models.IntegerField(_('失败条数'), null=True, blank=True)
    is_confirmed = models.BooleanField(_('已确认'), default=True)
    is_processed = models.BooleanField(_('已执行'), default=False)
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_upload_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='insurance_record_upload_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

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
            file_name = getattr(self, 'file').name
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
                        pass
                # 客户信息获取
                if data.get('mobile'):
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
                if data.get('insurance_company__name'):
                    insurance_company, insurance_company_created = InsuranceCompany.objects.get_or_create(
                        name=data['insurance_company__name'],
                        defaults={'desc': data['insurance_company__name'], 'display': False, 'is_active': True}
                    )
                else:
                    insurance_company = None
                for p in foreign_keys:
                    if p in data:
                        data.pop(p)
                ir, ir_created = InsuranceRecord.objects.update_or_create(
                    car=car,
                    belong_to=belong_to,
                    insurance_company=insurance_company,
                    has_payback=True,
                    is_payed=True,
                    notes='自动导入数据-{0}-{1}'.format(file_name, r.Index),
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


class PayedRecord(models.Model):
    related_store = models.ForeignKey(
        StoreInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('关联门店')
    )
    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('关联客户')
    )
    payed_date = models.DateField(_('支付日期'),  null=True, blank=True, default=timezone.now)
    related_service_record = models.ForeignKey(
        ServiceRecord,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联服务')
    )
    related_insurance_record = models.ForeignKey(
        InsuranceRecord,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联保险')
    )
    total_price = models.DecimalField(_('应收金额（元）'), default=0, decimal_places=2, max_digits=10)
    total_payed = models.DecimalField(
        _('实收金额（元）'),
        help_text=_('如果是挂账，请填写0'),
        default=0, decimal_places=2, max_digits=10)
    amount_payed = models.DecimalField(_('余额抵扣（元）'), default=0, decimal_places=2, max_digits=10)
    credit_payed = models.DecimalField(_('积分抵扣（元）'), default=0, decimal_places=2, max_digits=10)
    credit_change = models.BigIntegerField(_('积分获得'), help_text=_('现金支付，每满20元获得1积分'), default=0)
    cash_payed = models.DecimalField(_('现金支付（元）'), null=True, blank=True, decimal_places=2, max_digits=10)
    is_confirmed = models.BooleanField(_('已确认'), default=False)
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='income_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='income_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('收银记录')
        verbose_name_plural = _('收银记录')

    def __str__(self):
        return "{} {}".format(
            self.customer,
            self.total_payed
        )


class AmountChangeRecord(models.Model):
    """
    余额变更记录
    """
    customer = models.ForeignKey(
        Customer,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联客户')
    )
    amounts = models.DecimalField(
        verbose_name=_('金额变更（元）'), max_digits=10, decimal_places=2, null=True)
    current_amounts = models.DecimalField(
        verbose_name=_('变更后余额（元）'), max_digits=10, decimal_places=2, null=True, blank=True)
    related_payed_record = models.ForeignKey(
        PayedRecord,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联收银记录')
    )
    change_type = models.SmallIntegerField(
        _('变更类型'), default=1, choices=[(1, '充值'), (2, '支付'), (3, '合伙人收益'), (4, '其他')],
        help_text="1-->充值, 2-->支付, 3-->合伙人收益, 4-->其他"
    )
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='amount_change_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='amount_change_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('余额变更记录')
        verbose_name_plural = _('余额变更记录')

    def __str__(self):
        return "{0} {1} {2}".format(
            self.customer,
            self.amounts,
            self.notes,
        )


class CreditChangeRecord(models.Model):
    """
    积分变更记录
    """
    customer = models.ForeignKey(
        Customer,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联客户')
    )
    credits = models.BigIntegerField(_('积分变更'), null=True)
    current_credits = models.BigIntegerField(_('变更后积分'), null=True, blank=True)
    related_payed_record = models.ForeignKey(
        PayedRecord,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('关联收银记录')
    )
    change_type = models.SmallIntegerField(
        _('变更类型'), default=1, choices=[(1, '消费获取'), (2, '活动获取'), (3, '支付抵扣'), (4, '其他')],
        help_text="1-->消费获取, 2-->活动获取, 3-->支付抵扣, 4-->其他"
    )
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='credit_change_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='credit_change_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('积分变更记录')
        verbose_name_plural = _('积分变更记录')

    def __str__(self):
        return "{0} {1} {2}".format(
            self.customer,
            self.credits,
            self.notes,
        )


class ReportMake(models.Model):
    report_type = models.CharField(
        verbose_name=_('报告类型'),
        choices=(('归属统计', '归属统计'),),
        null=True, blank=True, max_length=255)
    file = models.FileField(_('报告文件'), null=True, blank=True, upload_to='report', editable=False)
    is_processed = models.BooleanField(_('已执行'), default=False)
    date_start = models.DateField(_('开始日期'), null=True, blank=True)
    date_end = models.DateField(_('结束日期'), null=True, blank=True)
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='report_make_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='report_make_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('报告生成')
        verbose_name_plural = _('报告生成')

    def __str__(self):
        return "{}".format(
            self.pk
        )


class MsgSendRecord(models.Model):
    mobile = models.CharField(_('手机'), max_length=20, null=True)
    code = models.CharField(_('验证码'), max_length=20, null=True, blank=True)
    paras = models.CharField(_('数据'), max_length=200, null=True, blank=True)
    msg_type = models.IntegerField(_('短信类型'), null=True, choices=[(1, '验证码'), (2, '支付记录')])
    notes = models.TextField(_('备注'), max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='msg_send_record_created_by',
        verbose_name=_('创建人员')
    )
    confirmed_by = models.ForeignKey(
        WxUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='msg_send_record_confirmed_by',
        verbose_name=_('审核人员')
    )
    datetime_created = models.DateTimeField(_('记录时间'), auto_now_add=True)
    datetime_updated = models.DateTimeField(_('更新时间'), auto_now=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-id']
        verbose_name = _('短信发送记录')
        verbose_name_plural = _('短信发送记录')

    def __str__(self):
        return "{} {}".format(
            self.mobile,
            self.paras
        )


@receiver(pre_save, sender=WxUser)
def create_username_password(sender, instance, **kwargs):
    key = settings.SECRET_KEY
    if not instance.username and not instance.password:
        if instance.openid:
            instance.username = hashlib.pbkdf2_hmac(
                "sha256", getattr(instance, 'openid').encode(encoding='utf-8'), key.encode(encoding='utf-8'), 10
            ).hex()
            raw_password = hashlib.pbkdf2_hmac(
                "sha256", instance.username.encode(), getattr(instance, 'openid').encode(encoding='utf-8'), 10
            ).hex()
            instance.password = make_password(raw_password)
        else:
            if instance.openid_gzh:
                instance.username = hashlib.pbkdf2_hmac(
                    "sha256", getattr(instance, 'openid_gzh').encode(encoding='utf-8'), key.encode(encoding='utf-8'), 10
                ).hex()
                raw_password = hashlib.pbkdf2_hmac(
                    "sha256", instance.username.encode(), getattr(instance, 'openid_gzh').encode(encoding='utf-8'), 10
                ).hex()
                instance.password = make_password(raw_password)


@receiver(post_save, sender=WxUser)
def update_related_customers(sender, instance, **kwargs):
    """
    如果用户填写了手机号，自动合并相同手机号的用户，并将手机号相同的客户关联到此账号
    """
    if instance.mobile:
        # 理论上用户可以有多个账号，同一个微信号可以注册公众号和小程序的账号，填写手机号后，将公众号和小程序注册的账号进行合并
        related_users = WxUser.objects.filter(mobile=instance.mobile).exclude(pk=instance.pk, is_staff=True)
        # 自动进行账号合并
        if instance.openid_gzh and not instance.openid:
            for u in related_users:
                if u.openid:
                    openid = u.openid
                    u.delete()
                    instance.openid = openid
        elif instance.openid and not instance.openid_gzh:
            for u in related_users:
                if u.openid_gzh:
                    openid_gzh = u.openid_gzh
                    u.delete()
                    instance.openid_gzh = openid_gzh
        # 手机号更新以后，以前关联的客户关系不变
        # related_customers = Customer.objects.filter(related_user=instance.pk)
        # for rc in related_customers:
        #     rc.related_user.remove(instance.pk)
        #     rc.save()
        # 根据手机号查找关联客户
        customer, created = Customer.objects.get_or_create(
            mobile=instance.mobile, defaults={'name': instance.nick_name})
        # todo 测试
        customer.related_user.add(instance.pk)
        customer.save()


@receiver(post_save, sender=Customer)
def post_save_customer(sender, instance, **kwargs):
    # 客户更新以后更新合伙人列表
    if instance.is_partner:
        Partner.objects.update_or_create(
            related_customer_id=instance.pk,
            defaults={
                'name': instance.name,
                'mobile': instance.mobile,
            })
    else:
        Partner.objects.filter(related_customer_id=instance.pk).delete()


@receiver(pre_save, sender=ServiceItem)
def pre_save_service_item(sender, instance, **kwargs):
    if instance.item_price and instance.item_count:
        instance.price = float(getattr(instance, 'item_price')) * int(getattr(instance, 'item_count'))


@receiver([post_save, post_delete], sender=ServiceItem)
def update_related_service_record(sender, instance, **kwargs):
    total_price = 0
    total_cost = 0
    if instance.related_service_record:
        items = ServiceItem.objects.filter(
            related_service_record_id=getattr(instance, 'related_service_record_id')
        ).values('price', 'cost')
        for it in items:
            # price 计算
            price = it.get('price', 0)
            if price:
                price = float(price)
            else:
                price = 0
            total_price = total_price + price
            # cost 计算
            cost = it.get('cost', 0)
            if cost:
                cost = float(cost)
            else:
                cost = 0
            total_cost = total_cost + cost
        ServiceRecord.objects.filter(
            pk=getattr(instance, 'related_service_record_id')
        ).update(total_price=total_price, total_cost=total_cost)


@receiver(pre_save, sender=PayedRecord)
def update_cash_payed(sender, instance, **kwargs):
    # 自动计算现金支付金额和积分获得
    if instance.total_payed:
        total_payed = float(getattr(instance, 'total_payed'))
        amount_payed = 0
        credit_payed = 0
        if instance.amount_payed:
            amount_payed = float(getattr(instance, 'amount_payed'))
        if instance.credit_payed:
            credit_payed = float(getattr(instance, 'credit_payed'))
        # 现金支付
        cash_payed = total_payed - amount_payed - credit_payed
        instance.cash_payed = cash_payed
        # 积分获得
        instance.credit_change = cash_payed // 20


@receiver(post_save, sender=PayedRecord)
def post_save_payed_record(sender, instance, **kwargs):
    # 如果有余额支付的情况，自动创建余额变更记录
    if instance.amount_payed and instance.customer:
        amounts_change = - float(getattr(instance, 'amount_payed'))
        AmountChangeRecord.objects.update_or_create(
            related_payed_record_id=instance.pk,
            change_type=2,
            defaults={
                'amounts': amounts_change,
                'customer': instance.customer,
                'created_by': instance.created_by,
                'notes': '余额支付',
            })
    if instance.customer:
        # 积分消耗
        if instance.credit_payed:
            credits_used = - float(getattr(instance, 'credit_payed'))
            CreditChangeRecord.objects.update_or_create(
                related_payed_record_id=instance.pk,
                change_type=3,
                defaults={
                    'credits': credits_used,
                    'customer': instance.customer,
                    'created_by': instance.created_by,
                    'notes': '积分抵扣'
                }
            )
        # 积分获得
        if instance.credit_change:
            credits_get = float(getattr(instance, 'credit_change'))
            CreditChangeRecord.objects.update_or_create(
                related_payed_record_id=instance.pk,
                change_type=1,
                defaults={
                    'credits': credits_get,
                    'customer': instance.customer,
                    'created_by': instance.created_by,
                    'notes': '现金支付获得积分'
                }
            )


@receiver([pre_save, post_delete], sender=AmountChangeRecord)
def pre_save_amount_change_record(sender, instance, **kwargs):
    # todo delete 测试
    current_amounts = 0
    current_amounts_all = 0
    # todo 可进行优化
    all_records = AmountChangeRecord.objects.filter(customer=instance.customer)
    if instance.pk:
        # 排除当前记录
        all_records = all_records.exclude(pk=instance.pk)
    for r in all_records.values('amounts'):
        current_amounts_all += float(r['amounts'])
    current_amounts_all += float(instance.amounts)  # 计算总余额
    # 更新客户的余额
    Customer.objects.filter(pk=getattr(instance, 'customer').id).update(current_amounts=round(current_amounts_all, 2))
    # 计算当前记录的余额
    if instance.pk:
        pre_records = all_records.filter(pk__lt=instance.pk)
        for r in pre_records.values('amounts'):
            current_amounts += float(r['amounts'])
        current_amounts += float(instance.amounts)
    else:
        current_amounts = current_amounts_all
    instance.current_amounts = round(current_amounts, 2)


@receiver(post_save, sender=AmountChangeRecord)
def post_save_amount_change_record(sender, instance, **kwargs):
    after_record = AmountChangeRecord.objects.filter(
        customer=instance.customer, pk__gt=instance.pk).order_by('pk').first()
    if after_record:
        after_record.save()


@receiver([pre_save, post_delete], sender=CreditChangeRecord)
def pre_save_credit_change_record(sender, instance, **kwargs):
    current_credits = 0
    current_credits_all = 0
    # todo 可进行优化
    all_records = CreditChangeRecord.objects.filter(customer=instance.customer)
    if instance.pk:
        all_records = all_records.exclude(pk=instance.pk)
    for r in all_records.values('credits'):
        current_credits_all += int(r['credits'])
    current_credits_all += int(instance.credits)
    # 更新客户的积分
    Customer.objects.filter(pk=getattr(instance, 'customer').id).update(current_credits=current_credits_all)
    # 计算当前记录的剩余积分
    if instance.pk:
        pre_records = all_records.filter(pk__lte=instance.pk)
        for r in pre_records.values('credits'):
            current_credits += int(r['credits'])
        current_credits += int(instance.credits)
    else:
        current_credits = current_credits_all
    instance.current_credits = current_credits


@receiver(post_save, sender=CreditChangeRecord)
def post_save_credit_change_record(sender, instance, **kwargs):
    after_record = CreditChangeRecord.objects.filter(
        customer=instance.customer, pk__gt=instance.pk).order_by('pk').first()
    if after_record:
        after_record.save()


@receiver(post_save, sender=InsuranceRecord)
def post_save_insurance_record(sender, instance, **kwargs):
    # 自动创建收款记录
    if instance.is_payed:
        total_payed = 0
        total_price = 0
        customer = None
        if instance.total_price:
            total_price = float(instance.total_price)
            if instance.payback_amount:
                total_payed = float(instance.total_price) - float(instance.payback_amount)
            else:
                total_payed = float(instance.total_price)
        if instance.car:
            customer = instance.car.customer
        # 不管有没有关联客户，都要创建收款记录 todo 测试
        related_payed_record, created = PayedRecord.objects.update_or_create(
            related_insurance_record=instance,
            defaults={
                'customer': customer,
                'total_price': total_price,
                'total_payed': total_payed,
                'created_by': instance.created_by,
                'confirmed_by': instance.confirmed_by,
                'payed_date': instance.record_date,
                'notes': '投保支付'
            },
        )
        # 如果有关联合伙人
        if instance.related_partner:
            partner_customer = instance.related_partner.related_customer
            if partner_customer:
                # 合伙人收益 2%
                partner_amount_get = total_price * 0.02
                if customer:
                    customer_name = customer.name
                else:
                    customer_name = '某人'
                AmountChangeRecord.objects.update_or_create(
                    related_payed_record=related_payed_record,
                    change_type=3,
                    defaults={
                        'customer': partner_customer,
                        'amounts': partner_amount_get,
                        'notes': '{0}投保{1:.2f}元收益'.format(
                            customer_name,
                            float(total_price))
                    },
                )
    else:
        PayedRecord.objects.filter(related_insurance_record_id=instance.pk).delete()


@receiver(post_save, sender=ServiceRecord)
def post_save_service_record(sender, instance, **kwargs):
    if instance.is_payed:
        # 自动创建收支记录
        customer = None
        if instance.car:
            customer = instance.car.customer
        # 不管有没有客户，都要创建收款记录 todo 测试
        total_payed = instance.total_payed
        related_payed_record, created = PayedRecord.objects.update_or_create(
            related_service_record=instance,
            defaults={
                'customer': customer,
                'total_price': instance.total_price,
                'total_payed': instance.total_payed,
                'created_by': instance.created_by,
                'confirmed_by': instance.confirmed_by,
                'payed_date': instance.datetime_updated,
                'notes': '服务支付'
            }
        )
        # 如果有关联合伙人
        if instance.related_partner:
            if total_payed:
                partner_customer = instance.related_partner.related_customer
                if partner_customer:
                    # 合伙人收益为实收金额的 5%
                    partner_amount_get = float(total_payed) * 0.05
                    if customer:
                        customer_name = customer.name
                    else:
                        customer_name = '某人'
                    AmountChangeRecord.objects.update_or_create(
                        related_payed_record=related_payed_record,
                        change_type=3,
                        defaults={
                            'customer': partner_customer,
                            'amounts': partner_amount_get,
                            'notes': '{0}消费{1:.2f}元收益'.format(
                                customer_name,
                                float(total_payed))
                        },
                    )
    else:
        PayedRecord.objects.filter(related_service_record_id=instance.pk).delete()
