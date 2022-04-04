# 一、scrapy shell的使用

在命令行输入scrapy shell “网址名”，以百度的域名为例子，需要了解即可，可以打印你想知道的信息

```shell
(python38) F:\SpiderProject\spider\某易云评论\easecloud\easecloud>scrapy shell "https://www.baidu.com"
[s] Available Scrapy objects:
[s]   scrapy     scrapy module (contains scrapy.Request, scrapy.Selector, etc)
[s]   crawler    <scrapy.crawler.Crawler object at 0x0000022A3FFA8130>
[s]   item       {}
[s]   request    <GET https://www.baidu.com>
[s]   response   <200 https://www.baidu.com>
[s]   settings   <scrapy.settings.Settings object at 0x0000022A3FFA8460>
[s]   spider     <DefaultSpider 'default' at 0x22a41038e20>
[s] Useful shortcuts:
[s]   fetch(url[, redirect=True]) Fetch URL and update local objects (by default, redirects are followed)
[s]   fetch(req)                  Fetch a scrapy.Request and update local objects
[s]   shelp()           Shell help (print this help)
[s]   view(response)    View response in a browser
>>>

```

可以获取请求头的信息，也可以在命令行获取相应的对应信息。

# 二、crawl spider

是scrapy框架的派生类，命令,当然也可以自己打，但不推荐，提供了新的属性和方法

```python
scrapy genspider -t crawl drdouban douban.com
```

定义了某一类的规则来进行解析URL,执行上述命令后就会生成以下代码

```python
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class DrdoubanSpider(CrawlSpider):
    name = 'drdouban'
    allowed_domains = ['douban.com']
    start_urls = ['http://douban.com/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'),#用于定义需要提取的链接
             callback='parse_item',# 指定函数进行处理
             follow=True),# 是否需要跟进爬取
    )
    def parse_item(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item
```

其中重要的是Rules这个重点解释

- LinkExtractor用于定义提取的链接，LinkExtractor(allow=r'Items/'),#用于定义需要提取的链接，可以用正则来表示。
- callback：从上面获取到连接之后就会进行回调函数，接受一个response作为第一个参数
- follow：一个bool值，确定是否需要跟进，是则为true,不是的话就false

**注意：在crawlspider中千万不能写parse这个函数，因为在原本的spider中已经有parse这个函数了。**

# 三、imagepipline的使用

## 1.思路

- 首先是要根据网页的内容来获取所有的图片的URL
- 然后将URL传入到Imagespipeline管道里面去
- 通过管道在进行图片网址的访问与请求

## 2.注意

**管道的方法一定要继承Imagespipiline这个管道**

**必须定义字段名**

**必须重写三种方法：get_media_requests，file_path，item_completed**

**必须开启管道，并且指定图片数据所保存的路径，IMAGES_STORE错一个字母都不行**

## 3.代码展示

### chinaz.py文件

```python
import scrapy

from ..items import ChinazItem


class ChinazSpider(scrapy.Spider):
    name = 'chinaz'
    allowed_domains = ['chinaz.com']
    start_urls = ['https://sc.chinaz.com/tupian/']

    def parse(self, response):
        item = ChinazItem()
        container = response.xpath('//div[@id="container"]/div')
        for div in container:
            src = div.xpath('./div/a/img/@src2').extract_first()
            src = "https:"+src
            src = src.replace('_s','')
            item['src'] = src
            print("这是在著代码里面的·1",src)
            yield item

```

### pipilines.py文件

```python
# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

class ChinazPipeline(ImagesPipeline):
    print("开始使用这个类")
    def get_media_requests(self, item, info):
        print(item['src'],"这是图片的地址")
        yield scrapy.Request(item['src'])

    def file_path(self, request, response=None, info=None, *, item=None):
        # 指定存储图片的名字以及路径
        image_name = request.url.split('/')[-1]
        return image_name
    def item_completed(self, results, item, info):
        # 返回数据给下一个需要执行的管道类
        return item
```

settings.py文件

```python
# 指定存储的路径
IMAGES_STORE='./images'
```

item.py文件

```python
class ChinazItem(scrapy.Item):
    src = scrapy.Field()
```

