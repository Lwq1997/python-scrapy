# -*- coding: utf-8 -*-
# @Time    : 2019/4/27 11:37
# @Author  : Lwq
# @File    : zhihu_login_requests.py
# @Software: PyCharm
import base64
import csv
import hashlib
import hmac
import json
import re
import threading
import time
from http import cookiejar
from urllib.parse import urlencode

import execjs
import pandas as pd
import requests
from PIL import Image


class ZhiHuAccount(object):
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password

        self.login_data = {
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'source': 'com.zhihu.web',
            'username': '',
            'password': '',
            'lang': 'en',
            'ref_source': 'homepage',
            'utm_source': ''
        }

        self.session = requests.session()
        self.session.headers = {
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }

        self.session.cookies = cookiejar.LWPCookieJar(filename='./cookies.txt')

    def login(self, captcha_lang: str = 'en', load_cookies: bool = True):
        """
           模拟登录知乎
           :param captcha_lang: 验证码类型 'en' or 'cn'
           :param load_cookies: 是否读取上次保存的 Cookies
           :return: bool
           若在 PyCharm 下使用中文验证出现无法点击的问题，
           需要在 Settings / Tools / Python Scientific / Show Plots in Toolwindow，取消勾选
        """
        if load_cookies and self.load_cookies():
            print('读取cookies文件')
            if self.check_login():
                print('登陆成功')
                return True
            print('Cookies已经过期')

        self.check_user_pass()
        self.login_data.update({
            'username': self.username,
            'password': self.password,
            'lang': captcha_lang
        })

        timestamp = int(time.time() * 1000)
        print('timestamp', timestamp)
        self.login_data.update({
            'captcha': self.get_captcha(self.login_data['lang']),
            'timestamp': timestamp,
            'signature': self.get_signature(timestamp)
        })
        headers = self.session.headers.copy()
        headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_1.1',
            'x-xsrftoken': self.get_xsrf()
        })
        data = self.encrypt(self.login_data)
        login_api = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        resp = self.session.post(login_api, data=data, headers=headers)
        if 'error' in resp.text:
            print(json.loads(resp.text)['error'])
        if self.check_login():
            response = self.session.get("https://www.zhihu.com", headers=headers)
            with open("index_page.html", "wb") as f:
                f.write(response.text.encode("utf-8"))
            print('登录成功')
            return True
        print('登录失败')
        return False

    def load_cookies(self):
        """
            读取 Cookies 文件加载到 Session
            :return: bool
        """
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        login_url = 'https://www.zhihu.com/signup'
        resp = self.session.get(login_url, allow_redirects=False)
        if resp.status_code == 302:
            self.session.cookies.save()
            return True
        return False

    def get_xsrf(self):
        """
        从登录页面获取 xsrf
        :return: str
        """
        self.session.get('https://www.zhihu.com/', allow_redirects=False)
        for c in self.session.cookies:
            if c.name == '_xsrf':
                return c.value
        raise AssertionError('获取 xsrf 失败')

    def get_captcha(self, lang: str):
        """
            请求验证码的 API 接口，无论是否需要验证码都需要请求一次
            如果需要验证码会返回图片的 base64 编码
            根据 lang 参数匹配验证码，需要人工输入
            :param lang: 返回验证码的语言(en/cn)
            :return: 验证码的 POST 参数
        """
        if lang == 'cn':
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        else:
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        resp = self.session.get(api)
        show_captcha = re.search(r'true', resp.text)

        if show_captcha:
            # 需要验证码
            put_resp = self.session.put(api)
            json_data = json.loads(put_resp.text)
            img_base64 = json_data['img_base64'].replace(r'\n', '')
            with open('./captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(img_base64))
            img = Image.open('./captcha.jpg')
            if lang == 'cn':
                # 倒立的汉字验证码
                import matplotlib.pyplot as plt
                plt.imshow(img)
                print('点击所有倒立的汉字，在命令行中按回车提交')
                points = plt.ginput(7)
                capt = json.dumps({'img_size': [200, 44],
                                   'input_points': [[i[0] / 2, i[1] / 2] for i in points]})
            else:
                # 输入英文字母验证码
                img_thread = threading.Thread(target=img.show, daemon=True)
                img_thread.start()
                capt = input('请输入图片里的验证码：')
            # 这里必须先把参数 POST 验证码接口
            self.session.post(api, data={'input_text': capt})
            return capt
        return ''

    def get_signature(self, timestamp: int or str):
        """
        通过 Hmac 算法计算返回签名
        实际是几个固定字符串加时间戳
        :param timestamp: 时间戳
        :return: 签名
        """
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_data['grant_type']
        client_id = self.login_data['client_id']
        source = self.login_data['source']
        ha.update(bytes((grant_type + client_id + source + str(timestamp)), 'utf-8'))
        return ha.hexdigest()

    def check_user_pass(self):
        """
            检查用户名和密码是否已输入，若无则手动输入
        """
        if not self.username:
            self.username = input('请输入手机号：')
        if self.username.isdigit() and '+86' not in self.username:
            self.username = '+86' + self.username

        if not self.password:
            self.password = input('请输入密码：')

    @staticmethod
    def encrypt(form_data: dict):
        with open('./encrypt.js') as f:
            js = execjs.compile(f.read())
            return js.call('Q', urlencode(form_data))

    def get_data(self, url):
        """
           功能：访问 url 的网页，获取网页内容并返回
           参数：
               url ：目标网页的 url
           返回：目标网页的 html 内容
        """
        try:
            r = self.session.get(url, headers=self.session.headers)
            r.raise_for_status()
            return r.text
        except requests.HTTPError as e:
            print(e)
            print("HTTPError")
        except requests.RequestException as e:
            print(e)
        except:
            print("Unknown Error !")

    def parse_data(self, html):
        """
        功能：提取 html 页面信息中的关键信息，并整合一个数组并返回
        参数：html 根据 url 获取到的网页内容
        返回：存储有 html 中提取出的关键信息的数组
        """
        json_data = json.loads(html)['data']
        comments = []

        try:
            for item in json_data:
                comment = []
                comment.append(item['author']['name'])  # 姓名
                comment.append(item['author']['gender'])  # 性别
                # comment.append(item['author']['url'])     # 个人主页
                comment.append(item['voteup_count'])  # 点赞数
                comment.append(item['comment_count'])  # 评论数
                # comment.append(item['url'])               # 回答链接
                comments.append(comment)

            return comments

        except Exception as e:
            print(comment)
            print(e)

    def save_data(self, comments):
        '''
        功能：将comments中的信息输出到文件中/或数据库中。
        参数：comments 将要保存的数据
        '''
        filename = './comments.csv'

        dataframe = pd.DataFrame(comments)
        dataframe.to_csv(filename, mode='a', index=False, sep=',', header=False)

    def to_start(self):

        url = 'https://www.zhihu.com/api/v4/questions/275359100/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=5&platform=desktop&sort_by=default'

        # get total cmts number
        html = self.get_data(url)
        # totals = json.loads(html)['paging']['totals']
        totals = 100

        print(totals)
        print('---' * 10)

        page = 0

        while (page < totals):
            url = 'https://www.zhihu.com/api/v4/questions/275359100/answers?include=data%5B%2A%5D.is_normal' \
                  '%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail' \
                  '%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment' \
                  '%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission' \
                  '%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship' \
                  '.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D' \
                  '.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5' \
                  '&offset=' + str(
                page) + '&platform=desktop&sort_by=default'

            html = self.get_data(url)
            comments = self.parse_data(html)
            self.save_data(comments)

            print(page)
            page += 5


if __name__ == '__main__':
    account = ZhiHuAccount('', '')
    # account.login(captcha_lang='en', load_cookies=True)
    account.to_start()
