# 一、xpinyin模块的使用

### 1.为什么使用xpinyin模块

- 当我们让爬虫程序去访问大量的不同的网站时，有时会遇到搜索的关键词的拼音就在网址里，这就需要我们自动地去识别程序
- 举个例子就是某图网

### 2.xpinyin 了解

```python
import requests  # 导入请求包
from retrying import retry
from xpinyin import Pinyin
# 实例化一个xpinyin的对象
p = Pinyin()

# 得到汉字的拼音，一般来说使用-隔开
print(p.get_pinyin("长沙"))
# 得到汉字的多个拼音，也就是多音字
print(p.get_pinyins("厦门"))

# 得到汉字的拼音，并且没有分割
print(p.get_pinyins("厦门",""))
# 得到一个汉字的首字母
print(p.get_initial("常"))
# 得到多个汉子的首字母，并且不分割
print(p.get_initials("沙门", ""))

```

### 3.xpinyin的使用

在某图网之中，有些汉字的拼音并不能直接的通过拼音来获取网址，而是通过https://699pic.com/search/getKwInfo?kw=三个    来得到如下的内容

```
{"status":"ok","message":"\u64cd\u4f5c\u6210\u529f","data":{"kwid":"290225","pinyin":"sange"}}
```

- 注意：response.text获得的类型是字符串的类型，如果需要将上面的字符串转化为字典的话，则需要转化为json这一步

```python
import requests  # 导入请求包
from retrying import retry
from xpinyin import Pinyin
# 实例化一个xpinyin的对象
p = Pinyin()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0"
}
keyword = input("请输入你想搜索的图片")
response_url = f"https://699pic.com/search/getKwInfo?kw={keyword}"
response1=requests.get(url=response_url,headers=headers)
print(type(response1.text)) # 字符串类型，但是需要转化为json类型
res = response1.json()
keyword = res["data"]["kwid"]
print(keyword)
url = f"https://699pic.com/tupian/{keyword}.html"

@retry(stop_max_attempt_number=3)
def spider_url():
    print("+====+")
    response = requests.get(url=url,headers=headers,timeout=(3,7),allow_redirects=False)
    response.encoding=response.apparent_encoding
    print(response.url)
spider_url()
```

# 二、requests_html的使用

### 1.优势

- 自带UA，不用再写请求头
- 自动将编码格式设置为utf-8

### 2.使用

```python
import requests  # 导入请求包
from requests_html import HTMLSession

# 实例化对象
session = HTMLSession()

response_url = "https://699pic.com/tupian/hunian.html"
response = session.get(response_url)

# 获取当前连接下所有的链接
print(response.html.links)
# 获取当前连接下所有绝对链接
print(response.html.absolute_links)

# 利用xpath来获取图片的详细链接，/表示下一级目录，div[@class='list']表示class属性，@href表示属性
print(response.html.xpath("//div[@class='list']/a/@href"))

```

# 三、json的使用

### 1.json数据格式的转换

**所谓json格式的数据，其实就是指的是字符串的数据，类型是字符串**

```python
import json


data = {"name":"一个","age":18}

# 将数据转化为json格式，但是键值对不能是元组的形式
print(json.dumps(data))
# 将数据转化为json格式，但是会跳过错误，继续执行
print(json.dumps(data,skipkeys=True))
# 将转化之后的数据进行排序
print(json.dumps(data,sort_keys=True))
# 将数据变得更加紧凑
print(json.dumps(data,separators=(',',":")))
# 将转化后的数据进行缩进3个单位
print(json.dumps(data,indent=3))
with open('test01.json','w',encoding='utf-8') as f:
    # 将数据写入到json文件之中，用的是dump
    json.dump(data,f,indent=4)

# loads的用法跟dumps的用法是差不多的，但是loads是将json字符串转化为正常的数据
with open('test01.json','r',encoding='utf-8') as f:
    # 将数据从json文件之中读取出来，用的是load
    print(json.load(f))
```

### 2.json获取网页上的数据

运用这种方法要注意以下几点

1. 先要模拟登录网站，并保持会话，防止后续直接访问网站失败
2. 找到能够获取的json数据的网址，然后发起请求，进行数据的转换（转json），进行数据的处理

```python
import requests,json
from datetime import datetime
session = requests.session()
url = 'https://passport.17k.com/ck/user/login'
book_url = "https://user.17k.com/ck/author/shelf?page=1&appKey=2406394919"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0"
}
data = {
    'loginName':'你的账号',
    "password":"你的密码"
}
res = session.post(url=url,data=data,headers=headers)
response = session.get(url=book_url).json()
for i in response['data']:
    bookName = i['bookName']
    bookClass = i["bookCategory"]['name']
    lastUpdateCharter = i['lastUpdateChapter']['name']
    updateTime = i['lastUpdateChapter']['updateTime']
    updateTime = datetime.fromtimestamp(int(updateTime)//1000)
    author = i['authorPenName']
    print(bookClass,bookName,lastUpdateCharter,updateTime,author)

```

### 3.jsonpath的使用

##### 3.1xpath中各符号的含义

/：表示子目录，也表示根目录

@：表示属性，用在div[@class='list']或者是@href这个上面

//：直接它之下所有的元素

*：表示所有的元素

.：表示当前元素

选择从1开始

##### 3.2jsonpath的使用

$：表示根目录

..：表示递归查找

@：表示当前元素

[]:表示子元素操作符

?()：应用于过滤的表达式

一般的话各个级之间用.隔开

选择从0开始

含操作符和操作数时就是用小括号加上

![image-20220125204639158](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20220125204639158.png)

### 4.re正则表达式

re.findall：从所得到的所有字符串里查找匹配

re.compile:得到一个正则表达式

主要就是用到这两个

##### 4.1re.findall的使用

```python
from requests_html import HTMLSession
import re
url = "https://www.89ip.cn/"
session = HTMLSession()
response = session.get(url=url)
result = re.findall('<tr>.*?<td>(.*?)</td>', response.text, re.S)
result = [i.strip() for i in result]
print(result)
```

##### 4.2re.compile以及re迭代器的使用

re.finditer——用?P<名称>来取名，会得到一个迭代对象，然后通过循环取出，i.group(你想要取出的名字)

```python
from requests_html import HTMLSession
import re
url = "https://www.89ip.cn/"
session = HTMLSession()
response = session.get(url=url)
re_regulate = re.compile('<tr>.*?<td>(?P<IP>.*?)</td>.*?<td>(?P<PORT>.*?)</td>.*?<td>(?P<LOCA>.*?)</td>.*?<tr>',re.S)
result = re_regulate.finditer(response.text)
for i in result:
    ip = i.group('IP')
    PORT = i.group('PORT')
    LOCA = i.group('LOCA')
    print(ip,PORT,LOCA)
```

