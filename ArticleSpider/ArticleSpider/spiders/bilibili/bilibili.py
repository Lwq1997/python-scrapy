# -*- coding: utf-8 -*-
# @Time    : 2019/4/28 18:29
# @Author  : Lwq
# @File    : bilibili.py
# @Software: PyCharm
import json
import time

import requests


def fetchURL(url):
    """
    爬取哔哩哔哩全职高手动画下的评论
    :param url: 目标网页url
    :return: 目标网页的html页面
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/68.0.3440.106 Safari/537.36',
    }

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.text
    except requests.HTTPError as e:
        print(e)
        print("HTTPError")
    except requests.RequestException as e:
        print(e)
    except:
        print("Unknown Error !")


def parserHtml(html):
    """
    根据爬取到的页面解析json
    :param html: 爬取到的页面,每一页有20个评论
    :return:
    """
    print('开始爬取')
    try:
        s = json.loads(html)
    except:
        print('error')

    commentlist = []
    hlist = []

    hlist.append("序号|")
    hlist.append("名字|")
    hlist.append("性别|")
    hlist.append("时间|")
    hlist.append("评论|")
    hlist.append("点赞数|")
    hlist.append("回复数")

    # commentlist.append(hlist)

    # 楼层，用户名，性别，时间，评价，点赞数，回复数
    for i in range(20):
        comment = s['data']['replies'][i]
        blist = []

        floor = comment['floor']
        username = comment['member']['uname']
        sex = comment['member']['sex']
        ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['ctime']))
        content = comment['content']['message']
        likes = comment['like']
        rcounts = comment['rcount']

        blist.append(str(floor) + '|')
        blist.append(str(username) + '|')
        blist.append(str(sex) + '|')
        blist.append(str(ctime) + '|')
        blist.append(str(content) + '|')
        blist.append(str(likes) + '|')
        blist.append(str(rcounts))

        commentlist.append(blist)

    writePage(commentlist)



def writePage(urating):
    '''
        Function : To write the content of html into a local file
        html : The response content
        filename : the local filename to be used stored the response
    '''
    print('开始写入文件')
    import pandas as pd
    dataframe = pd.DataFrame(urating)
    dataframe.to_csv('comments.csv', mode='a', index=False, sep=',', header=False)
    print('---' * 20)


if __name__ == '__main__':
    """
    这个url访问不到
    url = 'https://api.bilibili.com/x/v2/reply?callback=jQuery17208718507384171712_1556446515527&jsonp=jsonp&pn=5' \
           '&type=1&oid=11357166&sort=0&_=1556446746430 '
    改用下面这个。pn（页数），type（=1）和oid（视频id）
    """
    for page in range(1, 11):
        # 爬取10页存到csv文件中
        url = 'https://api.bilibili.com/x/v2/reply?type=1&oid=11357166&pn=' + str(page)
        print('爬取的url是:', url)
        html = fetchURL(url)
        parserHtml(html)
        # 为了降低被封ip的风险，每爬20页便歇5秒。
        if page % 20 == 0:
            time.sleep(20)
    # print(html)
