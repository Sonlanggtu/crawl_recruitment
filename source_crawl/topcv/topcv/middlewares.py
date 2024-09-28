# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
    
import time
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


# class TooManyRequestsRetryMiddleware(RetryMiddleware):
#         def __init__(self, crawler):
#             super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
#             self.crawler = crawler
    
#         @classmethod
#         def from_crawler(cls, crawler):
#             return cls(crawler)
    
#         def process_response(self, request, response, spider):
#             if request.meta.get('dont_retry', False):
#                 return response
#             elif response.status == 429:
#                 self.crawler.engine.pause()
#                 time.sleep(60) # If the rate limit is renewed in a minute, put 60 seconds, and so on.
#                 self.crawler.engine.unpause()
#                 reason = response_status_message(response.status)
#                 return self._retry(request, reason, spider) or response
#             elif response.status in self.retry_http_codes:
#                 reason = response_status_message(response.status)
#                 return self._retry(request, reason, spider) or response
#             return response 

class TopcvSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    # @classmethod
    # def from_crawler(cls, crawler):
    #     # This method is used by Scrapy to create your spiders.
    #     s = cls()
    #     crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
    #     return s
    
    # def __init__(self, crawler):
    #         super(TopcvSpiderMiddleware, self).__init__(crawler.settings)
    #         self.crawler = crawler
    
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler)
    
    # def process_response(self, request, response, spider):
    #     if request.meta.get('dont_retry', False):
    #         return response
    #     elif response.status == 429:
    #         self.crawler.engine.pause()
    #         time.sleep(60) # If the rate limit is renewed in a minute, put 60 seconds, and so on.
    #         self.crawler.engine.unpause()
    #         reason = response_status_message(response.status)
    #         return self._retry(request, reason, spider) or response
    #     elif response.status in self.retry_http_codes:
    #         reason = response_status_message(response.status)
    #         return self._retry(request, reason, spider) or response
    #     return response 

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class TopcvDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        print(f"request status is {request}")
        # Called for each request that goes through the downloader
        # middleware.
        proxy = spider.settings.get('PROXY')
        if proxy:
            request.meta['proxy'] = proxy

        max_retry_times = spider.settings.get('MAX_RETRY_TIMES')
        priority_adjust = spider.settings.get('PRIORITY_ADJUST')
        #print(f"max_retry_times req >> {max_retry_times}")
        #print(f"priority_adjust req >> {priority_adjust}")
        if max_retry_times:
            #request.meta['max_retry_times'] = max_retry_times
            self.max_retry_times = max_retry_times

        if priority_adjust:
            #request.meta['priority_adjust'] = priority_adjust
            self.priority_adjust = priority_adjust

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        print(f"response url {request.url} \nstatus is {response.status}")
        if response.status == 429:
            #self.crawler.engine.pause()
            time.sleep(6) # If the rate limit is renewed in a minute, put 200 seconds, and so on.

            reason = response_status_message(response.status)          
            return RetryMiddleware._retry(self, request, reason, spider)
        elif response.status == 403:
            #self.crawler.engine.pause()
            time.sleep(400) # If the rate limit is renewed in a minute, put 200 seconds, and so on.
        elif response.status == 400:
            #self.crawler.engine.pause()
            time.sleep(400) # If the rate limit is renewed in a minute, put 200 seconds, and so on.
        
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass
    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
