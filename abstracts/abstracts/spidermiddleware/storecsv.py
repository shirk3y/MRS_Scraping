import csv

from abstracts.items import AbstractItem


class StoreCsvMiddleware(object):

    current_csv_no = 5000

    def process_spider_output(self, response, spider, result):
        result = list(result)
        if any([isinstance(r, AbstractItem) for r in result]):
            with open('MRS%04d.csv' % self.current_csv_no, 'w') as csv_file:
                writer = csv.writer(csv_file, dialect='excel-tab')
                for r in result:
                    if isinstance(r, AbstractItem):
                        writer.writerow([r['url'], r['title'].encode('utf-8'),
                                         r['content'].encode('utf-8')])
        return result
