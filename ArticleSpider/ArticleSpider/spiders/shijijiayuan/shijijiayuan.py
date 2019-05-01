# -*- coding: utf-8 -*-
# @Time    : 2019/5/1 20:36
# @Author  : Lwq
# @File    : shijijiayuan.py
# @Software: PyCharm
import json
import re

import pandas as pd

import requests


def fetchURL(url):
    """
    功能：访问URL网页，获取网页内容并返回
    :param url:
    :return:
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        # 'Cookie': 'guider_quick_search=on; SESSION_HASH=f09e081981a0b33c26d705c2f3f82e8f495a7b56; PHPSESSID=e29e59d3eacad9c6d809b9536181b5b4; is_searchv2=1; save_jy_login_name=18511431317; _gscu_1380850711=416803627ubhq917; stadate1=183524746; myloc=11%7C1101; myage=23; mysex=m; myuid=183524746; myincome=30; COMMON_HASH=4eb61151a289c408a92ea8f4c6fabea6; sl_jumper=%26cou%3D17%26omsg%3D0%26dia%3D0%26lst%3D2018-11-07; last_login_time=1541680402; upt=4mGnV9e6yqDoj%2AYFb0HCpSHd%2AYI3QGoganAnz59E44s4XkzQZ%2AWDMsf5rroYqRjaqWTemZZim0CfY82DFak-; user_attr=000000; main_search:184524746=%7C%7C%7C00; user_access=1; PROFILE=184524746%3ASmartHe%3Am%3Aimages1.jyimg.com%2Fw4%2Fglobal%2Fi%3A0%3A%3A1%3Azwzp_m.jpg%3A1%3A1%3A50%3A10; pop_avatar=1; RAW_HASH=n%2AazUTWUS0GYo8ZctR5CKRgVKDnhyNymEBbT2OXyl07tRdZ9PAsEOtWx3s8I5YIF5MWb0z30oe-qBeUo6svsjhlzdf-n8coBNKnSzhxLugttBIs.; pop_time=1541680493356'
    }

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = 'unicode_escape'
        print('爬取的url：', url)
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
    根据url爬取到的html页面，解析获取参数
    :param html:
    :return:
    """
    s = json.loads(html)
    userInfo = []

    for key in s['userInfo']:
        blist = []

        uid = key['uid']
        nickname = key['nickname']
        sex = key['sex']
        age = key['age']
        work_location = key['work_location']
        height = key['height']
        education = key['education']

        matchCondition = key['matchCondition']
        marriage = key['marriage']
        income = key['income']
        shortnote = key['shortnote']
        image = key['image']

        blist.append(uid)
        blist.append(nickname)
        blist.append(sex)
        blist.append(age)
        blist.append(work_location)
        blist.append(height)
        blist.append(education)
        blist.append(matchCondition)
        blist.append(marriage)
        blist.append(income)
        blist.append(shortnote)
        blist.append(image)

        userInfo.append(blist)

        print('昵称：%s--年龄：%s--工作地点：%s' % (nickname, age, work_location))
    print('***' * 20)
    return userInfo


def writePage(urating):
    '''
        Function : To write the content of html into a local file
        html : The response content
        filename : the local filename to be used stored the response
    '''
    dataframe = pd.DataFrame(urating)
    dataframe.to_csv('Jiayuan_UserInfo.csv', mode='a', index=False, sep=',', header=False)


def down_img():
    userData = pd.read_csv("Jiayuan_UserInfo.csv",
                           names=['uid', 'nickname', 'sex', 'age', 'work_location', 'height', 'education',
                                  'matchCondition', 'marriage', 'income', 'shortnote', 'image'])
    for line in range(len(userData)):
        url = userData['image'][line]
        img = requests.get(url).content
        nickname = re.sub("[\s+\.\!\/_,$%^*(+\"\'?|]+|[+——！，。？、~@#￥%……&*（）▌]+", "", userData['nickname'][line])

        filename = str(line) + '-' + nickname + '-' + str(userData['height'][line]) + '-' + str(
            userData['age'][line]) + '.jpg'
        try:
            with open('./images_output/' + filename, 'wb') as f:
                f.write(img)
        except:
            print(filename)

    print('finish')


if __name__ == '__main__':
    # for i in range(1, 11):
    #     print('第%s页' % i)
    #     url = 'http://search.jiayuan.com/v2/search_v2.php?key=&sex=f&stc=2:18.24,3:155.170,' \
    #           '23:1&sn=default&sv=1&p=%s&f=select ' % i
    #     html = fetchURL(url)
    #     print('爬取到的页面:', html)
    #     userInfo = parserHtml(html)
    #     writePage(userInfo)
    down_img()
