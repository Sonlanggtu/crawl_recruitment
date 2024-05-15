# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    id = scrapy.Field()
    source = scrapy.Field()
    alias = scrapy.Field()
    id_record = scrapy.Field()

    url = scrapy.Field()
    position = scrapy.Field()
    created_date = scrapy.Field()
    exp_date = scrapy.Field()
    name_company = scrapy.Field()
    description_company = scrapy.Field()
    address_working = scrapy.Field()
    description_job = scrapy.Field()
    position_job = scrapy.Field()
    group_job = scrapy.Field()
    requirement = scrapy.Field()
    benefit = scrapy.Field()
    contract_type = scrapy.Field()
    gender = scrapy.Field()
    locaion = scrapy.Field()
    position_presentation = scrapy.Field()
    position_expect = scrapy.Field()
    experience = scrapy.Field()
    skill = scrapy.Field()
    group_job_priority = scrapy.Field()
    salary = scrapy.Field()
    is_ready_working = scrapy.Field()
