import re

import scrapy
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
    current_csv_no = 5000

    def __start_requests(self):
        #yield scrapy.Request('http://www.mrs.org/spring-1998-abstract-f/', self.parse_abstract_old)
        yield scrapy.Request('http://www.mrs.org/spring-1998-abstract-e/', self.parse_abstract_old)
        yield scrapy.Request('http://www.mrs.org/spring-1999-abstract-a/', self.parse_abstract_old)
        yield scrapy.Request('http://www.mrs.org/s07-abstract-g/', self.parse_abstract_old)

    rules = (
        Rule(
            LinkExtractor(
                allow='\d{4}',  # Year must be present
                #allow='spring1998',
                restrict_xpaths=[
                    css2xpath('.title a'),
                    css2xpath('#pastMeetings h3 a')
                ],
            )
        ),
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
            callback='parse_abstract_old',
        )
    )

    def parse_abstract_old(self, response):
        sel = scrapy.Selector(response)

        # Extract title from <title> tag
        title, = sel.css('title::text').extract()[:1] or ['']
        title = title.strip()
        column = '\n'.join(sel.css('div#contentCol').extract())

        h = HTML2Text()

        # Remove newline chars that are make no sense in HTML (only <br> do)
        flat_text = re.sub(r'[\n\r]+', '', column, flags=re.M)

        flat_text = h.handle(flat_text)
        # Remove all HTML tags, but keeps <br>
        flat_text = remove_tags(flat_text, keep=('br',))
        # Replace <br> with newline character
        flat_text = flat_text.replace('<br>', '\n')

        # Each abstract start with hour and abstract no.
        time_re = r'\d+:\d+ [AP]M [A-Z\d\.\*]+\S+'
        # Regex to remove SESSION *** headers
        header_re = r'SESSION [\w\d]+:.+?(%s)' % time_re

        flat_text = re.sub(header_re, r'\n\n\1', flat_text, flags=re.M | re.S)

        #print flat_text

        # Split flat text. The separator is hour with abstract no
        for content in re.split(time_re, flat_text, flags=re.M)[1:]:
            c = content
            # Remove first line of abstract
            not_empty_lines = filter(lambda x: x.strip() != '', content.split('\n'))
            content = '\n'.join(not_empty_lines[1:])
            # We have single abstract here
            content = content.replace('Back To Top', '')
            content = content.strip()
            # if 'Abstract not available' in content:
            #     print c.split('\n')
            if re.search('^.{,20}[A-Z]{8,}|SESSION', content):
                print '======\n%s\n' % response.url
                print (content)
            yield AbstractItem(url=response.url, title=title, content=content)
