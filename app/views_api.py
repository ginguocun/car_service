import json
import logging

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
                                        'full_name', 'mobile', 'gender', 'current_amounts', 'current_credits',
                                        'is_partner', 'is_client', 'is_manager'
                                    ])
                            },
                            status=HTTP_200_OK)
        return Response({'jwt': None, 'user': {}}, status=HTTP_204_NO_CONTENT)


class WxGzhLoginView(APIView):
    """
    post:
    公众号登录接口，传递参数 {'code': ''}
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
            api = WXAPPAPI(appid=settings.WX_GZH_APP_ID, app_secret=settings.WX_GZH_APP_SECRET)
            try:
                session_info = api.exchange_code_for_session_key(code=code)
            except OAuth2AuthExchangeError:
                session_info = None
            if session_info:
                openid_gzh = session_info.get('openid', None)
                if openid_gzh:
                    if user_info_raw:
                        for k, v in self.fields.items():
                            user_info[k] = user_info_raw.get(v)
                    user = create_or_update_user_info_gzh(openid_gzh, user_info)
                    if user:
                        token = AppTokenObtainPairSerializer.get_token(user).access_token
                        return Response(
                            {
                                'jwt': str(token),
                                'user': model_to_dict(
                                    user,
                                    fields=[
                                        'full_name', 'mobile', 'gender', 'current_amounts', 'current_credits',
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
        if not self.request.user.is_staff:
            return self.queryset.filter(created_by_id=self.request.user.id)
        return self.queryset


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
        if not self.request.user.is_staff:
            return self.queryset.filter(created_by_id=self.request.user.id)
        return self.queryset


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
        if not self.request.user.is_staff:
            return self.queryset.filter(created_by_id=self.request.user.id)
        return self.queryset


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


class UserInfoView(AppApi):
    """
    get:
    获取自己的用户信息
    """
    def get(self, request):
        res = {'user': dict(), 'amount_records': list(), 'credit_records': list()}
        if request.user.id:
            user = WxUser.objects.filter(pk=request.user.id).first()
            if user:
                res['user'] = model_to_dict(
                    user,
                    fields=[
                        'nick_name', 'full_name', 'mobile', 'gender',
                        'current_amounts', 'current_credits',
                        'is_partner', 'is_client', 'is_manager'
                    ])
                amount_records_q = AmountChangeRecord.objects.filter(
                    customer__related_user=user
                ).order_by('-pk').values('pk', 'customer__name', 'amounts', 'current_amounts', 'datetime_created')
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
                ).order_by('-pk').values('pk', 'customer__name', 'credits', 'current_credits', 'datetime_created')
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
            return Response(res, status=HTTP_200_OK)
        return Response(
            {'user': dict(), 'amount_records': list(), 'credit_records': list()}, status=HTTP_401_UNAUTHORIZED)
