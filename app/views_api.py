import json
import logging

from django.forms import model_to_dict

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


@api_view(["GET"])
def api_root(request):
    urls = {'method': request.method, 'admin': '/admin/', 'api': '/api/'}
    return Response(urls)


class WxLoginView(APIView):
    """
    post:
    微信登录接口
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
                                        'company', 'restaurant', 'current_role',
                                        'is_owner', 'is_client', 'is_manager'
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

    authentication_classes = (JWTAuthentication, CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated, )
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


class ServicePackageTypeListView(ListAPIView):
    """
    get:
    获取套餐类别列表
    """
    pagination_class = None
    permission_classes = ()
    queryset = ServicePackageType.objects.order_by('name')
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
    提交保险服务申请
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
