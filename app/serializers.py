from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *


class AppTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(AppTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = 'wx_{0}'.format(user.username)
        return token


class WxUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = WxUser
        fields = ['id', 'nick_name', 'avatar_url', 'gender']


class ServicePackageTypeSerializer(serializers.ModelSerializer):
    service_packages = serializers.ListField(read_only=True)

    class Meta:
        model = ServicePackageType
        fields = '__all__'


class ServicePackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServicePackage
        depth = 2
        fields = '__all__'


class OilPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = OilPackage
        fields = '__all__'


class StoreInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreInfo
        fields = '__all__'


class InsuranceCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = InsuranceCompany
        fields = '__all__'


class ServiceApplySerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceApply
        fields = '__all__'


class InsuranceApplySerializer(serializers.ModelSerializer):

    class Meta:
        model = InsuranceApply
        fields = '__all__'


class PartnerApplySerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerApply
        fields = '__all__'
