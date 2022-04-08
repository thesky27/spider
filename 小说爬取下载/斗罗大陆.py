import random
from datetime import datetime
import requests
from selenium import webdriver
from lxml import etree
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.chrome.service import Service
import time

url = "https://www.xbiquge.la/?hpprotid=2a8031d1"
title = []
url_content = []
# 设置请求头
headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"
}


my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]







"""
1.首先获取一本书的网页
2.进入主网页后在进行网页的解析，抓取title以及urL
3.访问ulr——content，以此来获取内容
4.将内容以及标题以txt的形式保存下来
"""
# 得到想要搜索的书的网页
def get_bookurl_html(url,bookname):
    # executable_path下添加的是chromedriver的位置，而不是chrome.exe的位置
    s = Service(r'D:\Google\Chrome\Application\chromedriver.exe')
    browser = webdriver.Chrome(service=s)
    browser.get(url)
    browser.find_element(By.ID, 'wd').send_keys(bookname)
    browser.find_element(By.ID, 'sss').click()
    response = browser.page_source
    tree = etree.HTML(response)
    url_booknamne = tree.xpath('//tbody/tr[2]/td[1]/a/@href')[0]
    html = get_html(url_booknamne,headers)
    return html,url_booknamne

def get_html(url,headers):

    response = requests.get(url=url,headers=headers)
    # 设置编码格式
    response.encoding = response.apparent_encoding
    # 使用etree来进行网页的转换
    html = etree.HTML(response.text)
    return html


def prase_url_title():
    book_name = input('请输入你想要下载的小说名字')
    html,url_bookname = get_bookurl_html(url,book_name)
    for dd in html.xpath('//div[@id = "list"]/dl/dd'):
        title.append(dd.xpath('.//text()')[0])
        # 获取网页的url
        url_pinjie = url_bookname + dd.xpath('./a/@href')[0].split('/')[-1]
        url_content.append(url_pinjie)
    return book_name


def get_headers():
    time.sleep(0.1)
    headers["user-agent"]=random.choice(my_headers)



def save_story():
    bookname = prase_url_title()
    for i in range(len(title)):
        print(f"{bookname}:\t", f"url:{url_content[i]},章节名:{title[i]}",)
        get_headers()
        html = get_html(url_content[i],headers)
        content = ''.join(html.xpath('//div[@id="content"]//text()'))

        if not os.path.exists(bookname):
            os.mkdir(bookname)
        with open(f'{bookname}/{title[i]}.txt','w',encoding='utf-8') as f:
            f.write(content)
            f.close()
starttime = datetime.now()
save_story()
endtime = datetime.now()
usedtime = (endtime-starttime).seconds
print("小说下载完成,共用",usedtime,"秒")
""""
以上代码遭遇了频繁被访问而被中断的情况
所以需要降低访问频率
1.更换请求头
2.添加代理IP
3.添加延迟
"""

"""
记录整个过程所查的资料
1.设置html的编码
2.selenium的使用，谷歌浏览器需要驱动chromedriver.exe
3.lxml中etree的是用，xpath的使用
4.文件需要关闭
5.禁止访问需要更换请求头或者代理IP等
"""


"""
继续改进
1.使用异步来加快爬取的速度
2.未使用爬虫的框架
3.未使用数据库存储数据
4.未使用
"""






