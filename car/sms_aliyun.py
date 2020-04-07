import base64
import datetime
import hashlib
import hmac
import os
import requests
from requests.exceptions import ConnectionError
import time
from urllib import request
import uuid

from django.conf import settings
# https://blog.csdn.net/shu_8708/article/details/79150290


def log(text):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print('Pid:{0} running {1} [function:{2}] at {3}'.format(os.getpid(),
                                                                     text, func.__name__,
                                                                     datetime.datetime.now()))
            return func(*args, **kwargs)
        return wrapper
    return decorator


class MsgUrlBuild:
    def __init__(self, dic, secret_id=None):
        self.HttpMethod = 'GET'
        self._info = dic
        if secret_id is None:
            raise ValueError('SecretID must input!')
        self._secret_id = secret_id
        # print('api information write complete!')
        
    @staticmethod
    def en_code(x):
        x = request.quote(x, safe='')
        x = x.replace("+", "%20").replace("*", "%2A").replace("%7E", "~")
        return x
    
    @log('build sorted dictionary')
    def _build_query(self):
        if self._info is None:
            raise ValueError('please init first')
        lst = sorted(self._info)
        temp_ls = []
        for k in lst:
            v = self._info[k]
            para = '{0}={1}'.format(self.en_code(k), self.en_code(v))
            temp_ls.append(para)
        return '&'.join(temp_ls)
    
    @log('build string to sign')
    def _sign_to_sign(self, x):
        return self.HttpMethod+'&'+self.en_code('/')+'&'+self.en_code(x)

    @log('create a sign')
    def _create_sign(self, x):
        sha1 = hmac.new((self._secret_id+'&').encode('utf-8'), x.encode('utf-8'), hashlib.sha1).digest()
        sign = base64.b64encode(sha1)
        return self.en_code(sign)
    
    @log('reset the information of api')
    def reset_info(self, dic):
        self._info = dic
    
    @log('start build request')
    def url_build(self):
        base_str = self._build_query()
        tmp = self._sign_to_sign(base_str)
        x = self._create_sign(tmp)
        return 'http://dysmsapi.aliyuncs.com/?Signature={0}&{1}'.format(x, base_str)


def sms_aliyun_url(mobile='17159866179', template_code='SMS_186953342', para='{"code":"2019"}'):
    form = dict()
    form["SignatureMethod"] = "HMAC-SHA1"
    form["SignatureNonce"] = str(uuid.uuid1())
    form["AccessKeyId"] = settings.ACCESS_KEY_ID
    form["SignatureVersion"] = "1.0"
    form['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    form['Action'] = "SendSms"
    form['Version'] = "2017-05-25"
    form['RegionId'] = "cn-hangzhou"
    form['SignName'] = "24h车服务"  # 签名
    form['TemplateParam'] = para  # 模板替换部分
    form['PhoneNumbers'] = mobile  # 接受信息的号码
    form['TemplateCode'] = template_code  # 模板号
    xx = MsgUrlBuild(form, settings.ACCESS_KEY_SECRET)
    msm_url = xx.url_build()
    try:
        response = requests.get(msm_url)
    except ConnectionError:
        # TODO return msm send failed message
        return None
    return response


def sms_code(mobile, code):
    paras = dict()
    paras['code'] = code
    paras = str(paras)
    msg = sms_aliyun_url(mobile=mobile, para=paras)
    return msg


def test():
    paras = dict()
    paras['code'] = '2020'
    m = '15068826001'
    paras = str(paras)
    msg = sms_aliyun_url(mobile=m, para=paras)
    print(msg)


if __name__ == '__main__':
    test()
