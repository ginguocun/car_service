import base64
import binascii
import datetime
import hashlib
import rsa
import xlwt

from django.conf import settings
from django.http import FileResponse

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def file_iterator(filename, chuck_size=512):
    with open(filename, "rb") as f:
        while True:
            c = f.read(chuck_size)
            if c:
                yield c
            else:
                break


def export_excel(queryset, headers, columns, filename='jf'):
    wb = xlwt.Workbook()
    sheet = wb.add_sheet("data")
    for i, h in enumerate(headers):
        sheet.write(0, i, h)
    cols = 1
    for query in queryset.values(*columns):
        for i, k in enumerate(columns):
            v = query.get(k)
            if isinstance(v, datetime.datetime):
                v = v.strftime('%Y-%m-%d %H:%M:%S')
            sheet.write(cols, i, v)
        cols += 1
    wb.save(filename)
    response = FileResponse(file_iterator(filename))
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


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


def str_value(string, upper=False):
    """
    去除文本的空格
    :param string: 文本数据
    :param upper: 是否要大写
    :return: 返回格式化后的数据
    """
    if upper is True:
        res = str(string).replace(' ', '').upper()
    else:
        res = str(string).replace(' ', '')
    if res:
        return res
    else:
        return None


def num_value(num, decimal_places=4):
    """
    数字数据的处理
    :param num: 数字数据
    :param decimal_places: 小数点的位数
    :return: 返回处理后的数据
    """
    try:
        res = round(float(num), decimal_places)
    except (ValueError, TypeError):
        res = None
    return res


def date_value(ori_date):
    """
    日期数据的处理
    :param ori_date: 原始日期数据
    :return: 返回处理后的数据
    """
    from datetime import datetime
    try:
        res = datetime.strptime(ori_date, '%Y.%m.%d').strftime('%Y-%m-%d')
    except ValueError:
        res = None
    return res
