# -*- coding: utf-8 -*-
import datetime
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from ..items import JingDong

"""
https://blog.csdn.net/wenxuhonghe/article/details/84454485
"""


class JingdongSpider(scrapy.Spider):
    name = 'jingdong'
    allowed_domains = ['search.jd.com']
    max_page = 100
    # 这个页面是在京东搜索零食的页面
    start_urls = [
        'https://search.jd.com/Search?keyword=%E9%9B%B6%E9%A3%9F&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=lingshi&stock=1'
        '&click=0&page=1']

    def parse(self, response):

        content = response.body
        soup = BeautifulSoup(content, "html.parser")
        brand_temp_list = soup.find_all('li', attrs={'id': re.compile(r'brand-(\w+)')})
        brand_list = list()

        for item in brand_temp_list:
            brand_title = item.find('a')['title']
            brand_list.append(re.sub("[A-Za-z0-9\!\%\[\]\,\。\(\)\（\）\"\.\'\ ]", "", brand_title))
            # brand_list.append(brand_title)

        goods_temp_list = soup.find_all('li', attrs={'class': 'gl-item'})
        for item in goods_temp_list:
            goods = JingDong()

            # 零食 id
            goods_id = item['data-pid']

            # 零食 title
            goods_temp_title = item.find_all('div', attrs={'class': 'p-name'})
            goods_title = goods_temp_title[0].find('em').text

            # 零食 img
            goods_temp_img = item.find_all('div', attrs={'class': 'p-img'})
            goods_img = 'http:' + goods_temp_img[0].find('img')['source-data-lazy-img']
            # print(goods_temp_img)

            # 零食 url
            goods_temp_url = goods_temp_title[0].find('a')['href']
            goods_url = goods_temp_url if 'http' in goods_temp_url else 'https:' + goods_temp_url

            # if 'http' in goods_temp_url:
            #    goods_url = goods_temp_url
            # else:
            #    goods_url = 'http:' + goods_temp_url
            # print(goods_url)

            # 零食 price
            goods_price = item.find_all('div', attrs={'class': 'p-price'})[0].find('i').text
            # print(goods_price)

            # 零食 shop
            goods_temp_shop = item.find_all('div', attrs={'class': 'p-shop'})[0].find('a')
            goods_shop = '' if goods_temp_shop is None else goods_temp_shop.text
            # print(goods_shop)

            # 零食 优惠
            goods_temp_icon = item.find_all('div', attrs={'class': 'p-icons'})[0].find_all('i')
            goods_icon = ''
            for icon in goods_temp_icon:
                goods_icon += '/' + icon.text
            # print(goods_icon)

            # 零食 brand
            goods_brand = self.getGoodsBrand(goods_title, brand_list)
            # print(goods_brand)

            # 零食 time
            cur_time = datetime.datetime.now()
            cur_year = str(cur_time.year)
            cur_month = str(cur_time.month) if len(str(cur_time.month)) == 2 else '0' + str(cur_time.month)
            cur_day = str(cur_time.day) if len(str(cur_time.day)) == 2 else '0' + str(cur_time.day)
            goods_time = cur_year + '-' + cur_month + '-' + cur_day
            # print(goods_time)

            # 零食 描述
            goods_describe = ""

            goods['goods_id'] = goods_id
            goods['goods_title'] = goods_title
            goods['goods_url'] = goods_url
            goods['goods_img'] = goods_img
            goods['goods_price'] = goods_price
            goods['goods_shop'] = goods_shop
            goods['goods_icon'] = goods_icon
            goods['goods_time'] = goods_time
            goods['goods_brand'] = goods_brand
            goods['goods_describe'] = goods_describe

            yield goods

            cur_page_num = int(response.url.split('&page=')[1])
            next_page_num = cur_page_num + 1
            if cur_page_num < self.max_page:
                next_url = response.url[:-len(str(cur_page_num))] + str(next_page_num)
                yield Request(url=next_url, callback=self.parse, dont_filter=True)


    def getGoodsBrand(self, goods_title, brand_list):
        for brand in brand_list:
            if brand in goods_title:
                return brand
        return 'No-brand'
