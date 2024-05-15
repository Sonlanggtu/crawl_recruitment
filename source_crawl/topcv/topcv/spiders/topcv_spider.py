import scrapy
from pathlib import Path
from topcv.items import JobItem
from topcv.utilities import gen_alias
from scrapy.utils.project import get_project_settings

import json
import uuid

class TopcvSpider(scrapy.Spider):
    name = "topcv_spider"
    allowed_domains = ["www.topcv.vn"]
    start_urls = ["https://www.topcv.vn"]

    def start_requests(self):
        urls = [
            "https://www.topcv.vn/api-featured-jobs?limit=10&city=0&salary=&exp=&category="
            #"https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

       # self.logger("response.body dsads")
        res = json.loads(response.body)
        self.log("response status: ==========================")
        self.log(res["status"])
        #self.log(res["jobs"][1]["company"])
        if res["status"] == "success":
           
           jobs = res["jobs"]
           if jobs !=[]:
               for job in jobs:
                   item = JobItem()
                   
                   source = "topcv"
                   item['id'] = str(uuid.uuid4())
                   item['id_record'] = job["id"]
                   item['source'] = source
                   item['alias'] = gen_alias(source, job["id"])                

                   item['url']  = job["url"]
                   item['position']  = job["title"]
                   item['created_date'] = "" #res[""]
                   item['exp_date'] = job["deadline"]
                   item['name_company'] = job["company"]["name"]
                   item['description_company'] = ""
                   item['address_working'] = job["address"]
                   item['description_job'] = job["job_description"]
                   item['position_job'] = job["title"]
                   item['group_job'] = ""
                   item['requirement'] = job["job_requirement"]
                   item['benefit'] = job["job_benefit"]
                   item['contract_type'] =  "" #res[""]
                   item['gender'] = ""
                   item['locaion'] =  job["short_cities"]
                   item['position_presentation'] = "" #job[""]
                   item['position_expect'] = ""
                   item['experience'] = job["job_exp"]
                   item['skill'] = "" #job[""]
                   item['group_job_priority'] = ""  #job[""]
                   item['salary'] = job["salary"]
                   item['is_ready_working'] = job["is_hot"]
                   

                   #self.log(item['salary'])
                   yield item

        
