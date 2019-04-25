# -*- coding: utf-8 -*-
import re
from urllib import parse

import scrapy
from scrapy.http import Request


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
            1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
            2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章的具体信息
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·',
                                                                                                                    '').strip()
        praise_nums = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_re = re.match('.*?(\d+).*', fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        match_re = re.match('.*?(\d+).*', comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.xpath('//div[@class="entry"]').extract_first(default='')

        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # print([element for element in ['IT技术', ' 2 评论 ', 'Vim'] if not element.strip().endswith('评论')])
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tag = ','.join(tag_list)

        # css选择器
        css_title = response.css('.entry-header h1::text').extract()[0]
        css_create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].strip().replace('·',
                                                                                                         '').strip()
        css_praise_nums = response.css('.vote-post-up h10::text').extract()[0]
        css_fav_nums = response.css(".bookmark-btn::text").extract()[0]
        match_re = re.match('.*?(\d+).*', css_fav_nums)
        if match_re:
            css_fav_nums = int(match_re.group(1))
        else:
            css_fav_nums = 0

        css_comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match('.*?(\d+).*', css_comment_nums)
        if match_re:
            css_comment_nums = int(match_re.group(1))
        else:
            css_comment_nums = 0

        css_content = response.css('div.entry').extract()

        css_tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # print([element for element in ['IT技术', ' 2 评论 ', 'Vim'] if not element.strip().endswith('评论')])
        css_tag_list = [element for element in css_tag_list if not element.strip().endswith('评论')]
        css_tag = ','.join(css_tag_list)
