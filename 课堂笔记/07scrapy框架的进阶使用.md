### 一、思考

#### 1.为什么下面的代码会用到yield？

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
            item['introduce'] = introduce
            items.append(item)
            # 将返回的数据交给pipeline
            yield item
        # 返回数据，但是不经过pipeline
        return items

```

yield是一个迭代器，可以被迭代调用，通常用在循环当中，但是不会像return那样会退出。

在此就是将从网页获取到的数据先交给pipeline进行处理，并保存而不是直接返回

#### 2.持久化存储

就是在pipiline中使保存文件，pipeline.py文件

```
class DoubanPipeline:
    def process_item(self, item, spider):
        with open('movie.txt','w',encoding='utf-8') as f:
            f.write(f"{item['title']}:{item['introduce']}")
        return item
```

创建了一个类，item就是从主爬虫文件传过来的数据，spider就是爬虫的本体。

**使用管道之前一定要在settings文件中开启管道**

```python
# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'easecloud.pipelines.EasecloudPipeline': 300,
}
```

以下是主要保存的代码

```python
import scrapy
from ..items import DoubanItem

class DoubanSpider(scrapy.Spider):
    name = 'douban' #爬虫名字
    # allowed_domains = ['https://www.douban.com/'] # 允许爬取的范围
    start_urls = ['https://movie.douban.com/top250'] #第一个访问的URL

    def parse(self, response):
        item = {}
        info = response.xpath('//div[@class="info"]')
        for div in info:
            title = div.xpath("./div[1]/a/span[1]/text()").extract_first()
            introduce = div.xpath("./div[2]/p[1]/text()").extract()
            introduce = ''.join(j.strip() for j in [i.replace("\\xa0",'') for i in introduce])
            item['title'] = title
            item['introduce'] = introduce
            # 将返回的数据交给pipeline
            yield item
        # # 返回数据，但是不经过pipeline
        # return items

```

#### 3.存在反复打开关闭文件的问题

但是以上代码有缺陷，没有关闭文件，但是如果加上文件的话，就会一直重复的打开与关闭，非常的麻烦。所以一般不会直接使用withopen 方法。一般会使用的方法：**创建生命周期，修改pipeline文件**



```python
class DoubanPipeline:
    # 生的时候做什么事情，再开始的时候做什么事情
    def open_spider(self,spider):
        print("爬虫开始运行")
        self.fp = open('./movie.txt','w',encoding='utf-8')

        pass
    def process_item(self, item, spider):

        self.fp.write(f"{item['title']}:{item['introduce']}")
        return item
    # 死的时候做什么事情
    def close_spider(self,spider):
        print("爬虫结束运行")
        self.fp.close()
```

这样的话就会只打开一次文件。但是i上述的spider根本没有用？是真的没有用吗？

#### 4.spider存在的意义？

一个爬虫项目可以有多个爬虫的代码，比如可以爬某度，某东。某易，但它们都是共用的配置文件，包括管道文件，怎么才能区分呢？就是靠spider

```
# 在pipeline中通过以下代码来对不同爬虫来源的数据进行区分。
if spider.name="你的爬虫名字"
```

### 二、logging模块的使用

当我们的代码报错的时候，我们希望知道是在哪出的错误，尤其是对应于一个框架来说，使用日志能更好的检查错误，修正BUG

```python
import scrapy
from ..items import DoubanItem
import logging
logger = logging.getLogger(__name__)

class DoubanSpider(scrapy.Spider):
    name = 'douban' #爬虫名字
    # allowed_domains = ['https://www.douban.com/'] # 允许爬取的范围
    start_urls = ['https://movie.douban.com/top250'] #第一个访问的URL

    def parse(self, response):
        item = {}
        info = response.xpath('//div[@class="info"]')
        for div in info:
            title = div.xpath("./div[1]/a/span[1]/text()").extract_first()
            introduce = div.xpath("./div[2]/p[1]/text()").extract()
            introduce = ''.join(j.strip() for j in [i.replace("\\xa0",'') for i in introduce])
            item['title'] = title
            item['introduce'] = introduce
            logger.warning(title)
            # 将返回的数据交给pipeline
            # yield item
        # # 返回数据，但是不经过pipeline
        # return items
```

**这样就会打印日志文件的信息，但是日志文件的打印信息的等级要和配置文件中的一致。**

在settings里面设置

```python
LOG_FILE = './log.log'
```

这样的话打印的日志信息就i会保存在这个文件里面

### 三、全站爬取

全站爬取的时候在进行访问第一个网页的时候，会访问其他的访问，在此时会将新的url加入到调度器里去。

之前我们只是获取第一页的内容



**获取全站**

现在就想办法获取下一页的URL就可以了，然后将他交给什么函数来进行处理。使用scrapy.Request()可以将新获取的url继续进行解析

```python
import scrapy
from ..items import DoubanItem
import logging
logger = logging.getLogger(__name__)

class DoubanSpider(scrapy.Spider):
    name = 'douban' #爬虫名字
    # allowed_domains = ['https://www.douban.com/'] # 允许爬取的范围
    start_urls = ['https://movie.douban.com/top250'] #第一个访问的URL

    def parse(self, response):
        item = {}
        info = response.xpath('//div[@class="info"]')
        for div in info:
            title = div.xpath("./div[1]/a/span[1]/text()").extract_first()
            introduce = div.xpath("./div[2]/p[1]/text()").extract()
            introduce = ''.join(j.strip() for j in [i.replace("\\xa0",'') for i in introduce])
            item['title'] = title
            item['introduce'] = introduce
            # break
            # 将返回的数据交给pipeline
            # yield item
        # # 返回数据，但是不经过pipeline
        # return items
        next_url = response.xpath('//div[@class="paginator"]/span[3]/a/@href').extract()
        # logger.warning(next_url)
        if next_url !=None:
            next_url = 'https://movie.douban.com/top250'+next_url
            yield scrapy.Request(
                url=next_url,#访问的地址
                callback=self.parse,#请求后得到的相应，需要交给哪个函数来进行处理

            )
```

**进一步获取详情页**



```python
import scrapy
from ..items import DoubanItem,DoubanDetailItem
import logging
logger = logging.getLogger(__name__)

class DoubanSpider(scrapy.Spider):
    name = 'douban' #爬虫名字
    # allowed_domains = ['https://www.douban.com/'] # 允许爬取的范围
    start_urls = ['https://movie.douban.com/top250'] #第一个访问的URL


    # url模板
    url = 'https://movie.douban.com/top250?start=%d&filter='

    def parse(self, response):
        max_page = response.xpath('//div[@class="paginator"]/a[9]/text()').extract_first()
        for page in range(0,int(max_page)*25,25):
            next_url=self.url %page
            print(next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_douban,
                meta={'index':page}
            )
            break

    def parse_douban(self,response):
        item = DoubanItem()
        info = response.xpath('//div[@class="info"]')
        for div in info:
            title = div.xpath("./div[1]/a/span[1]/text()").extract_first()
            introduce = div.xpath("./div[2]/p[1]/text()").extract()
            introduce = ''.join(j.strip() for j in [i.replace("\\xa0",'') for i in introduce])
            item['title'] = title
            item['introduce'] = introduce
            detail_url = div.xpath('./div[1]/a/@href').extract_first()
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                meta={'movie_detail':item}
            )
            break
    def parse_detail(self,response):
        info = response.xpath('/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[2]//text()').extract()
        info = [i.strip() for i in info]
        movie_introduce = response.xpath('/html/body/div[3]/div[1]/div[3]/div[1]/div[3]/div/span[2]/text()').extract()
        movie_introduce = ''.join(j.strip() for j in [i.replace("\\u3000", '') for i in movie_introduce])

        detail_item = DoubanDetailItem()
        detail_item['info'] = info
        detail_item['movie_introduce'] = movie_introduce
        item = response.meta['movie_detail']
        item['detail'] = detail_item
        logger.warning(item)
```

