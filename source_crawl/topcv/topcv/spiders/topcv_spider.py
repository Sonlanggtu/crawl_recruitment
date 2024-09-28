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
from topcv.utilities  import send_email
import re, html
from scrapy.selector import Selector

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
            #GET_NUMBER_PAGE = int(settings['GET_NUMBER_PAGE'])
            #self.log(f"-------------- GET_NUMBER_PAGE : {GET_NUMBER_PAGE}")


            page_number = 2 # max page is 200
            self.log(f"-------------- GET_PAGE_NUMBER : {page_number}")
            for page in range(page_number, 0, -1):
                #time.sleep(5)
                url = f"https://www.topcv.vn/tim-viec-lam-moi-nhat?sort=new&page={page}"
                
                #self.log(f"------------ url: {url}----------")
                time.sleep(1)
                yield scrapy.Request(url=url, callback=self.get_link_job_xpath)
            

            # yield scrapy.Request(url='https://www.topcv.vn/brand/trung-tam-anh-ngu-ila/tuyen-dung/nhan-vien-tu-van-tuyen-sinh-educational-planner-ila-khu-vuc-binh-duong-thu-nhap-hap-dan-j1359938.html?ta_source=JobBrandSameCompany_LinkDetail&jr_i=rule-based-v0%3A%3A1724245493723%3A%3A1359938%3A%3A5',
            #                       callback=self.getjob_detail)
            

        except Exception as e:
            self.log(repr(e))      
            self.save_error_message(repr(e)) 
            
    def get_link_job_xpath(self, response):
        try:
            
            self.log(f"------------ get_link_page {response.request.url} ")

            self.log(f"------------ get_link_page_status {response.status} ")

            # if(response.status == 429):
            #     time.sleep(60)

            #time.sleep(1)
            linkJobs = response.xpath("//*[@class='wrapper-content']//div[1]/div[1]/div/div/div[2]/div[1]/div/div[1]/h3/a/@href").extract()
            self.log(f"length linkJobs >> {len(linkJobs)}")
            for linkjob in linkJobs:
                
                self.log(linkjob)
                #time.sleep(6)      # and add this line
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
            urlRequest = response.request.url
            self.log(f"------------ get_link_job_detail: {response.request.url} ")

            if re.search("/viec-lam/", urlRequest):
                self.log(f"{urlRequest} in type -- viec lam")
                yield self.getjob_detail_vieclam(response)
            elif re.search("/brand/", urlRequest):
                self.log(f"{urlRequest} in type -- brand")
                yield self.get_type_brand(response)
            else:
                self.log(f"{urlRequest} no type")

        except Exception as e:      
            self.save_error_message(repr(e))

    def getjob_detail_vieclam(self, response):    
        try:
            self.log(f"------------ getjob_detail_vieclam: {response.request.url} ")

            #time.sleep(0.3)
            json_result = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
            job = json.loads(json_result)
            #self.log(job)

            item = JobItem()
            #job = self.job
            # job = self.job_item
            #job = response.meta['job']
            gender = response.xpath("//*[@class='box-general-content']/div[6]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            level = "" #response.xpath("//*[@class='box-general-content']/div[2]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            quantity_recruitment = response.xpath("//*[@class='box-general-content']/div[4]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            working_form = response.xpath("//*[@class='box-general-content']/div[5]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            
            list_property_job = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div").extract()

            branch = ""
            area_working = ""
            #self.log("--------------job_property")
            self.log(len(list_property_job))
            for job_property in list_property_job:
                #self.log(html.unescape(job_property))
                header_field = Selector(text=job_property).xpath("//div[1]/div[1]/text()").extract_first()
                #self.log("header_field")
                #self.log(header_field)
                path_context = f"//div[1]/div[2]/a/text()"

                if "Ngành nghề" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract()
                    #self.log(context)
                    branch = context

                elif "Khu vực" in header_field: 
                    path_context = f"//div[1]/div[2]/span/a/text()"
                    context = Selector(text=job_property).xpath(path_context).extract()
                    #self.log(context)
                    area_working = context

                elif "Kỹ năng cần có" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract()
                    #self.log(context)
            
            #branch = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[1]/div[2]/a/text()").extract()
            #area_working = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[3]/div[2]/div[2]/span/a/text()").extract()
            experience = response.xpath("//*[@id='job-detail']/div[3]/div/div[2]/div[2]/div/div[3]/div[2]/div[2]/text()").extract_first()
            id = response.xpath("//*[@name='job_report_job_id']/@value").extract_first() 
            time_dealine =  job['validThrough']  #response.xpath("//*[@id='box-job-information-detail']/div[3]/div[2]/text()").extract_first() 

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

            if branch:
                item['branch'] = branch
            else:
                item['branch'] = ""
            item['skill_requirements'] = skill_requirements
            item['benefit'] = job["jobBenefits"]
            item['contract_type'] =  ""
            item['gender'] = gender
            
            if area_working:
                item['working_area'] = area_working
            else:
                item['working_area'] = ""
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
            return item

        except Exception as e:      
            self.save_error_message(repr(e))

    def get_type_brand(self, response):
        try:
            self.log(f"------------ getjob_detail_brand: {response.request.url} ")

            #time.sleep(1)
            brand_type = response.xpath("//div[@class='box-job-info']").extract_first()
            #self.log(brand_type) 
            if brand_type:
                self.log("brand type 1")  #ex https://www.topcv.vn/brand/vpbank/tuyen-dung/chuyen-vien-quan-he-khach-hang-doanh-nghiep-vi-mo-yen-lang-dong-da-j1446925.html?ta_source=JobSearchList_LinkDetail&u_sr_id=qaSvqkoQili6N8TVSMPJZT6DvxCGiwmuFmqBZPQW_1724259049
                return self.getjob_detail_brand_type_1(response)
            else:
                self.log("brand type 2") #https://www.topcv.vn/brand/trung-tam-anh-ngu-ila/tuyen-dung/chuyen-vien-tu-van-tuyen-sinh-kinh-doanh-sales-consultant-thu-nhap-len-den-30-trieu-ila-quan-7-quan-4-quan-8-j1446654.html?ta_source=JobSearchList_LinkDetail&u_sr_id=qaSvqkoQili6N8TVSMPJZT6DvxCGiwmuFmqBZPQW_1724259049
                return self.getjob_detail_brand_type_2(response)

        except Exception as e:      
            self.save_error_message(repr(e))

    def getjob_detail_brand_type_1(self, response):
        try:
            self.log(f"------------ getjob_detail_brand_type_1: {response.request.url} ")

            #time.sleep(0.3)
            json_result = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
            job = json.loads(json_result)
            #self.log(job)

            item = JobItem()
            #job = self.job
            # job = self.job_item
            #job = response.meta['job']
            gender = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[5]/div[2]/span/text()").extract_first()
            #level = response.xpath("//*[@class='box-general-content']/div[2]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            quantity_recruitment = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/span/text()").extract_first()
            working_form = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[3]/div[2]/span/text()").extract_first()
            branch = ""
            area_working = ""
            experience = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[6]/div[2]/span/text()").extract_first()
            id = response.xpath("//*[@name='job_report_job_id']/@value").extract_first() 
            time_dealine = job['validThrough'] 
            working_address = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[2]/div/text()").extract_first() 
            skill_requirements = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[4]/div").extract_first() 
            salary = response.xpath("//*[@id='main']/div[1]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[1]/div[2]/span/text()").extract_first() 

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

            if branch:
                item['branch'] = branch
            else:
                item['branch'] = ""
            item['skill_requirements'] = skill_requirements
            item['benefit'] = job["jobBenefits"]
            item['contract_type'] =  ""
            item['gender'] = gender
            
            if area_working:
                item['working_area'] = area_working
            else:
                item['working_area'] = ""
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
            return item

        except Exception as e:      
            self.save_error_message(repr(e))

    def getjob_detail_brand_type_2(self, response):
        try:
            self.log(f"------------ getjob_detail_brand_type_2: {response.request.url} ")

            #time.sleep(0.3)
            json_result = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
            job = json.loads(json_result)
            #self.log(job)

            item = JobItem()
            #job = self.job
            # job = self.job_item
            #job = response.meta['job']
            gender = response.xpath("//*[@id='premium-job']/div[2]/div[2]/div[1]/div/div[4]/div[2]/div[2]/text()").extract_first()
            #level = response.xpath("//*[@class='box-general-content']/div[2]/div[@class='box-general-group-info']/div[@class='box-general-group-info-value']/text()").extract_first()
            quantity_recruitment = response.xpath("//*[@id='premium-job']/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[2]/text()").extract_first()
            working_form = response.xpath("//*[@id='premium-job']/div[2]/div[2]/div[1]/div/div[3]/div[2]/div[2]/text()").extract_first()

            branch = response.xpath("//*[@id='premium-job']/div[2]/div[2]/div[3]/div[1]/div/span/a/text()").extract()
            area_working = response.xpath("//*[@id='premium-job']/div[2]/div[2]/div[3]/div[2]/div/span/a/text()").extract()
            id = response.xpath("//*[@name='job_report_job_id']/@value").extract_first() 
            time_dealine = job['validThrough'] 
            working_address = response.xpath("//*[@id='premium-job']/div[2]/div[1]/div[1]/div[3]/div[4]").extract_first() 

            salary = ""
            experience = ""
            haveFlalshJob = response.xpath("//div[@class='premium-job-basic-information']/div[@class='tag-job-flash']/@data-job-id").extract_first()
            if haveFlalshJob:
                salary = response.xpath("//*[@id='premium-job']/div[2]/div[1]/div[1]/div[1]/div[2]/div/div[1]/div[2]/div[2]/text()").extract_first()
                experience = response.xpath("//*[@id='premium-job']/div[2]/div[1]/div[1]/div[1]/div[2]/div/div[3]/div[2]/div[2]/text()").extract_first()
            else:
                salary = response.xpath("//*[@id='premium-job']/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/text()").extract_first()
                experience = response.xpath("//*[@id='premium-job']/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[3]/div[2]/div[2]/text()").extract_first()
                

            skill_requirements = response.xpath("//*[@id='premium-job']/div[2]/div[1]/div[1]/div[3]/div[2]").extract_first() 
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

            if branch:
                item['branch'] = branch
            else:
                item['branch'] = ""
            item['skill_requirements'] = skill_requirements
            item['benefit'] = job["jobBenefits"]
            item['contract_type'] =  ""
            item['gender'] = gender
            
            if area_working:
                item['working_area'] = area_working
            else:
                item['working_area'] = ""
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
            return item

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
        #send_email("notification [spider topcv] - [error]", str(repr(error_message))) 
        return item