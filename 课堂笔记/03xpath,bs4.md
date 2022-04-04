# 一、xpath

### 1.xpath的语法介绍

//：表示根目录，text()：表示元素里面的内容

.：表示当前节点，/：表示下一节点

**要想使用xpath语法，就要安装lxml包，并从里面导入etree**

一般的话如果是html的网页转化成的字符串，就要用etree.HTML()

如果是文件的话，就要用etree.parse()来进行使用

**注意！！返回的都是列表**

### 2.xpath的使用

##### 1.etree.HTML的使用

```python
from lxml import etree
data = """
<div>
    <ul>
         <li class="item-0"><a href="link1.html">first item</a></li>
         <li class="item-1"><a href="link2.html">second item</a></li>
         <li class="item-inactive"><a href="link3.html"><span class="bold">third item</span></a></li>
         <li class="item-1"><span class="bold">fourth item</span><a href="link4.html">fourth item</a></li>
         <li class="item-0"><a class="test" href="link5.html">fifth item</a></li>
         <li class="item-0" vmid="10023898942">bsajkfhsdbfhjsdgbhfds</li>
         <li class="item-0"><a class="test" href="link5.html">fifth item</a></li>
    </ul>
 </div> 
        """
tree = etree.HTML(data)
# tree1 = etree.parse('test01.json')
# 获取第二个li的节点下的内容
print(tree.xpath('//div/ul/li[2]/a/text()'))
# 通过指定的标签属性值来获取倒数第二个的li的内容
print(tree.xpath('//li[@vmid="10023898942"]/text()'))
# 获取a的class属性为test的所有内容
print(tree.xpath('//div/ul//a[@class="test"]//text()'))
# 获取第三个li的href属性值
print(tree.xpath('//li[@class="item-inactive"]/a/@href'))
```

##### 2.etree.parse的使用

```python
from lxml import etree
tree = etree.parse('test01.html')

# 获取文件当中的第二个div下的h2的小标题
print(tree.xpath('//div/div[2]/h2/text()')[0])

# 当要获取多个的时候，用管道符|隔开，并且它们之间互不影响,这里是获取第一个和第三个下的所有的li的内容
print(tree.xpath('//div/div[1]//li/text()|//div/div[3]//li/text()'))
# child:选取当前节点的所有子元素
print(tree.xpath('//div/div[1]/child::*//text()'))

# attribute:得到标签的属性值
print(tree.xpath('//div/div[2]/attribute::id'))
print(tree.xpath('//div/div[2]/attribute::data-h'))
print(tree.xpath('//div/div[2]/attribute::*'))
```



- 
  与attribute，child有相同用法的还有几个
- ancestor ：选取父辈元素，ancestor-or-self:选取父辈元素以及自己
-  following：选取当前节点结束标签之后的所有节点
- preceding：选取当前节点开始标签之前的所有的节点

### 3.图片爬取代码实际案例

```python
from lxml import etree
from requests_html import HTMLSession
from xpinyin import Pinyin
p = Pinyin()
keyword = input('请输入你想爬取的相关图片')
keyword = p.get_pinyin(keyword,"")
print(keyword)
session = HTMLSession()
number = 1
a = 1
# 得到有多少页数，最多只能得到10页图片，等到后面会继续完善的
def get_number(number,keyword):
    response = session.get(url=f'https://www.sucai999.com/searchlist/{keyword}-{number}.html')
    tree = etree.HTML(response.text)
    result = tree.xpath('//div[@class="pt10 pages"]/a')
    return len(result)
# 将这一页的图片保存下来
def save_img(tree,a):
    b = 1
    for li in tree.xpath('//section[@class="responsive flow leshembox"]/ul//li'):
        base_url = li.xpath('./figure/a/img/@data-src')[0]
        name = li.xpath('./figure/a/img/@title')[0]
        response1 = session.get(url=base_url)
        with open(f'images/第{a}页-第{b}章-{name}.jpg','wb') as f:
            f.write(response1.content)
        b += 1
        print(f'第{a}页-第{b}章-{name}.jpg，这张图片已经下载完成')

end_number = get_number(number=number,keyword=keyword)

print(f'开始下载图片,共{end_number-1}页',)

for num in range(1, end_number):
    url_res = f'https://www.sucai999.com/searchlist/{keyword}-{num}.html'
    response_res = session.get(url=url_res)
    tree = etree.HTML(response_res.text)
    save_img(tree,a)
    a += 1
print('下载任务完成')
```

### 4.bs4

##### 4.1bs4的基本使用

```python
# pip install bs4 -i https://pypi.douban.com/simple/

from bs4 import BeautifulSoup
import re
html = open('test01.html','r',encoding='utf-8').read()
soup = BeautifulSoup(html,'html.parser')

""" 1.最常用的就是，标签名字 """
# soup直接加一个标签名就是只取第一个的标签值，返回的是<class 'bs4.element.Tag'>
print(soup.title)
print(soup.a)
print(soup.li)
print(type(soup.li))

""" 2.获取标签的属性值 ,attrs返回的是属性值字典形式,可以通过get方法来得到属性值，get_text():获取标签里面的内容包括其所有的子孙节点"""
print(soup.a.attrs)
print(soup.a.attrs.get('href'))
print(soup.a.get_text())

# 查找所有的a标签，当然也可以用正则re来表示
print(soup.find_all('a'))
# 查找只有story的内容
print(soup.find_all(text='story'))
# 用compile来表示，其中text=re.compile
print(soup.find_all(text=re.compile(r'.*?stroy.*?')))
# 限定找的a标签的类是sister
print(soup.find_all('a',class_="sister"))



# print(soup)
# css选择器样式,#代表id，.代表class，大于表示子节点，空格表示所有子节点
print(soup.select('#testid > h2'))
# 查找所有的li
print(soup.select('#testid li'))
# 不能用下标来取值
# print(soup.select('#testid li[1]'))



# 下面这两种都是一样的
print(soup.select('#testid li:nth-of-type(3)'))
print(soup.select('#testid li:nth-child(3)'))
# 只选择一个
print(soup.select_one('#testid li:nth-of-type(3)'))
```

##### 4.2bs4的使用实例

**爬取b站动漫的排行榜**

```python
from bs4 import BeautifulSoup
from requests_html import HTMLSession

session = HTMLSession()

url = "https://www.bilibili.com/v/popular/rank/guochan"

cartoon_name=[]
update=[]
view_counts = []

response = session.get(url=url)
soup = BeautifulSoup(response.text,'html.parser')
# 获取动画名
for i in soup.select('.info>a'):
    cartoon_name .append(i.get_text())

#获取更新集数
for i in soup.select('.info>div.detail>span'):
    update .append(i.text.strip())

#  获取播放量
for i in soup.select('.info>div.detail>div>span'):
    view_counts.append(i.get_text().strip())
    
```

# 二、总结

从html网页的元素中获取想要的信息一共有四种方法

1.etree中的xpath——推荐使用，速度虽然不及正则re，但是规则容易记，查找速度快

2.bs4中的beautifulsoup——不推荐使用，速度较慢，不容易记住语法规则，查找速度较慢

3.re正则——查找速度最快，但是容易出问题，并且规则难记

**一般推荐使用etree中的xpath来搜索想要的文本内容**
