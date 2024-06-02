import scrapy
from pathlib import Path
from vietnamworks.items import JobItem, ErrorItem
#from vietnamworks import gen_alias
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
import pymongo

import json, time
import uuid
import datetime 
import math


class VietnamworkSpider(scrapy.Spider):
    name = "vietnamwork_spider"
    allowed_domains = ["www.vietnamworks.com"]
    start_urls = ["https://www.vietnamworks.com"]

    global _source
    _source = "vietnamwork"  

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
            GET_NUMBER_PAGE = int(settings['GET_NUMBER_PAGE'])
            self.log(f"------GET_NUMBER_PAGE: {GET_NUMBER_PAGE}")

            for i in range(0, GET_NUMBER_PAGE, 1):
                print(i)
                url = f"https://ms.vietnamworks.com/job-search/v1.0/search"
                params = {"hitsPerPage": 100, "page": i}
                self.log(f"------ PAGE: {i} ---- ")
                yield scrapy.Request( url, method='POST', 
                                body=json.dumps(params), 
                                headers={'Content-Type': 'application/json; charset=UTF-8'}, callback = self.parse)
                
        except Exception as e:      
            self.save_error_message(repr(e)) 
        

    def parse(self, response):
        try:
            #print("response json ----------")
            res = json.loads(response.body)
            #print(str(res))
            print("response httpcode:")
            http_code_res = res["meta"]["code"]
            print(str(http_code_res))
            if http_code_res == 200:
                jobs = res["data"]
                for job in jobs:
                    self.log("job ---------- ")  
                    item = JobItem()
                    arrBenefits = []
                    for benefit in job["benefits"]:
                        arrBenefits.append(benefit["benefitNameVI"])
                    
                    arrSkills = []
                    for arrSkill in job["skills"]:
                        arrSkills.append(arrSkill["skillName"])

                    arr_address_working = []
                    for address_working in job["workingLocations"]:
                        arr_address_working.append(address_working["address"])

                    item['benefit'] = arrBenefits
                    item['skill'] = arrSkills
                    item['working_address'] = arr_address_working
                    id = job["jobId"]
                    item['id_record'] = id
                    item['source'] = _source
                    item['alias'] = str(f"{_source}_{id}")              
                    item['url']  = job["jobUrl"]
                    item['position']  = job["jobTitle"]
                    item['created_date'] = job["createdOn"]
                    item['exp_date'] = job["expiredOn"]
                    item['company_name'] = job["companyName"]
                    item['company_description'] = job["companyProfile"]
                    item['job_description'] = job["jobDescription"]
                    item['job_position'] = job["jobTitle"]
                    item['branch'] = job["jobFunction"]["parentName"]
                    item['skill_requirements'] = job["jobRequirement"]
                    item['contract_type'] =  ""
                    item['working_area'] =  job["workingLocations"][0]["cityNameVI"]
                    item['current_level'] = ""
                    item['desired_level'] = ""
                    item['job_group_priority'] = "" 
                    item['salary'] = job["prettySalary"]
                    item['level_of_readiness'] = job["isUrgentJobM"]
                    item['number_of_vacancies'] = ""
                    item['working_form'] = ""
                    if job["isShowGender"] == 0:
                        item['gender'] = "Không hiển thị"
                    else:
                        item['gender'] = ""
                    if job["yearsOfExperience"] == 0 or job["yearsOfExperience"] == -1:
                        item['experience'] = 0
                    else:
                        item['experience'] = job["yearsOfExperience"] 

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

