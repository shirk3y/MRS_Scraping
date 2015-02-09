from scrapy import log


class AbstractsPipeline(object):
    def process_item(self, item, spider):
        if not item['title']:
            spider.log('No title in %s' % item, level=log.WARNING)
        if not item['symposium_name']:
            spider.log('No symposium_name in %s' % item, level=log.WARNING)
        return item
