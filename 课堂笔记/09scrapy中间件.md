# 一、反爬虫的策略

1. 更换UA：用户标识符，动态的设置，随即切换User-agent，模拟不同用户之间的浏览器信息	
2. 禁用cookie，不向网站发送cookie，因为有的网站通过cookie来识别爬虫的行为
3. 设置COOKLIES_ENABLED控制cookie中间件的开启与关闭
4. 可以设置延迟下载，防止访问过于频繁，最好是2秒以上
5. 使用UP地址池，代理IP，大部分是根据IP来ban的
6. 使用Crawlera(专门用于爬虫的代理组件)

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawlera.CrwaleraMiddleware':600
}
CRAWLERA_ENABLED = True
CRAWLERA_USER = "注册购买的UserKey"
CRAWLERA_PASS = "注册购买的PASSWORD"

```

# 二、设置下下载中间件

- 当引擎传递给下载器请求的时候，下载中间件可以对请求添加请求信息（请求头，ip，proxy等）
- 当完成下载请求传递回响应的时候，可以进行对响应处理。

## 1.中间件文件的介绍

```python
class EasecloudDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

```

process_request：请求需要被下载时，经过所有下载器中间件的process_request被调用

- 如果返回	none，则就会继续下载
- 返回Response object ：停止执行该函数，并且执行process_response函数
- 返回Requesrt object ：停止执行该函数，并且执行process_exception函数

process_response:用来处理响应的函数

process_exception：处理异常请求和响应

## 2.功能的使用

**请求中进行UA伪装**

首先在settings中添加UA大全，然后在process_request里面去引入：

```
USER_AGENT_LIST = [
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
		'Opera/8.0 (Windows NT 5.1; U; en)',
		'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
		'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
		'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
		'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ',
	]
```



```python
    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        # uA伪装
        request.heades["User-Agent"] = random.choice(spider.settings.get('USER_AGENT_LIST'))
        return None
```

**设置代理IP**

1.process_request加在这个里面，每次都会换IP，以防止反爬，但是很费钱

2.process_exception加载这个里面，只有当ip出现问题时才会更换IP

**处理响应**

- 比如说你访问的页面实现了软加载或者是异步，不能直接的显示全部信息，这时就需要对响应重新设置。
- 在process_response这个里面去实现相对应的方法，比如使用selenium自动化等等

# 三、scrapy模拟登录，金属

## 1.使用requests进行模拟登录

1. 使用登陆之后的cookie，将data数据加在请求头里面，通过headers进行属性值的传递
2. 也就是通过cookies进行属性传值，键值对的形式传值

## 2.找到登陆的POST接口输入正确的参数进行登录

1. 找到formdata里面的参数，看下是否需要改动
2. 直接输入正常的用户名和密码，进行直接登录

## 3.scrapy模拟登录

在整个scrapy框架运行之前，需要一个启动软件，这个启动软件的条件是start_urls,从这个网页发起请求，才会有后面的调度器，下载器等。

所以这里可以重写这个方法，进行携带cookie

**注意：这里必须有yield返回，不然相当于没有传递东西**

使用cookie之前，要在settings设置中开启Cookie因为一般会关闭cookie

### 3.1使用登陆之后的cookie

```python
    def start_requests(self):
        # 添加登陆之后的cookie
        cookie = ""
        cookie_dict={}
        for i in cookie.split(";"):
            cookie_dict[i.split('=')[0]]=i.split('=')[1]
        yield scrapy.Request(url=self.start_urls[0],callback=self.parse,cookies=cookie_dict)
```

### 3.2使用请求头

```python
def start_requests(self):
    headers = {
        "Cookie":"cookie_info"
    }
    yield scrapy.Request(url=self.start_urls[0],callback=self.parse,headers=headers)
```



### 3.3使用formdata参数来进行启动

```python
    def parse(self, response):
        
        aaa = "zzz"
        bbb = "aaa"
        post_data = {
            "aaa":aaa,
            "bbb":bbb
        }
        yield scrapy.FormRequest(url="要请求的网络地址",formdata=post_data,callback=self.parse_datail)

```

### 3.4直接传递用户名和密码参数

```python
    def parse(self, response):

        yield scrapy.FormRequest.from_response(
            response=response,
            formdata={
                "用户名字段":"用户名",
                "密码字段":"密码"
            },
            callback=self.parse_datail
        )
```

