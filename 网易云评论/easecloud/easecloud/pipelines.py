# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
import logging,csv

from scrapy.pipelines.images import ImagesPipeline

log = logging.getLogger(__name__)

class EasecloudPipeline:
    def open(self,spider):
        log.warning("爬虫开始,运行")
        self.headers = ['歌曲名字','歌手','专辑','歌曲时长','歌词']
        self.headers_comment = ['评论人','评论内容','评论时间','评论点赞数']
        self.info = open('./wycomment.csv','w+',encoding='utf-8',newline='')
        self.info_comment = open('./wycomment_comment.csv','w+',encoding='utf-8')


    def process_item(self, item, spider):
        try:
            media_io = item['media']
            with open(f'./music/{item["album"]}.mp3','wb') as f:
                f.write(media_io.getvalue())
                f.close()
        except Exception as e:
            log.warning(f'出错了{e}，音频的名字是{item["songname"]}')
        finally:
            data = []
            data_comment = []
            data_singer =  item['singer']
            data_songname =  item['songname']
            data_album=  item['album']
            data_duration =  item['duration']
            data_lyric =  item['lyric']
            data_comment_commenter_name = item['comment']['commenter_name']
            data_comment_comment_datail = item['comment']['comment_datail']
            data_comment_time = item['comment']['time']
            data_comment_thumb_number = item['comment']['thumb_number']
            data.append((data_singer,data_songname,data_album,data_duration,data_lyric))
            data_comment.append(data_comment_commenter_name,data_comment_comment_datail,data_comment_time,data_comment_thumb_number)
            writer = csv.writer(self.info)
            writer.writerows(self.headers)
            writer.writerows(data)
            writer_comment = csv.writer(self.info_comment)
            writer_comment.writerow(self.headers_comment)
            writer_comment.writerows(data_comment)
        return item

    def close_spider(self,spider):
        log.warning("爬虫结束，存储数据完毕")
        self.info.close()
        self.info_comment.close()


class ImgEasecloudPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):

        yield scrapy.Request(item['img_url'])
    def file_path(self, request, response=None, info=None, *, item=None):
        # 指定存储图片的名字以及路径
        return item['songname']
    def item_completed(self, results, item, info):
        # 返回数据给下一个需要执行的管道类
        return item


