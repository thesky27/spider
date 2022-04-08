# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EasecloudItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
    要获取
    1.歌曲的图片img_url
    2.album
    3.歌曲的时长duration
    4.歌曲的时长名字songname
    5.歌曲手singer
    6.歌词lyric
    7.评论comment

    """
    img_url = scrapy.Field()
    album = scrapy.Field()
    singer = scrapy.Field()
    duration = scrapy.Field()
    songname = scrapy.Field()
    lyric = scrapy.Field()
    comment = scrapy.Field()
    media = scrapy.Field()



class CommentDetail(scrapy.Item):
    """
    评论的内容又包括
    1.评论人
    2.评论内容
    3.评论时间
    4.评论点赞数
    不包括回复的内容
    """
    commenter_name = scrapy.Field()
    commenter_url = scrapy.Field()
    comment_datail = scrapy.Field()
    time = scrapy.Field()
    thumb_number = scrapy.Field()

