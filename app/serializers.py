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
