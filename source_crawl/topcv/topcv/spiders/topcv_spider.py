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
    start_urls = ["www.topcv.vn"]

    global _source
    _source = "topcv"
    #_numberjob = 0
    
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
            print(f"-------------- GET_NUMBER_PAGE : {GET_NUMBER_PAGE}")
            for page in range(51, GET_NUMBER_PAGE + 1, 1):
                #time.sleep(5)
                url = f"https://www.topcv.vn/tim-viec-lam-moi-nhat?sort=new&page={page}"
                
                #print(f"------------ url: {url}----------")
                yield scrapy.Request(url=url, callback=self.get_link_job_xpath)
           
            #yield scrapy.Request(url='https://www.topcv.vn/viec-lam/ky-su-thiet-ke-dien/1408990.html', callback=self.parse)
            

        except Exception as e:
            print(repr(e))      
            self.save_error_message(repr(e)) 
            
    def get_link_job_xpath(self, response):
        try:
            

            print(f"------------ get_link_page {response.request.url} ")

            print(f"------------ get_link_page_status {response.status} ")

            # if(response.status == 429):
            #     time.sleep(60)

            time.sleep(5)
            linkJobs = response.xpath("//*[@class='wrapper-content']//div[1]/div[1]/div/div/div[2]/div[1]/div/div[1]/h3/a/@href").extract()
            for linkjob in linkJobs:
                
                print(linkjob)
                #time.sleep(3)      # and add this line
                yield scrapy.Request(url= linkjob, callback=self.getjob_detail)

            #yield scrapy.Request(url= linkJobs[0], callback=self.getjob_detail)

            
            # with open('crawl.html', 'w') as f:
            #    f.write(listJob)

            # res = json.loads(response.body)
            # self.log("response status: ==========================")
            # self.log(res["status"])
            # if res["status"] == "success":
            #     jobs = res["jobs"]
            #     if jobs !=[]:
            #         for jobItem in jobs:
            #             self.log("job ---------- ")
                                        
                        
            #             #self.job = jobItem
            #             self.log(jobItem["url"]) 

            #             #time.sleep(2)      # and add this line
            #             yield scrapy.Request(url= jobItem["url"], callback=self.getjob_detail, meta={'job':jobItem})

        except Exception as e:      
            self.save_error_message(repr(e))

    def getjob_detail(self, response):
        try:
            print(f"------------ get_link_job_detail: {response.request.url} ")
            time.sleep(5)
            json_result = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
            job = json.loads(json_result)
            #print(job)

            item = JobItem()
            #job = self.job
            # job = self.job_item
            #job = response.meta['job']
            gender = response.xpath("//*[@class='box-general-content']/div[6]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            level = response.xpath("//*[@class='box-general-content']/div[2]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            quantity_recruitment = response.xpath("//*[@class='box-general-content']/div[4]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            working_form = response.xpath("//*[@class='box-general-content']/div[5]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            branch = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[1]/div[2]/a/text()").extract()
            area_working = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[2]/div[2]/span/a/text()").extract()
            experience = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[2]/div/div[3]/div[2]/div[2]").extract_first()
            id = response.xpath("//*[@name='job_report_job_id']/@value").extract_first() 
            time_dealine = response.xpath("//*[@id='box-job-information-detail']/div[3]/div[2]/text()").extract_first() 

            working_address = response.xpath("//*[@id='box-job-information-detail']/div[2]/div/div[4]/div/div/text()").extract_first() 
            skill_requirements = response.xpath("//*[@id='box-job-information-detail']/div[2]/div/div[2]/div").extract_first() 
            salary = response.xpath("//*[@id='header-job-info']/div[1]/div[1]/div[2]/div[2]/text()").extract_first() 

            item['id_record'] = job["identifier"]["value"]
            item['source'] = _source
            item['alias'] = gen_alias(_source, id)                
            item['url']  = response.request.url
            item['job_title']  = job["title"]
            item['created_date'] = job["datePosted"]
            item['exp_date'] = time_dealine
            item['company_name'] = job["hiringOrganization"]["name"]
            item['company_description'] = ""
            item['working_address'] = working_address
            item['job_description'] = job["employerOverview"]
            item['job_position'] = job["occupationalCategory"]
            item['branch'] = branch
            item['skill_requirements'] = skill_requirements
            item['benefit'] = job["jobBenefits"]
            item['contract_type'] =  ""
            item['gender'] = gender
            item['working_area'] =  area_working
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = experience #job["experienceRequirements"]["monthsOfExperience"]
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = salary
            item['level_of_readiness'] = ""
            item['number_of_vacancies'] = quantity_recruitment
            item['working_form'] = working_form

            create_date = datetime.datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')
            yield item

        except Exception as e:      
            self.save_error_message(repr(e))                    

    # def getjob_detail_json(self, response):
    #     try:
    #         item = JobItem()
    #         #job = self.job
    #         # job = self.job_item
    #         job = response.meta['job']
    #         gender = response.xpath("//*[@class='box-general-content']/div[6]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
    #         level = response.xpath("//*[@class='box-general-content']/div[2]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
    #         quantity_recruitment = response.xpath("//*[@class='box-general-content']/div[4]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
    #         working_form = response.xpath("//*[@class='box-general-content']/div[5]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
    #         branch = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[1]/div[2]/a/text()").extract()
    #         area_working = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[2]/div[2]/span/a/text()").extract()

            
    #         item['id_record'] = job["id"]
    #         item['source'] = _source
    #         item['alias'] = gen_alias(_source, job["id"])                
    #         item['url']  = job["url"]
    #         item['position']  = job["title"]
    #         item['created_date'] = ""
    #         item['exp_date'] = job["deadline"]
    #         item['company_name'] = job["company"]["name"]
    #         item['company_description'] = ""
    #         item['working_address'] = job["address"]
    #         item['job_description'] = job["job_description"]
    #         item['job_position'] = job["title"]
    #         item['branch'] = branch
    #         item['skill_requirements'] = job["job_requirement"]
    #         item['benefit'] = job["job_benefit"]
    #         item['contract_type'] =  ""
    #         item['gender'] = gender
    #         item['working_area'] =  area_working
    #         item['current_level'] = ""
    #         item['desired_level'] = level
    #         item['experience'] = job["job_exp"]
    #         item['skill'] = ""
    #         item['job_group_priority'] = "" 
    #         item['salary'] = job["salary"]
    #         item['level_of_readiness'] = job["is_hot"]
    #         item['number_of_vacancies'] = quantity_recruitment
    #         item['working_form'] = working_form

    #         create_date = datetime.datetime.now()
    #         #yesterday = datetime.now() - datetime.timedelta(1)
    #         item['created_date_crawl_job'] = create_date
    #         item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')
    #         yield item

    #     except Exception as e:      
    #         self.save_error_message(repr(e))                 
        

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