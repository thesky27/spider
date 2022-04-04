## scrapy框架

### 一、框架的基本使用

#### 1.介绍

- Scrapy是一个开源协作的框架，其目的是为了页面抓取，使用它可以快速、简单、可扩展的从网站中提取所需要的数据
- 用途十分广泛，可用于数据挖掘、监测和自动化测试等领域，使用的时候十分方便，并通过异步来实现并发

#### 2.组成部分

1. Scrapy Engine——引擎
   - 负责控制系统所有组件之间的数据流，并在某些动作发生时触发事件
2. Scheduler——调度器
   - 用来接收引擎发过来的请求，压入队列中，并在引擎再次请求时返回，可以理解为一个URL的优先级队列，由他来决定下一个要抓取的网址是什么，同时去除重复的网址
3. Downloader——下载器
   - 用于下载网页的内容，并将网页内容返回给engine
4. Spiders——爬虫
   - 是开发人员自定义的类，负责处理所有的responses，从中提取数据，获取Item字段需要的数据，并将需要跟进的URL提交给引擎，再次进入Scheduler（调度器）
5. Item Pipline——项目管道
   - 在items被提取后负责处理他们，主要包括清理、验证、持久化等操作
6. 下载中间件（Downloader Middlewares）
   - 自定义扩展下载的功能
7. 爬虫中间件（Spider Middlewares）
   - 主要是处理Spider的输入和输出

#### 3.运行流程

```
引擎：Hi,Spider，你要处理哪一个网站？
Spider：老大，我要处理xxx.com
引擎：你把第一个需要处理的URL给我吧
Spider：老大，第一个URL是xxx.com
引擎：Hi,调度器，我这有request请求你帮我排序入队一下
调度器：好的正在处理，你等一下
引擎：Hi,调度器，把你处理好的request请求给我
调度器：给你，这是我处理好的request
引擎：Hi,下载器，你按照下载中间件的设置帮我下载一下这个request请求
下载器：好的，给你（如果失败，sorry，这个request下载失败了，然后引擎告诉调度器，这个request下载失败了，你记录一下，我们待会下载）
引擎：Hi spider,这是下载好的东西，并且已经按照老大的下载中间件处理过了，（注意！这儿responses是默认交给def parse（）这个函数处理）
Spider：（处理完毕数据之后对于需要跟进的URL）HI，引擎，我这里有两个结果，这个是我需要跟进的URL，这个是我获取的Item数据
引擎：HI，管道，我这儿有个Item你帮我处理一下！调度器！这是需要跟进的Url，你帮我处理一下，然后从第四部开始循环，知道获取老大需要的全部信息。
管道，调度器：好的，现在就做！
```

注意：只有调度器中没有url时，程序才会停止

### 二、安装

```python
#主要是用Windows
1.pip install pywin32
2.pip install twisted
3.pip install scrapy
#Linux
1.apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
2.pip install scrapy
```

在自己的环境下输入scrapy，看看是否出现版本名，有则就安装成功

### 三、简单的使用

##### **1.学习目标**

- 创建一个scrapy项目
- 定义要提取的结构化数据（Item）
- 编写爬取网站的spider并提取结构化的数据（Item）
- 编写Item Pipline来存储提取到的结构化数据

##### 2.**新建项目**

- 开始爬去之前，必须创建一个新的Scrapy项目，进入自定义的项目目录中，并实行以下命令

```shell
scrapy startproject 爬虫名字
```

##### **3.文件介绍**

```
scrapy.cfg:项目的配置文件
easecloud/:项目的python模块，
easecloud/items.py:项目的目标文件
easecloud/pipelines.py:项目的管道文件
easecloud/settings.py:项目的配置文件
easecloud/easecloud/：项目涉及的代码
```

##### 4.**明确目标**

打算抓取豆瓣top250里面所有的标题和简介

1. 打开myspider结构下的item.py文件
2. Item定义结构化数据字段，用来保存爬取到的数据，有点像dic
3. 可以通过创建一个scrapy.item类，并且定义类型为scrapy。Field的类属性来定义一个Item
4. 创建一个DoubanItem类和构建Item模型

```python
class DoubanItem(scrapy.Item):
    title = scrapy.Field()
    indroduce = scrapy.Field()
    pass
```

##### 5.**制作爬虫**

###### 5.1爬数据

：在easecloud下面加上,会生成一个douban.py的文件

```
spider genspider douban douban.com
```

出现了

```python
import scrapy


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['http://douban.com/']

    def parse(self, response):
        pass
```

1. name = 'douban'：爬虫的命名识别，是唯一的
1. allowed_domains = ['douban.com']：是搜索的域名范围，也是爬虫的约束区域，规定只爬取这个页面之下的东西
1. start_urls = ['http://douban.com/']：爬虫会从这些url中进行
4. def parse(self, response):解析的方法，每个url完成下载后将被调用，将传回的Response作为唯一参数，主要作用如下：
   - 负责解析网页传回的数据，response.body,提取结构化的数据（生成Item）
   - 生成下一页的URL的请求

爬取之前做的小修改，在settings文件里面需要全部大写，否则不会生效

```python
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
LOG_LEVEL = 'WARNING'
# Obey robots.txt rules
ROBOTSTXT_OBEY = True


#自定义parse函数
    def parse(self, response):
        with open('movie.html','w',encoding='utf-8')as f:
            f.write(response.text)
```

运行命令：scrapy crwal 爬虫名

###### 5.2获取数据

douban.py文件的修改

```python
import scrapy
from ..items import DoubanItem

class DoubanSpider(scrapy.Spider):
    name = 'douban' #爬虫名字
    # allowed_domains = ['https://www.douban.com/'] # 允许爬取的范围
    start_urls = ['https://movie.douban.com/top250'] #第一个访问的URL

    def parse(self, response):
        info = response.xpath('//div[@class="info"]')
        for div in info:
            title = div.xpath("./div[1]/a/span[1]/text()").extract_first()
            introduce = div.xpath("./div[2]/p[1]/text()").extract()
            print(title,introduce)
            break

"""
肖申克的救赎 ['\n                            导演: 弗兰克·德拉邦特 Frank Darabont\xa0\xa0\xa0主演: 蒂姆·罗宾斯 Ti
m Robbins /...', '\n                            1994\xa0/\xa0美国\xa0/\xa0犯罪 剧情\n                        ']

"""            
```

**用xpath得到的是一个selector对象，要想提取出其中的值，就要用到extract（）方法，将数据会保存到列表里去的**

###### 5.3取数据

```python
import scrapy
from ..items import DoubanItem

class DoubanSpider(scrapy.Spider):
    name = 'douban' #爬虫名字
    # allowed_domains = ['https://www.douban.com/'] # 允许爬取的范围
    start_urls = ['https://movie.douban.com/top250'] #第一个访问的URL

    def parse(self, response):
        items = []
        item = {}
        info = response.xpath('//div[@class="info"]')
        for div in info:
            title = div.xpath("./div[1]/a/span[1]/text()").extract_first()
            introduce = div.xpath("./div[2]/p[1]/text()").extract()
            introduce = ''.join(j.strip() for j in [i.replace("\\xa0",'') for i in introduce])
            item['title'] = title
            item['introduce'] = introduce[0]
            items.append(item)
            break
        return items
```

###### 5.4保存数据

scrapy保存数据的简单方式主要有四种，-o 是输出格式，itcast是你的爬虫名

```python
# json格式，默认为Unicode编码
scrapy crawl itcast -o movie.json
# json lines格式，默认为Unicode编码
scrapy crawl itcast -o movie.jsonl
# csv逗号表达式，可用excel打开
scrapy crawl itcast -o movie.csv
# xml格式
scrapy crawl itcast -o movie.xml
```

### 四、总结

**本次爬虫只是最基础的，没有用到pipeline以及调度器来处理数据，读者可先进行了解，后续会进行相关笔记的编写**
