import re

import scrapy
from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from w3lib.html import remove_tags

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

    def parse_abstracts_old(self, response):
        sel = scrapy.Selector(response)
        title = self._get_title(sel)
        column = '\n'.join(sel.css('div#contentCol').extract())
        # Remove newline chars that are make no sense in HTML (only <br> do)
        flat_text = re.sub(r'[\n\r]+', '', column, flags=re.M)
        # Remove tags
        flat_text = remove_tags(flat_text, keep=('br'))
        # Convert <br> to LF
        flat_text = re.sub('<br\s*/?>', '\n', flat_text)
        # Each abstract starts with hour and abstract no.
        section_re = r'(?:\d+:\d+ [AP]M )?\s*[\*A-Z/]+\d+\.\d+?.*'
        # Split it. The separator is hour with abstract number
        # Also skip first element, because this is introduction
        # that we don't need
        contents = re.split(section_re, flat_text, flags=re.M)[1:]
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

            # Remove first line of abstract (author list)
            non_empty_lines = filter(lambda x: x.strip() != '',
                                     content.split('\n'))
            content = '\n'.join(non_empty_lines[1:])
            # Remove "Back To Top" string
            content = content.replace('Back To Top', '')
            content = content.strip()

            yield AbstractItem(url=response.url, title=title, content=content)

    def parse_abstracts_new(self, response):
        sel = scrapy.Selector(response)
        title = self._get_title(sel)
        contents = sel.css(
            'a:contains("Hide Abstract") + div.expandIt, '
            'a:contains("Show Abstract") + div.expandIt'
        ).extract()
        # Skip page if no abstracts found
        if not contents:
            self.log('no abstracts found on: %s' % response.url,
                     level=log.WARNING)
            return
        for content in contents:
            content = remove_tags(content)
            yield AbstractItem(url=response.url, title=title, content=content)

    def _get_title(self, sel):
        title, = sel.css('title::text').extract()[:1] or ['']
        return title.strip()
