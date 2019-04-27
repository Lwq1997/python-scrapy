# -*- coding: utf-8 -*-
# @Time    : 2019/4/27 11:55
# @Author  : Lwq
# @File    : test.py
# @Software: PyCharm
login_data = {
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'source': 'com.zhihu.web',
            'username': '',
            'password': '',
            'lang': 'en',
            'ref_source': 'homepage',
            'utm_source': ''
        }

print('before',login_data)
login_data.update({
            'username': 123456,
            'password': 123456
        })

print('after',login_data)