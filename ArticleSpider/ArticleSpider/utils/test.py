# -*- coding: utf-8 -*-
# @Time    : 2019/4/27 11:55
# @Author  : Lwq
# @File    : test.py
# @Software: PyCharm
# login_data = {
#             'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
#             'grant_type': 'password',
#             'source': 'com.zhihu.web',
#             'username': '',
#             'password': '',
#             'lang': 'en',
#             'ref_source': 'homepage',
#             'utm_source': ''
#         }
#
# print('before',login_data)
# login_data.update({
#             'username': 123456,
#             'password': 123456
#         })
#
# print('after',login_data)
import StringIO
import gzip
import re

# with open('./cookies.txt', 'r') as f:
#     str = f.read()
# print(str)
# str = str.replace('\n','')
# print(str)
# aaa = re.match('.*?Set-Cookie3: (.*?)path.*?: (.*?)path.*?: (.*?)path.*?: (.*?)path.*?: (.*?) path.*',str,re.DOTALL)
# c1 = aaa.group(1)
# c2 = aaa.group(2)
# c3 = aaa.group(3)
# c4 = aaa.group(4)
# c5 = aaa.group(5)
# print(c1)
# print(c2)
# print(c3)
# print(c4)
# print(c5)
# str1 = c1+c2+c3+c4+c5
# print(str1)
# c=0
# for i in str1.split('; '):
#     print(i)
#     c+=1
#     print(c)
# cookies_dict = {i.split('=')[0]: i.split('=')[1] for i in str1.split('; ')}
# print(cookies_dict)
# print(c1+c2+c3+c4+c5)
# s1 = '_xsrf=G2XGyymNyWezxjPqJYn619XoDAw6VjJl'
# print(s1.split('=')[0])
# print(s1.split('=')[1])
import sys

sys.setdefaultencoding("utf-8")

def decodeGzip(data):

    stream = StringIO.StringIO(data)

    gziper = gzip.GzipFile(fileobj=stream)

    return gziper.read()

#此处填链接，百度可能会屏蔽链接所以把链接内容省略了
