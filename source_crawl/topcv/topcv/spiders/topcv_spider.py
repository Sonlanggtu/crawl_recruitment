import scrapy
from pathlib import Path
from topcv.items import JobItem
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
    
    def start_requests(self):
        settings = get_project_settings()
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

        urls = [
            settings['LINK_GET_JOB_TOPCV']
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #global job
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
                   

    def getjob_detail(self, response):
        item = JobItem()
        source = "topcv"

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
        item['source'] = source
        item['alias'] = gen_alias(source, job["id"])                
        item['url']  = job["url"]
        item['position']  = job["title"]
        item['created_date_post'] = ""
        item['exp_date'] = job["deadline"]
        item['name_company'] = job["company"]["name"]
        item['description_company'] = ""
        item['address_working'] = job["address"]
        item['description_job'] = job["job_description"]
        item['position_job'] = job["title"]
        item['branch'] = branch
        item['requirement'] = job["job_requirement"]
        item['benefit'] = job["job_benefit"]
        item['contract_type'] =  ""
        item['gender'] = gender
        item['area_working'] =  area_working
        item['position_presentation'] = ""
        item['position_expect'] = level
        item['experience'] = job["job_exp"]
        item['skill'] = ""
        item['group_job_priority'] = "" 
        item['salary'] = job["salary"]
        item['is_ready_working'] = job["is_hot"]
        item['quantity_recruitment'] = quantity_recruitment
        item['working_form'] = working_form
        item['created_date_crawl_job'] = datetime.datetime.now()   
        yield item
                        
        
