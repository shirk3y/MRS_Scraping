from scrapy.exceptions import IgnoreRequest


class IgnorePdfMiddleware(object):
    def process_response(self, request, response, spider):
        content_type = response.headers.get('content-type', None)
        if content_type and 'pdf' in content_type:
            raise IgnoreRequest('No PDF files allowed')
        return response
