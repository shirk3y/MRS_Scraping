import scrapy


class AbstractItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    symposium_name = scrapy.Field()