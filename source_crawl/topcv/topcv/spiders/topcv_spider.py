import scrapy
from pathlib import Path
from topcv.items import JobItem, ErrorItem
from topcv.utilities import gen_alias
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
import pymongo

import json, time
import uuid
import datetime 


class TopcvSpider(scrapy.Spider):
    name = "topcv_spider"
    allowed_domains = ["www.topcv.vn"]
    start_urls = ["https://www.topcv.vn"]

    global _source
    _source = "topcv"
    
    def __init__(self):
        settings = get_project_settings()
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection_error = db[settings['MONGODB_COLLECTION_ERROR']]

    def start_requests(self):
        try:

            settings = get_project_settings()
            urls = [
                settings['LINK_GET_JOB_TOPCV']
            ]
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)

        except Exception as e:      
            self.save_error_message(repr(e)) 
            
    def parse(self, response):
        try:
            res = json.loads(response.body)
            self.log("response status: ==========================")
            self.log(res["status"])
            if res["status"] == "success":
                jobs = res["jobs"]
                if jobs !=[]:
                    for jobItem in jobs:
                        self.log("job ---------- ")
                                        
                        
                        #self.job = jobItem
                        self.log(jobItem["url"]) 

                        #time.sleep(2)      # and add this line
                        yield scrapy.Request(url= jobItem["url"], callback=self.getjob_detail, meta={'job':jobItem})

        except Exception as e:      
            self.save_error_message(repr(e))             

    def getjob_detail(self, response):
        try:
            item = JobItem()
            #job = self.job
            # job = self.job_item
            job = response.meta['job']
            gender = response.xpath("//*[@class='box-general-content']/div[6]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            level = response.xpath("//*[@class='box-general-content']/div[2]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            quantity_recruitment = response.xpath("//*[@class='box-general-content']/div[4]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            working_form = response.xpath("//*[@class='box-general-content']/div[5]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            branch = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[1]/div[2]/a/text()").extract()
            area_working = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[2]/div[2]/span/a/text()").extract()

            
            item['id_record'] = job["id"]
            item['source'] = _source
            item['alias'] = gen_alias(_source, job["id"])                
            item['url']  = job["url"]
            item['position']  = job["title"]
            item['created_date'] = ""
            item['exp_date'] = job["deadline"]
            item['company_name'] = job["company"]["name"]
            item['company_description'] = ""
            item['working_address'] = job["address"]
            item['job_description'] = job["job_description"]
            item['job_position'] = job["title"]
            item['branch'] = branch
            item['skill_requirements'] = job["job_requirement"]
            item['benefit'] = job["job_benefit"]
            item['contract_type'] =  ""
            item['gender'] = gender
            item['working_area'] =  area_working
            item['current_level'] = ""
            item['desired_level'] = level
            item['experience'] = job["job_exp"]
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = job["salary"]
            item['level_of_readiness'] = job["is_hot"]
            item['number_of_vacancies'] = quantity_recruitment
            item['working_form'] = working_form

            create_date = datetime.datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')
            yield item

        except Exception as e:      
            self.save_error_message(repr(e))                 
        

    def save_error_message(self, error_message):
        item = ErrorItem()
        create_date = datetime.datetime.now()
        item['id_error'] = str(uuid.uuid4())
        item['source'] = _source
        item['error_message'] = error_message 
        item['created_date'] = create_date
        item['created_date_string'] = create_date.strftime('%d/%m/%Y')
        self.collection_error.insert_one(dict(item))
        return item