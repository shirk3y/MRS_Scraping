import re

import scrapy
from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from w3lib.html import remove_tags
from html2text import HTML2Text

from abstracts.items import AbstractItem


def css2xpath(css):
    """Utility function to convert CSS query to XPATH query"""
    sel = scrapy.Selector()
    return sel._css2xpath(css)


class MrsOrgSpider(CrawlSpider):
    name = 'mrs.org'
    start_urls = ['http://www.mrs.org/spring-meetings/',
                  'http://www.mrs.org/fall-meetings/']
    # Crawling rules
    rules = (
        Rule(
            LinkExtractor(
                allow='\d{4}',  # Year must be present
                restrict_xpaths=[
                    css2xpath('.title a'),
                    css2xpath('#pastMeetings h3 a')
                ],
            )
        ),
        # Old abstracts (<2011)
        Rule(
            LinkExtractor(
                restrict_xpaths=[
                    css2xpath('ul.nav li.current a:contains(Abstracts)'),
                ]
            ),
        ),
        Rule(
            LinkExtractor(
                allow='abstract-[\w\d]+/?$'
            ),
            callback='parse_abstracts_old',
        ),
        # New abstracts (>=2011)
        Rule(
            LinkExtractor(
                restrict_xpaths=[
                    css2xpath('ul.nav li.current '
                              'a:contains("Technical Sessions")'),
                ]
            ),
        ),
        Rule(
            LinkExtractor(
                restrict_xpaths=[
                    css2xpath('#sessions a:contains("Program/Abstracts")'),
                ]
            ),
            callback='parse_abstracts_new'
        ),
    )

    def __init__(self, *args, **kwargs):
        super(MrsOrgSpider, self).__init__(*args, **kwargs)
        self.html2text = HTML2Text()
        self.html2text.body_width = 0
        self.html2text.ignore_images = True

    def parse_abstracts_old(self, response):
        sel = scrapy.Selector(response)
        # Extract symposium name
        symposium_name, = sel.css('h1::text').extract()[:1] or ['']
        symposium_name = re.sub('.+?:', '', symposium_name, count=1)
        symposium_name = symposium_name.strip()
        # Extract malformed content column
        column = '\n'.join(sel.css('div#contentCol').extract())
        # Remove newline chars that are make no sense in HTML (only <br> do)
        flat_text = re.sub(r'[\n\r]+', '', column, flags=re.MULTILINE)
        # Convert HTML to Markdown
        flat_text = self.html2text.handle(flat_text)
        # Each abstract starts with hour and abstract no, so we split by it
        section_re = r'''
            \** # Bold text 
            (?:\d+:\d+\ *[AP]M\ *)? # Optional hour
            [_\*\s]* # Bold, italics
            [\*A-Z/]+\d+\.\d+ # Abstract number
            [_\*\s]*.* # End bold, italics
        '''
        # Skip first element, because this is introduction
        # that we don't need
        contents = re.split(section_re, flat_text,
                            flags=re.MULTILINE | re.VERBOSE)[1:]
        # Skip page if no abstracts were found
        if not contents:
            self.log('No abstracts found on: %s' % response.url,
                     level=log.WARNING)
            return
        for content in contents:
            if 'Abstract Withdrawn' in content:
                continue
            if 'Abstract not available' in content:
                continue
            # Remove header with next session info
            content = re.sub('(?:## )?SESSION.+', '', content,
                             flags=re.M | re.S)

            # Extract only non-empty lines
            non_empty_lines = filter(lambda x: x.strip() != '',
                                     content.split('\n'))
            if not non_empty_lines:
                continue
            title, = re.findall('\*\*(.+?)\*\*',
                                non_empty_lines[0])[:1] or ['']
            title = title.strip()
            content = '\n'.join(non_empty_lines[1:])
            # Remove "Back To Top" string
            content = content.replace('Back To Top', '')
            content = content.strip()

            yield AbstractItem(url=response.url, title=title, content=content,
                               symposium_name=symposium_name)

    def parse_abstracts_new(self, response):
        sel = scrapy.Selector(response)
        symposium_name, = sel.css('h1::text').extract()[:1] or ['']
        symposium_name = re.sub('.+?:', '', symposium_name, count=1)
        symposium_name = symposium_name.strip()
        content_els = sel.css(
            'a:contains("Hide Abstract") + div.expandIt, '
            'a:contains("Show Abstract") + div.expandIt'
        )
        # Skip page if no abstracts found
        if not content_els:
            self.log('no abstracts found on: %s' % response.url,
                     level=log.WARNING)
            return
        for el in content_els:
            title, = el.xpath(
                './preceding-sibling::h2[1]/following-sibling::p[1]/text()'
            ).extract()[:1] or ['']
            content = el.extract()
            content = remove_tags(content)
            if 'Abstract not available' in content:
                continue
            yield AbstractItem(url=response.url, title=title, content=content,
                               symposium_name=symposium_name)
