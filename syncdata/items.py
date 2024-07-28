# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ErrorItem(scrapy.Item):
    id_error = scrapy.Field()
    source = scrapy.Field()
    error_message = scrapy.Field()
    created_date = scrapy.Field()
    created_date_string = scrapy.Field()