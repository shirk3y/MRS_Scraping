Mrs.org spider
===

Installation:
---

If you don't have scrapy, install it:

    pip install scrapy

Running
---

    scrapy crawl mrs.org

Or with output file specified:

    scrapy crawl mrs.org -o abstracts.csv

This site is very slow, so HTTPCACHE module is highly recommended if we do recrawls. To enable it, please run scrapy with following arguments:

    scrapy crawl mrs.org -o abstracts.csv -s HTTPCACHE_ENABLED=1