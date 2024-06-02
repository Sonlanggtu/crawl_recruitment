import scrapy
from pathlib import Path
from jobsgo.items import  JobItem, ErrorItem
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
import pymongo
import re
import json, time
import uuid
import datetime 
import json
import requests

class JobsgoSpiderSpider(scrapy.Spider):
    name = "jobsgo_spider"
    allowed_domains = ["jobsgo.vn"]
    start_urls = ["https://jobsgo.vn"]

    global _source
    _source = "jobsgo"

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
            GET_NUMBER_PAGE = settings['GET_NUMBER_PAGE']
            print(f"-------------- GET_NUMBER_PAGE: {GET_NUMBER_PAGE}")
            for page in range(0, GET_NUMBER_PAGE, 1):
                if page == 1:
                    continue
                url = f"https://jobsgo.vn/viec-lam.html?page={page}&sort=created"
                print(f"------------ get page : {page} ----------")
                yield scrapy.Request(url=url, callback=self.get_link_jobs)

        except Exception as e:      
            self.save_error_message(repr(e))   

    def get_link_jobs(self, response):
        try:
            #print(f"------------ get_link_jobs {response.request.url} ----------")
            link_jobs = response.xpath("//div[@class='brows-job-position']/h3/a/@href").extract()
            print(f"------------ get_link_jobs detail: {link_jobs} ----------")
            for link in link_jobs:
                yield scrapy.Request(url=link, callback=self.get_job_detail)

        except Exception as e:      
            self.save_error_message(repr(e))     


    def get_job_detail(self, response):
        try:
            print(f"------------ get_job_detail {response.request.url}----------")

            res = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
            res = json.loads(res)
            print(res) ## get detail job

            item = JobItem()
            

            list_property_job = response.xpath("//div[@class='panel-body']/div[@class='row']/div").extract()
            gender = "";  exprience = ""
            statments = range(len(list_property_job))
            for statment in statments:
                if "Ngày đăng tuyển" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()

                elif "Vị trí/chức vụ" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()

                elif  "Yêu cầu bằng cấp" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()

                elif  "Yêu cầu kinh nghiệm" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()
                    exprience = context

                elif  "Yêu cầu độ tuổi" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()

                # elif  "Yêu cầu ngôn ngữ" in list_property_job[statment]: 
                #     path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                #    context = response.xpath(path).extract_first()

                elif  "Yêu cầu giới tính" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()
                    gender = context


            title = response.xpath("/html/head/meta[@property='og:title']/@content").extract_first()
            salary = response.xpath("//span[@class='saraly text-bold text-green']/text()").extract_first()

            arr_address_working = []
            for location in res["jobLocation"]:
                arr_address_working.append(location["address"]["streetAddress"])
            url = response.request.url
            item['working_address'] = arr_address_working
            id = url.replace(".html", "").split('-')[-1]
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url
            item['position']  = title
            item['created_date'] = res["datePosted"]
            item['exp_date'] = res["validThrough"]
            item['company_name'] = res["hiringOrganization"]["name"]
            item['company_description'] = res["employerOverview"]       
            item['job_description'] = res["description"]
            item['job_position'] = title
            item['branch'] = res["industry"]
            item['skill_requirements'] = res["description"]
            item['benefit'] = res["jobBenefits"]
            item['contract_type'] =  ""
            item['gender'] = gender
            item['working_area'] = res["applicantLocationRequirements"]["name"]
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = exprience
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = salary
            item['level_of_readiness'] = ""
            item['number_of_vacancies'] = ""
            item['working_form'] = res["employmentType"]

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
