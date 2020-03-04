import base64
import binascii
import hashlib
import rsa

from django.conf import settings

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NormalResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

    def get_paginated_response(self, data):
        if not self.page.has_next():
            next_page = None
        else:
            next_page = self.page.next_page_number()
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'next_page': next_page,
            'length': len(data),
            'count': self.page.paginator.count,
            'page': self.page.number,
            'num_pages': self.page.paginator.num_pages,
            'page_size': self.page.paginator.per_page,
            'results': data
        })


def generate_keys():
    """
    生成公钥和私钥
    :return:
    """
    public_key, private_key = rsa.newkeys(1024)
    pub = public_key.save_pkcs1()
    public_file = open('public.pem', 'wb')
    public_file.write(pub)
    public_file.close()
    pri = private_key.save_pkcs1()
    private_file = open('private.pem', 'wb')
    private_file.write(pri)
    private_file.close()


def rsa_encrypt(d_str):
    """
    对文本进行加密
    :param d_str: 文本
    :return: 加密后的数据
    """
    p = settings.PUBKEY.encode()
    public_key = rsa.PublicKey.load_pkcs1(p)
    # 将字符串进行编码
    content = d_str.encode('utf-8')
    # 公钥加密
    crypto = rsa.encrypt(content, public_key)
    return base64.b64encode(crypto).decode()


def rsa_decrypt(crypto):
    """
    对文本进行解密
    :param crypto: 密文
    :return: 解密后的数据
    """
    p = settings.PRIVKEY.encode()
    private_key = rsa.PrivateKey.load_pkcs1(p)
    # 解密
    content = rsa.decrypt(base64.b64decode(crypto), private_key)
    # 解码
    content = content.decode('utf-8')
    return content


def pbkdf2_hmac_encrypt(d_str):
    """
    单向加密数据
    :param d_str: 文本
    :return: 加密后的数据
    """
    dk = hashlib.pbkdf2_hmac('sha256', d_str.encode(), settings.SECRET_KEY.encode(), 100)
    crypto = binascii.hexlify(dk).decode()
    return crypto


