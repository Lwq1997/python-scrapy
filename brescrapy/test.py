# -*- coding: utf-8 -*-
# @Time    : 2019/4/24 21:18
# @Author  : Lwq
# @File    : test.py
# @Software: PyCharm
import re

str = 'xxx出生于2016-06-01'
# str = 'xxx出生于2016年6月1号'
# str = 'xxx出生于2016/6/1'
# str = 'xxx出生于2016/06/01'
# str = 'xxx出生于2016年6月'
# str = 'xxx出生于2016/06'
regstr = r".*出生于(\d{4}[年/-]\d{1,2}([月/-]\d{1,2}([号]|$)|[月]|$))"
matchstr = re.match(regstr,str)
if matchstr:
    print(matchstr.group(1))