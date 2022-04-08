import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging
from ..items import EasecloudItem, CommentDetail
import json
import io
log = logging.getLogger(__name__)
from.parse_params import eneryctAES

class WycommentSpider(CrawlSpider):
    name = 'wycomment'
    start_urls = ['https://music.163.com/discover/toplist?id=19723756']
    rules = (
        Rule(LinkExtractor(allow=r'toplist\?i'), callback='parse_item', follow=True),
    )
    encrypt = eneryctAES()


    def parse_item(self, response):
        """
        通过访问原始的https://music.163.com/discover/toplist?id=19723756这个网址，得到每一个排行榜的链接
        接着对这些链接通过这个函数进行访问
        因为信息在js文本中，所以通过js来获取

        遍历每一首歌，获取歌曲song_id，歌曲所属的专辑album，歌曲的图片地址img_url，歌手singer，歌曲时长total_time，然后将剩下的信息交给下一个函数解析

        :param response:
        :return:
        """
        log.warning(f'爬取的排行榜网址是{response.request.url}')
        log.warning(f'UA标识：{response.request.headers["User-Agent"]}')
        item = EasecloudItem()
        try:
            detail = response.xpath('//textarea[@id="song-list-pre-data"]/text()').extract_first()
            log.warning(type(detail))
            # 在这里会出现问题，detail可能会返回none，因为网站做了反爬机制
            result = json.loads(detail)
            for i in range(len(result)):
                album =result[i]['album']['name']
                img_url =result[i]['album']['picUrl']
                singer = result[i]['artists'][0]['name']
                total_time = result[i]['duration']
                song_id = result[i]['id']
                total_time = total_time // 1000

                minute = total_time // 60
                second = total_time % 60
                item['album'] = album
                item['img_url'] = img_url
                item['singer'] = singer
                item['duration'] = f'{minute}:{second}'
                yield scrapy.Request(url=f'https://music.163.com/song?id={song_id}',callback=self.parse_detail_songname,meta={'song_id':song_id,'item':item})
                break
        except Exception as e:
            log.warning(f'parse_item函数出现了问题，问题是{e},出现错误的网址是{response.request.url}')



    def parse_detail_songname(self,response):
        song_id = response.meta['song_id']
        item = response.meta['item']
        songname = response.xpath('//title/text()').extract_first()
        item['songname'] = songname
        liric_data = self.encrypt.resultEncrypt(self.encrypt.lyric % song_id)
        yield scrapy.FormRequest(url=self.encrypt.lyric_url,
                                 callback=self.parse_detail_liric, meta={'song_id': song_id, 'item': item},
                                 formdata=liric_data)

    def parse_detail_liric(self,response):
        """

        1.含有歌词内容的url需要有提交的参数，params以及enSecKey,这涉及到JS逆向解密AES，rsa等，比较复杂，自己可以去了解
        2.与解密有关的函数有create16RandomBytes，AESEncrypt，RSAEncrypt，resultEncrypt，目的就是得到合适的提交参数
        3.获取歌词内容
        :param response:
        :return:
        """
        try:
            song_id = response.meta['song_id']
            item = response.meta['item']
            # 在这里会出现问题，detail可能会返回none，因为网站做了反爬机制
            # 会出现一开始访问不到的情况，之后再解决
            result = json.loads(response.text)
            lyric = result["lrc"]["lyric"]
            lyric = self.parse_lyric(lyric)
            item['lyric'] = lyric

            comment_data = self.encrypt.resultEncrypt(self.encrypt.comment % (song_id,song_id))
            yield scrapy.FormRequest(url=self.encrypt.comment_url,
                                         callback=self.parse_detail_comment, meta={'id': song_id, 'item': item},
                                         formdata=comment_data)
        except Exception as e:
            log.warning(f'parse_detail_liric函数出现了错误,{e},出现错误的网址是{response.request.url}')


    def parse_detail_comment(self,response):
        """
        1.分析评论，发现评论的呢iron过于复杂所以就只爬取精彩的评论
        2.在精彩的评论中爬取 1.评论人、评论内容、评论时间、评论点赞数、不包括回复的内容
        :param response:
        :return:
        """
        try:
            song_id = response.meta['id']
            item = response.meta['item']
            comment_item = CommentDetail()
            result = json.loads(response.text,strict = False)
            for i in range(len(result['data']['hotComments'])):
                comment_item['comment_datail'] = result['data']['hotComments'][i]['content']
                comment_item['time'] = result['data']['hotComments'][i]['timeStr']
                comment_item['thumb_number'] = result['data']['hotComments'][i]['likedCount']
                comment_item['commenter_name'] = result['data']['hotComments'][i]['user']['nickname']
                comment_item['commenter_url'] = result['data']['hotComments'][i]['user']['avatarUrl']
                item['comment'] = comment_item
                meida_data = self.encrypt.resultEncrypt(self.encrypt.meida % song_id)
                yield scrapy.FormRequest(url=self.encrypt.meida_url,
                                            callback=self.parse_detail_media_url, meta={'song_id': song_id, 'item': item},
                                            formdata=meida_data)
                break
        except Exception as e:
            log.warning(f'parse_detail_comment函数出现了错误，错误是{e},出现错误的网址是{response.request.url}')

    def parse_detail_media_url(self,response):
        item = response.meta['item']
        try:
            result = json.loads(response.text,strict = False)
            media_url = result['data'][0]['url']
            log.warning(f"这是你找到的音频网址{media_url}")
            if media_url:
                yield scrapy.Request(url=media_url,callback=self.parse_detail_media,meta={'item':item})
        except Exception as e:
            log.warning(f"parse_detail_media_url函数出现了问题{e},找不到访问url失败,出错网址是{response.request.url}")


    def parse_detail_media(self,response):

        item = response.meta['item']
        # log.warning(f'这是所有数据的和{item}')
        try:
            media_io = io.BytesIO()
            media_io.write(response.body)
            item['media'] = media_io
        except Exception as e:
            log.warning("没有二进制数据")

        yield item
    def parse_lyric(self,string):
        lyric = ''.join(string.split())
        lyric = lyric.replace(']', '[')
        lyric = lyric.split('[')
        lyric = [lyric[2 * i] for i in range(len(lyric)) if 2 * i <= len(lyric) and i != 0]
        return ''.join(lyric)




"""
评论  https://music.163.com/weapi/comment/resource/comments/get?csrf_token=
音频 https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=
歌词     https://music.163.com/weapi/song/lyric?csrf_token=
"""



