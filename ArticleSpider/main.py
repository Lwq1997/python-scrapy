# -*- coding: utf-8 -*-
# @Time    : 2019/4/25 17:51
# @Author  : Lwq
# @File    : main.py
# @Software: PyCharm
import os
import sys

from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', 'jobbole'])
execute(['scrapy', 'crawl', 'lagou'])
# execute(['scrapy', 'crawl', 'jingdong'])

