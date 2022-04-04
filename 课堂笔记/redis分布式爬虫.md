# scrapy-redis分布式爬虫

## 一、介绍

所谓分布式就是多台机器对一个项目进行联合爬取

**可以增加工作单位，提升爬取效率**

## 二、思考

**以下就是scrapy框架的流程**

![image-20220326143104266](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20220326143104266.png)

如果是三台电脑去爬取十万条数据，那这是分布式吗？不是，因为数据有重复而且时间没有减少。

**条件**

1. 每一台机器都可以进行连接
2. 能够对需要爬取的URL进行数据的存储
3. 要存储URL数据

## 三、存储

### 3.1数据库的选择

这就涉及到了URL数据，需要哪一个数据库进行存储呢？

redis：是持久化存储，非关系型数据库，有字符串，列表，集合，有序集合，哈希等

mongodb：类似于json的文档

其中列表满足调度器的队列，集合满足调度器的去重

### 3.2redis的使用

可以将url由爬虫交给引擎，引擎交给redis，也可以把URL由调度器交给redis，同样的在持久化存储的过程中，也由管道把item数据交给redis存储。

### 3.3redis的基本操作

```python
redis-server  #启动服务
redis-cli  	  #启动客户端
LPUSH key values	# 添加数据
llen name 		#查看数据的个数
keys *			#查看所有的数据
type keys		#查看数据类型
flushall		#清空数据
```

## 四、实战

### 4.1创建爬虫

这里以淘车为例

```python
scrapy startproject myspider
scrapy genspider -t crawl taoche taoche.com
```

这里使用公共调度器，需要去下载scrapy-redis库

### 4.2定义爬取的字段

```python
import scrapy


class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass

```

这里需要把item管道换成redis管道

```python
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider

class TaocheSpider(RedisCrawlSpider):
    name = 'taoche'
    allowed_domains = ['taoche.com']
    start_urls = ['http://taoche.com/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item

```

然后在settings文件中进行修改

```python
# 指定管道redis
ITEM_PIPELINES = {
   'myspider.pipelines.RedisPipeline': 300,
}
# 指定redis服务器的地址，端口，
REDIS_HOST = '127.0.0.1'
REDIS_POST = '6379'
```

调度器的配置

```python
# 去充容器的配置,使用redis集合来存储请求的指纹数据从而实现去重的持久化
DUPEFILTER_CLASS='scrapy.redis.dupefilter.RFPDupeFilter'
# 使用scrapy-redis的调度器
SCHEDULER = 'scrapy.redis.scheduler.Scheduler'
# 配置调度器是否需要持久化,是否在爬虫结束的时候不要清空redis中请求队列和指纹的set集合，持久化则为True
SCHEDULER_PERSIST = True
```

配置需要连接的数据库,关闭保护模式

```
sudo vim /etc/redis/redis.conf
bind 0.0.0.0 #需要进行来连接的IP
protected-mode no
```

### 4.3爬取的主要代码

```python
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from ..items import MyspiderItem

class TaocheSpider(RedisCrawlSpider):
    name = 'taoche'
    # allowed_domains = ['taoche.com'] # 不做域名限制
    # start_urls = ['http://taoche.com/'] # 起始的url应该去redis（公共调度器） 里面获取

    redis_key = 'taoche' # 回去redis（公共调度器）里面获取key为taoche的数据 taoche:[]
    # 老师，我给你找一下我改的源码在哪里，看看是那的错误吗
    rules = (
        # LinkExtractor 链接提取器，根据正则规则提取url地址
        # callback 提取出来的url地址发送请求获取响应，会把响应对象给callback指定的函数进行处理
        # follow  获取的响应页面是否再次经过rules进行提取url
        Rule(LinkExtractor(allow=r'/\?page=\d+?'),
             callback='parse_item',
             follow=True),
    )

    def parse_item(self, response):
        print("开始解析数据")
        car_list = response.xpath('//div[@id="container_base"]/ul/li')
        for car in car_list:
            lazyimg = car.xpath('./div[1]/div/a/img/@src').extract_first()
            title = car.xpath('./div[2]/a/span/text()').extract_first()
            resisted_data = car.xpath('./div[2]/p/i[1]/text()').extract_first()
            mileage = car.xpath('./div[2]/p/i[2]/text()').extract_first()
            city = car.xpath('./div[2]/p/i[3]/text()').extract_first()
            city = city.replace('\n', '')
            city = city.strip()
            price = car.xpath('./div[2]/div[1]/i[1]/text()').extract_first()
            sail_price = car.xpath(
                './div[2]/div[1]/i[2]/text()').extract_first()

            item = MyspiderItem()
            item['lazyimg'] = lazyimg
            item['title'] = title
            item['resisted_data'] = resisted_data
            item['mileage'] = mileage
            item['city'] = city
            item['price'] = price
            item['sail_price'] = sail_price
            print(item)
            print("解析完成")
            yield item

```

settings.py文件

```python
# Scrapy settings for myspider project

BOT_NAME = 'myspider'

SPIDER_MODULES = ['myspider.spiders']
NEWSPIDER_MODULE = 'myspider.spiders'



# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 指定管道 ，scrapy-redis组件帮我们写好
ITEM_PIPELINES = {
   'scrapy_redis.pipelines.RedisPipeline':300
}

# 指定redis
REDIS_HOST = '127.0.0.1' # redis的服务器地址，我们现在用的是虚拟机上的回环地址
REDIS_PORT = 6379 # virtual Box转发redistribution的端口


# 去重容器类配置 作用：redis的set集合来存储请求的指纹数据，从而实现去重的持久化
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

# 使用scrapy-redis的调度器
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'

# 配置调度器是否需要持久化，爬虫结束的时候要不要清空redis中请求队列和指纹的set集合，要持久化设置为True
SCHEDULER_PERSIST = True




# 最大闲置时间，防止爬虫在分布式爬取的过程中关闭
# 这个仅在队列是SpiderQueue 或者 SpiderStack才会有作用，
# 也可以阻塞一段时间，当你的爬虫刚开始时（因为刚开始时，队列是空的）
SCHEDULER_IDLE_BEFORE_CLOSE = 10
```



