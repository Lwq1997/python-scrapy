# -*- coding: utf-8 -*-
# @Time    : 2019/4/25 22:06
# @Author  : Lwq
# @File    : common.py
# @Software: PyCharm
import hashlib
def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == '__main__':
    print(get_md5('https://www.baidu.com'))