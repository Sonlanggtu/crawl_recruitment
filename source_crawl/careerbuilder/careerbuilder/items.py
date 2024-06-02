# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    #id = scrapy.Field()
    source = scrapy.Field()
    alias = scrapy.Field()
    id_record = scrapy.Field()

    url = scrapy.Field()
    position = scrapy.Field()
    created_date = scrapy.Field()
    exp_date = scrapy.Field()
    company_name = scrapy.Field()
    company_description = scrapy.Field()
    working_address = scrapy.Field()
    job_description = scrapy.Field()
    job_position = scrapy.Field()
    branch = scrapy.Field()
    skill_requirements = scrapy.Field()
    benefit = scrapy.Field()
    contract_type = scrapy.Field()
    gender = scrapy.Field()
    working_area = scrapy.Field()
    current_level = scrapy.Field()
    desired_level = scrapy.Field()
    experience = scrapy.Field()
    skill = scrapy.Field()
    job_group_priority = scrapy.Field()
    salary = scrapy.Field()
    level_of_readiness = scrapy.Field()
    number_of_vacancies = scrapy.Field()
    working_form = scrapy.Field()
    created_date_crawl_job = scrapy.Field()
    created_date_crawl_job_string = scrapy.Field()

class ErrorItem(scrapy.Item):
    id_error = scrapy.Field()
    source = scrapy.Field()
    error_message = scrapy.Field()
    created_date = scrapy.Field()
    created_date_string = scrapy.Field()