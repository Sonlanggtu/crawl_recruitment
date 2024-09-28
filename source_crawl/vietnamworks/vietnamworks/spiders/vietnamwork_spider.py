import scrapy
from pathlib import Path
from vietnamworks.items import JobItem, ErrorItem
#from vietnamworks import gen_alias
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
import pymongo

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import json, time
import uuid
import datetime 
import math, requests
from vietnamworks.utilities  import send_email

class VietnamworkSpider(scrapy.Spider):
    name = "vietnamwork_spider"
    allowed_domains = ["www.vietnamworks.com","ms.vietnamworks.com"]
    start_urls = ["ms.vietnamworks.com"]

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
            
            _page_number : int = 0  #get max page
            
            self.log(f"--- find max page number")
            url = f"https://ms.vietnamworks.com/job-search/v1.0/search"
            params = {"hitsPerPage": 100, "page": 0}
            response = requests.post(url, json=params, headers={'Content-Type': 'application/json; charset=UTF-8'})
            #self.log(f"response {response.status_code}")
            if response.status_code == 200 and response.json()['data'] != []:
                self.log(f"response status_code -- {response.status_code}")
                _page_number = int(response.json()['meta']['nbPages'])
                self.log(f"--- result max page number: {_page_number}")
            else:
                self.log(f"Error status_code: {response.status_code}")


            if _page_number != 0:
                _page_number = _page_number -1  # pagestop - 1 because pagestop start = 0
                for i in range(_page_number, 0, -1):  
                    self.log(i)
                    url = f"https://ms.vietnamworks.com/job-search/v1.0/search"
                    params = {"hitsPerPage": 100, "page": i}
                    self.log(f"------ PAGE: {i} ---- ")
                    time.sleep(0.5)
                    yield scrapy.Request( url, method='POST', 
                                    body=json.dumps(params), 
                                    headers={'Content-Type': 'application/json; charset=UTF-8'}, callback = self.parse)

     
            #old   
            # GET_NUMBER_PAGE = int(settings['GET_NUMBER_PAGE'])
            # self.log(f"------GET_NUMBER_PAGE: {GET_NUMBER_PAGE}")		
            # for i in range(0, GET_NUMBER_PAGE, 1):
            #     self.log(i)
            #     url = f"https://ms.vietnamworks.com/job-search/v1.0/search"
            #     params = {"hitsPerPage": 100, "page": i}
            #     self.log(f"------ PAGE: {i} ---- ")
            #     yield scrapy.Request( url, method='POST', 
            #                     body=json.dumps(params), 
            #                     headers={'Content-Type': 'application/json; charset=UTF-8'}, callback = self.parse)
                
        except Exception as e:      
            self.save_error_message(repr(e)) 
        

    def parse(self, response):
        try:
            #self.log("response json ----------")
            res = json.loads(response.body)
            #self.log(str(res))
            self.log("response httpcode:")
            http_code_res = res["meta"]["code"]
            self.log(str(http_code_res))
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
                    item['job_title']  = job["jobTitle"]
                    item['created_date'] = job["createdOn"]
                    item['exp_date'] = job["expiredOn"]
                    item['company_name'] = job["companyName"]
                    item['company_description'] = job["companyProfile"]
                    item['job_description'] = job["jobDescription"]
                    item['job_position'] = job["jobLevelVI"]
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
        #send_email("notification [spider vietnamwork] - [error]", str(repr(error_message))) 
        return item
