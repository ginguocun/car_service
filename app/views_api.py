import json
import logging
import random
import re
from datetime import datetime

import requests
from django_filters import rest_framework as filters

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from weixin import WXAPPAPI
from weixin.oauth2 import OAuth2AuthExchangeError

from car.sms_aliyun import sms_code
from car.utils import NormalResultsSetPagination

from .serializers import *


logger = logging.getLogger('django')


class AppFilter(filters.FilterSet):

    @classmethod
    def filter_for_field(cls, field, field_name, lookup_expr='exact'):
        filter_class = super().filter_for_field(field, field_name, lookup_expr)
        if lookup_expr == 'exact':
            filter_class.extra['help_text'] = '{0} 等于'.format(field.verbose_name)
        elif lookup_expr == 'contains':
            filter_class.extra['help_text'] = '{0} 包含'.format(field.verbose_name)
        elif lookup_expr == 'gte':
            filter_class.extra['help_text'] = '{0} 大于等于'.format(field.verbose_name)
        elif lookup_expr == 'gt':
            filter_class.extra['help_text'] = '{0} 大于'.format(field.verbose_name)
        elif lookup_expr == 'lt':
            filter_class.extra['help_text'] = '{0} 小于'.format(field.verbose_name)
        elif lookup_expr == 'lte':
            filter_class.extra['help_text'] = '{0} 小于等于'.format(field.verbose_name)
        return filter_class


def create_or_update_user_info(openid, user_info):
    """
    创建或者更新用户信息
    :param openid: 微信 openid
    :param user_info: 微信用户信息
    :return: 返回用户对象
    """
    if openid:
        if user_info:
            user, created = WxUser.objects.update_or_create(openid=openid, defaults=user_info)
        else:
            user, created = WxUser.objects.get_or_create(openid=openid)
        return user
    return None


def create_or_update_user_info_gzh(openid_gzh, user_info):
    """
    创建或者更新用户信息
    :param openid_gzh: 微信 openid
    :param user_info: 微信用户信息
    :return: 返回用户对象
    """
    if openid_gzh:
        if user_info:
            user, created = WxUser.objects.update_or_create(openid_gzh=openid_gzh, defaults=user_info)
        else:
            user, created = WxUser.objects.get_or_create(openid_gzh=openid_gzh)
        return user
    return None


@api_view(["GET"])
def api_root(request):
    urls = {'method': request.method, 'admin': '/admin/', 'api': '/api/'}
    return Response(urls)


class WxLoginView(APIView):
    """
    post:
    小程序的微信登录接口，传递参数 {'code': '', 'user_info': ''}
    """
    authentication_classes = []
    permission_classes = []
    fields = {
        'nick_name': 'nickName',
        'gender': 'gender',
        'language': 'language',
        'city': 'city',
        'province': 'province',
        'country': 'country',
        'avatar_url': 'avatarUrl',
    }

    def post(self, request):
        user_info = dict()
        code = request.data.get('code')
        logger.info("Code: {0}".format(code))
        user_info_raw = request.data.get('user_info', {})
        if isinstance(user_info_raw, str):
            user_info_raw = json.loads(user_info_raw)
        if not isinstance(user_info_raw, dict):
            user_info_raw = {}
        logger.info("user_info: {0}".format(user_info_raw))
        if code:
            api = WXAPPAPI(appid=settings.WX_APP_ID, app_secret=settings.WX_APP_SECRET)
            try:
                session_info = api.exchange_code_for_session_key(code=code)
            except OAuth2AuthExchangeError:
                session_info = None
            if session_info:
                openid = session_info.get('openid', None)
                if openid:
                    if user_info_raw:
                        for k, v in self.fields.items():
                            user_info[k] = user_info_raw.get(v)
                    user = create_or_update_user_info(openid, user_info)
                    if user:
                        token = AppTokenObtainPairSerializer.get_token(user).access_token
                        return Response(
                            {
                                'jwt': str(token),
                                'user': model_to_dict(
                                    user,
                                    fields=[
                                        'full_name', 'mobile', 'gender',
                                        'is_partner', 'is_client', 'is_manager'
                                    ])
                            },
                            status=HTTP_200_OK)
        return Response({'jwt': None, 'user': {}}, status=HTTP_204_NO_CONTENT)


def get_access_token(code):
    """
    公众号微信授权，通过 code 获取 access_token
    :param code: 前端获取的 code
    :return: 返回 {"access_token":"","expires_in":7200,"refresh_token":"","openid":"","scope":"snsapi_userinfo"}
    """
    data = dict()
    if code:
        res = requests.get(
            url='https://api.weixin.qq.com/sns/oauth2/access_token?'
                'appid={0}&'
                'secret={1}&'
                'code={2}&'
                'grant_type=authorization_code'.format(
                    settings.WX_GZH_APP_ID,
                    settings.WX_GZH_APP_SECRET,
                    code))
        if res.status_code == 200:
            data = res.json()
    return data


def get_wx_gzh_user_info(code):
    """
    公众号微信授权，通过 code 获取用户信息
    :param code: 前端获取的 code
    :return: {
          "openid":" OPENID",
          "nickname": NICKNAME,
          "sex":"1",
          "province":"PROVINCE",
          "city":"CITY",
          "country":"COUNTRY",
          "headimgurl": "",
          "privilege":[ "PRIVILEGE1" "PRIVILEGE2"],
          "unionid": ""
        }
    """
    data = get_access_token(code)
    user_info = dict()
    access_token = data.get('access_token')
    openid = data.get('openid')
    if access_token and openid:
        res = requests.get(
            url='https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'.format(
                access_token,
                openid))
        if res.status_code == 200:
            user_info = res.json()
    return user_info


class WxGzhLoginView(APIView):
    """
    post:
    公众号登录接口，传递参数 {'code': ''}
    """
    authentication_classes = []
    permission_classes = []
    fields = {
        'openid': 'openid',
        'nick_name': 'nickname',
        'language': 'language',
        'gender': 'sex',
        'city': 'city',
        'province': 'province',
        'country': 'country',
        'avatar_url': 'headimgurl',
    }

    def post(self, request):
        user_info = dict()
        code = request.data.get('code')
        logger.info("Code: {0}".format(code))
        # 通过 code 获取用户信息
        user_info_raw = get_wx_gzh_user_info(code)
        if isinstance(user_info_raw, str):
            user_info_raw = json.loads(user_info_raw)
        if not isinstance(user_info_raw, dict):
            user_info_raw = {}
        logger.info("user_info: {0}".format(user_info_raw))
        if user_info_raw:
            openid_gzh = None
            for k, v in self.fields.items():
                if k == 'openid':
                    openid_gzh = user_info_raw.get('openid')
                else:
                    current_v = user_info_raw.get(v)
                    if current_v:
                        if isinstance(current_v, str):
                            current_v = current_v.encode('iso-8859-1').decode('utf-8')
                        user_info[k] = current_v
            if openid_gzh:
                user = create_or_update_user_info_gzh(openid_gzh, user_info)
                if user:
                    token = AppTokenObtainPairSerializer.get_token(user).access_token
                    return Response(
                        {
                            'jwt': str(token),
                            'user': model_to_dict(
                                user,
                                fields=[
                                    'nick_name', 'full_name', 'mobile', 'gender', 'avatar_url',
                                    'is_partner', 'is_client', 'is_manager'
                                ])
                        },
                        status=HTTP_200_OK)
        return Response({'jwt': None, 'user': {}}, status=HTTP_204_NO_CONTENT)


class AppTokenObtainPairView(TokenObtainPairView):
    """
    Token Obtain API
    """
    serializer_class = AppTokenObtainPairSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return True  # To not perform the csrf check previously happening


class AppListCreateApi(ListCreateAPIView):

    # authentication_classes = (JWTAuthentication, CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated, )
    authentication_classes = ()
    permission_classes = ()
    pagination_class = NormalResultsSetPagination

    def create(self, request, *args, **kwargs):
        new_data = dict()
        for k, v in request.data.items():
            new_data[k] = v
        if self.request.user:
            new_data['created_by'] = getattr(self.request.user, 'id')
        serializer = self.get_serializer(data=new_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class AppListApi(ListAPIView):

    authentication_classes = (JWTAuthentication, CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated, )
    pagination_class = NormalResultsSetPagination


class AppApi(APIView):

    authentication_classes = (JWTAuthentication, CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated, )


class ServicePackageTypeListView(ListAPIView):
    """
    get:
    获取套餐类别列表
    """
    pagination_class = None
    permission_classes = ()
    queryset = ServicePackageType.objects.filter(is_active=True).order_by('name')
    serializer_class = ServicePackageTypeSerializer


class ServicePackageFilter(AppFilter):
    class Meta:
        model = ServicePackage
        fields = {
            'service_type': ['exact'],
        }


class ServicePackageListView(ListAPIView):
    """
    get:
    获取保养套餐列表
    """
    pagination_class = None
    permission_classes = ()
    queryset = ServicePackage.objects.order_by('name')
    serializer_class = ServicePackageSerializer
    filterset_class = ServicePackageFilter


class OilPackageListView(ListAPIView):
    """
    get:
    获取机油套餐列表
    """
    pagination_class = None
    permission_classes = ()
    queryset = OilPackage.objects.order_by('name')
    serializer_class = OilPackageSerializer


class StoreInfoListView(ListAPIView):
    """
    get:
    获取门店信息列表
    """
    pagination_class = None
    permission_classes = ()
    queryset = StoreInfo.objects.order_by('name')
    serializer_class = StoreInfoSerializer
    search_fields = ('name', 'address')


class InsuranceCompanyListView(ListAPIView):
    """
    get:
    获取保险公司列表
    """
    pagination_class = None
    permission_classes = ()
    queryset = InsuranceCompany.objects.filter(display=True, is_active=True).order_by('pk')
    serializer_class = InsuranceCompanySerializer
    search_fields = ('name',)


class ServiceApplyListView(AppListCreateApi):
    """
    get:
    获取维修服务申请列表，如果不是后台管理员用户，只能获取自己的申请记录。

    post:
    提交维修服务申请
    """
    queryset = ServiceApply.objects.order_by('-pk')
    serializer_class = ServiceApplySerializer
    search_fields = ('car_number', 'car_brand')

    def get_queryset(self):
        if self.request.user.id:
            if not self.request.user.is_staff:
                return self.queryset.filter(created_by_id=self.request.user.id)
            return self.queryset
        else:
            return self.queryset.none()


class InsuranceApplyListView(AppListCreateApi):
    """
    get:
    获取保险服务申请列表，如果不是后台管理员用户，只能获取自己的申请记录。

    post:
    保险服务申请，包含车辆续保、保险分期、购车贷款等提交
    """
    queryset = InsuranceApply.objects.order_by('-pk')
    serializer_class = InsuranceApplySerializer
    search_fields = ('car_number', 'car_brand')

    def get_queryset(self):
        if self.request.user.id:
            if not self.request.user.is_staff:
                return self.queryset.filter(created_by_id=self.request.user.id)
            return self.queryset
        else:
            return self.queryset.none()


class PartnerApplyListView(AppListCreateApi):
    """
    get:
    获取城市合伙人申请列表，如果不是后台管理员用户，只能获取自己的申请记录。

    post:
    提交城市合伙人申请
    """
    queryset = PartnerApply.objects.order_by('-pk')
    serializer_class = PartnerApplySerializer
    search_fields = ('name', 'mobile')

    def get_queryset(self):
        if self.request.user.id:
            if not self.request.user.is_staff:
                return self.queryset.filter(created_by_id=self.request.user.id)
            return self.queryset
        else:
            return self.queryset.none()


class AmountChangeRecordListView(AppListApi):
    """
    get:
    获取自己的余额变更记录，主要获取 amounts、notes 和 datetime_created 字段的数据。amounts-->金额， notes-->备注, datetime_created-->创建日期
    """
    queryset = AmountChangeRecord.objects.order_by('-pk')
    serializer_class = AmountChangeRecordSerializer
    search_fields = ('customer__mobile', 'customer__name')

    def get_queryset(self):
        if self.request.user.id:
            return self.queryset.filter(customer__related_user_id=self.request.user.id)
        return self.queryset.none()


class CreditChangeRecordListView(AppListApi):
    """
    get:
    获取自己的积分变更记录，主要获取 credits、notes 和 datetime_created 字段的数据。credits-->积分， notes-->备注, datetime_created-->创建日期
    """
    queryset = CreditChangeRecord.objects.order_by('-pk')
    serializer_class = CreditChangeRecordSerializer
    search_fields = ('customer__mobile', 'customer__name')

    def get_queryset(self):
        if self.request.user.id:
            return self.queryset.filter(customer__related_user_id=self.request.user.id)
        return self.queryset.none()


def get_user_detail(user):
    """
    获取用户的信息
    :param user: 用户对象
    :return: 返回用户信息
    """
    res = {
        'user': dict(),
        'amount_records': list(),
        'credit_records': list(),
        'current_amounts': None,
        'current_credits': None,
        'bank_account_name': None,
        'bank_account_no': None,
        'bank_name': None,
    }
    if user:
        res['user'] = model_to_dict(
            user,
            fields=[
                'id', 'nick_name', 'full_name', 'mobile', 'gender', 'avatar_url',
                'is_partner', 'is_client', 'is_manager'
            ])
        amount_records_q = AmountChangeRecord.objects.filter(
            customer__related_user=user
        ).order_by('-pk').values(
            'pk', 'customer__name', 'amounts', 'current_amounts', 'datetime_created', 'notes')
        for ar in amount_records_q:
            res['amount_records'].append(
                {
                    'pk': ar.get('pk'),
                    'name': ar.get('customer__name'),
                    'amounts': ar.get('amounts'),
                    'current_amounts': ar.get('current_amounts'),
                    'notes': ar.get('notes'),
                    'datetime_created': ar.get('datetime_created'),
                }
            )
        credit_records_q = CreditChangeRecord.objects.filter(
            customer__related_user=user
        ).order_by('-pk').values(
            'pk', 'customer__name', 'credits', 'current_credits', 'datetime_created', 'notes')
        for cr in credit_records_q:
            res['credit_records'].append(
                {
                    'pk': cr.get('pk'),
                    'name': cr.get('customer__name'),
                    'credits': cr.get('credits'),
                    'current_credits': cr.get('current_credits'),
                    'notes': cr.get('notes'),
                    'datetime_created': cr.get('datetime_created')
                }
            )
        fs = ['bank_account_name', 'bank_account_no', 'bank_name', 'current_amounts', 'current_credits']
        related_customer = Customer.objects.values(*fs).filter(related_user=user).first()
        if related_customer:
            for f in fs:
                res[f] = related_customer.get(f)
    return res


class UserInfoView(AppApi):
    """
    get:
    获取自己的用户信息
    """
    def get(self, request):
        if self.request.user.id:
            user = WxUser.objects.filter(pk=request.user.id).first()
            if user:
                res = get_user_detail(user)
                return Response(res, status=HTTP_200_OK)
        return Response({'detail': '请登录'}, status=HTTP_401_UNAUTHORIZED)


class UpdateMobileView(AppApi):
    """
    post:
    更新手机号，字段 mobile 和 code
    """
    def post(self, request):
        if self.request.user.id:
            user = WxUser.objects.filter(pk=request.user.id).first()
            pre_related_customers = Customer.objects.filter(related_user=user)
            mobile = request.data.get('mobile', '')
            code = request.data.get('code', '')
            if re.match(r"^1[2-9]\d{9}$", mobile):
                if code:
                    code_msg = MsgSendRecord.objects.filter(
                        mobile=str(mobile), msg_type=1, code=str(code)
                    ).order_by('-pk').first()
                    if code_msg:
                        if (datetime.now() - code_msg.datetime_created).seconds < 300:
                            # 如果用户之前已经有手机号，并且已经关联了客户信息，用户更新手机号会同步更新关联客户的手机号
                            if pre_related_customers.exists() and user.mobile:
                                exist_customer = Customer.objects.filter(mobile=mobile).first()
                                # 新提供的手机号是否已经存在
                                if not exist_customer:
                                    # 如果不存在，直接更新
                                    pre_related_customers.filter(mobile=user.mobile).update(mobile=mobile)
                                else:
                                    # 如果存在，将之前相同手机号的关联用户删除，然后将用户关联到已经存在的客户上
                                    pre_related_customer = pre_related_customers.filter(mobile=user.mobile).first()
                                    pre_related_customer.related_user.remove(user.pk)
                                    pre_related_customer.save()

                                    exist_customer.related_user.add(user.pk)
                                    exist_customer.save()
                            user.mobile = mobile
                            user.save()
                            res = get_user_detail(user)
                            return Response(res, status=HTTP_200_OK)
                        return Response({'detail': '验证码过期'}, status=HTTP_400_BAD_REQUEST)
                    return Response({'detail': '验证失败'}, status=HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': '验证码未提供'}, status=HTTP_400_BAD_REQUEST)
                    # 如果用户之前已经有手机号，并且已经关联了客户信息，用户更新手机号会同步更新关联客户的手机号
                    # if pre_related_customers.exists() and user.mobile:
                    #     exist_customer = Customer.objects.filter(mobile=mobile).first()
                    #     # 新提供的手机号是否已经存在
                    #     if not exist_customer:
                    #         # 如果不存在，直接更新
                    #         pre_related_customers.filter(mobile=user.mobile).update(mobile=mobile)
                    #     else:
                    #         # 如果存在，将之前相同手机号的关联用户删除，然后将用户关联到已经存在的客户上
                    #         pre_related_customer = pre_related_customers.filter(mobile=user.mobile).first()
                    #         pre_related_customer.related_user.remove(user.pk)
                    #         pre_related_customer.save()
                    #         exist_customer.related_user.add(user.pk)
                    #         exist_customer.save()
                    # user.mobile = mobile
                    # user.save()
                    # res = get_user_detail(user)
                    # return Response(res, status=HTTP_200_OK)
            return Response({'detail': '手机号格式有误'}, status=HTTP_400_BAD_REQUEST)
        return Response({'detail': '请登录'}, status=HTTP_401_UNAUTHORIZED)


class UpdateUserInfoView(AppApi):
    """
    post:
    更新姓名和银行卡信息，可更新字段为 'name', 'bank_account_name', 'bank_account_no', 'bank_name'
    """
    def post(self, request):
        fields = ['name', 'bank_account_name', 'bank_account_no', 'bank_name']
        if self.request.user.id:
            user = WxUser.objects.filter(pk=request.user.id).first()
            data = {}
            for f in fields:
                v = request.data.get(f)
                data[f] = v
            customers = Customer.objects.filter(related_user=user)
            if not customers.exists():
                if user.mobile:
                    customer = Customer.objects.create(name=user.nick_name, mobile=user.mobile, defaults=data)
                    customer.related_user.add(user.pk)
                    customer.save()
                else:
                    return Response({'detail': '请先提交手机号'}, status=HTTP_400_BAD_REQUEST)
            else:
                customers.update(**data)
                customer = customers.first()
            return Response(model_to_dict(customer, fields=fields), status=HTTP_200_OK)
        return Response({'detail': '请登录'}, status=HTTP_401_UNAUTHORIZED)


class GetCodeView(APIView):
    """
    get:
    获取验证码
    """
    def get(self, request):
        if self.request.user.id:
            # 校验参数
            mobile = request.query_params.get('mobile')
            if not mobile:
                return Response('手机号未提供', status=HTTP_400_BAD_REQUEST)
            res = re.match(r'^1[2-9]\d{9}$', mobile)
            if res:
                # 查看之前的发送记录
                pre_send = MsgSendRecord.objects.filter(mobile=mobile).order_by('-pk').first()
                if pre_send:
                    if (datetime.now() - pre_send.datetime_created).seconds < 300:
                        return Response('操作过于频繁，请在5分钟后重新申请', status=HTTP_400_BAD_REQUEST)
                # 保存短信验证码
                code = random.randint(1000, 9999)
                record = MsgSendRecord.objects.create(
                    mobile=mobile, code=code, paras=str({'code': code}), msg_type=1,
                    created_by_id=self.request.user.id
                )
                # 发送短信
                sms = sms_code(mobile=mobile, code=code)
                record.notes = sms.text
                record.save()
                if sms.status_code == 200:
                    return Response('发送成功', status=HTTP_200_OK)
                else:
                    return Response(sms.text, status=HTTP_400_BAD_REQUEST)
            else:
                return Response('手机号不符合规则', status=HTTP_400_BAD_REQUEST)
        else:
            return Response('请先登录', status=HTTP_401_UNAUTHORIZED)
