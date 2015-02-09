
BOT_NAME = 'abstracts'

SPIDER_MODULES = ['abstracts.spiders']
NEWSPIDER_MODULE = 'abstracts.spiders'

USER_AGENT = 'Mozilla/5.0'

SPIDER_MIDDLEWARES = {
    'abstracts.spidermiddleware.storecsv.StoreCsvMiddleware': 500
}

COMMANDS_MODULE = 'scrapy_datatest'
