# coding=utf-8
#!/usr/bin/env python

"""
news_crawler:新闻爬虫
~~~~~~~~~~~~~~~~~~~~~~~~·
获取 新浪滚动新闻 的链接
存储为csv文件
"""

import time
import sys
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
import os
import datetime
from pandas.core.frame import DataFrame
reload(sys)
sys.setdefaultencoding('utf-8')

s = requests.session()
s.keep_alive = False
requests.adapters.DEFAULT_RETRIES = 5

def get_URL(i):
    # init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2513&k=&num=50&page={}'#娱乐
    init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2511&k=&num=50&page={}'#国际
    # init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2512&k=&num=50&page={}'#体育
    # init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2514&k=&num=50&page={}'#军事
    # init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2515&k=&num=50&page={}'  # 科技
    # init_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=50&page={}'#财经
    page = requests.get(url=init_url.format(i), headers=headers).json()
    links = []
    for j in range(50):
        urls = page['result']['data'][j]['url']
        links.append(urls)
    return links

def get_title(init_url, weekago_date):
    pagenum = 50  # choose pagenum u want to scrapy
    i = 1
    record_i = 0
    titles = []
    while i < pagenum and record_i != i:
        record_i = i
        page = requests.get(url=init_url.format(i), headers=headers).json()
        for j in range(50):
            title = page['result']['data'][j]['title']
            url = page['result']['data'][j]['url']
            res = requests.get(url)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.select(".main-title")[0].text
            issue_date = soup.select(".date")[0].text
            issue_date = issue_date.split()[0].strip()
            issue_date = issue_date.encode('utf-8')
            issue_date = issue_date.replace('年', '-').replace('月', '-').replace('日', '')
            #issue_date转化为比较形式
            news_date = datetime.datetime.strptime(issue_date, '%Y-%m-%d')
            diff = news_date - weekago_date
            if diff.days < 0:
                print("一周内新闻标题获取完毕！")
                break
            else:
                titles.append(issue_date + ':' +title)
            #防止requests太快，休息一秒
            time.sleep(1)
        else:
            i += 1
            print("第" + str(i) + "页链接已经全部获取")
    return titles

def main():
    global headers
    headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/55.0.2883.87 Safari/537.36'}
    init_urls = ['https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2510&k=&num=50&page={}', 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2511&k=&num=50&page={}']
    init_urls_category = ['国内', '国际']

    # 获取当前时间
    today = datetime.datetime.now()
    # 计算偏移量(一天)
    offset = datetime.timedelta(days=-7)
    # 获取想要的日期的时间
    weekago_date = (today + offset).strftime('%Y-%m-%d')
    weekago_date = datetime.datetime.strptime(weekago_date, '%Y-%m-%d')

    root = ".//newsCollection//"
    #分不同的种类 每种一个文件
    for index, init_url in enumerate(init_urls):
        path = root + init_urls_category[index] + ".csv"
        titles = get_title(init_url, weekago_date)
        c = {'title': titles}
        data = DataFrame(c)
        try:
            if not os.path.exists(root):
                os.mkdir(root)
                print('mkdir success')
            data.to_csv(path)
        except IOError:
            print('sorry, write failed')
        else:
            print("---" + init_urls_category[index] + ".csv have created---")

if __name__ == "__main__":
    sys.setrecursionlimit(100000)  # 设置默认递归深度
    main()

    #获取单个新闻和新闻标题
    # url = 'https://news.sina.com.cn/w/2020-08-14/doc-iivhvpwy0958479.shtml'
    # res = requests.get(url)
    # #print(res.encoding)
    # res.encoding = 'utf-8'
    # soup = BeautifulSoup(res.text, 'html.parser')
    # title = soup.select(".main-title")[0].text
    # print(title)
    # article_content = ""
    # article = soup.select('.article p')[:-1]#末端的消息来源不需要
    # for p in article:
    #     article_content = article_content + p.text.strip()
    # print(article_content)