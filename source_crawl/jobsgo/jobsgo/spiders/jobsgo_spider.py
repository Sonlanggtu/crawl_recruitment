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
from jobsgo.utilities  import send_email
from scrapy.http import HtmlResponse

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
            self.log(f"-------------- GET_NUMBER_PAGE: {GET_NUMBER_PAGE}")
            max_page = 0

            url_first = f"https://jobsgo.vn/viec-lam.html?page=1000&sort=created"
            response = requests.get(url_first, headers={'Content-Type': 'application/json; charset=UTF-8'})

            responseHtml = HtmlResponse(url=url_first, body=response.text, encoding='utf-8')
            max_page = int(responseHtml.xpath("//ul[@class='pagination']/li[@class='active']/a/text()").extract_first())
            self.log(f"result max page: {max_page}")

            #max_page = 2
            # crawl job at page filter
            if max_page != 0:
                for page in range(max_page, 0, -1):
                    if page == 1:
                        continue
                    url = f"https://jobsgo.vn/viec-lam.html?page={page}&sort=created"
                    self.log(f"------------ get page : {page} ----------")
                    #time.sleep(1)
                    yield scrapy.Request(url=url, callback=self.get_link_jobs)
            else:
                self.log("get max page = 0")
            
            #crawl job at page Home
            url = f"https://jobsgo.vn/"
            self.log(f"------------ get page: home ----------")
            yield scrapy.Request(url=url, callback=self.get_link_jobs_home)


            # old flow
            # for page in range(0, GET_NUMBER_PAGE, 1):
            #     if page == 1:
            #         continue
            #     url = f"https://jobsgo.vn/viec-lam.html?page={page}&sort=created"
            #     self.log(f"------------ get page : {page} ----------")
            #     yield scrapy.Request(url=url, callback=self.get_link_jobs)

            # link_job = "https://jobsgo.vn/viec-lam/nhan-vien-cham-soc-khach-hang-18475682453.html"         
            # yield scrapy.Request(url=link_job, callback=self.get_type_job_detail)
        except Exception as e:      
            self.save_error_message(repr(e))   

    def get_link_jobs_home(self, response):
        try:
            hostbase = f"https://jobsgo.vn"
            #self.log(f"------------ get_link_jobs {response.request.url} ----------")
            get_link_job_total = []
            link_jobs_viec_tuyen_gap = response.xpath("//*[@id='carousel1']/div[2]/div/div/div/a/@href").extract()
            link_jobs_viec_noi_bat = response.xpath("//*[@id='carousel3']/div/div/div/div/a/@href").extract()

            self.log(f"------------ link_jobs_viec_tuyen_gap count >>> {len(link_jobs_viec_tuyen_gap)} --- detail : {link_jobs_viec_tuyen_gap} ----------")
            self.log(f"------------ link_jobs_viec_noi_bat count >>> {len(link_jobs_viec_noi_bat)} --- detail : {link_jobs_viec_noi_bat} ----------")
            get_link_job_total.extend(link_jobs_viec_tuyen_gap)
            get_link_job_total.extend(link_jobs_viec_noi_bat)


            self.log(f"------------ get_link_job_total count >>> {len(get_link_job_total)}  ----------")
            for link in get_link_job_total:
                yield scrapy.Request(url=f"{hostbase}/{link}", callback=self.get_type_job_detail)

        except Exception as e:      
            self.save_error_message(repr(e)) 

    def get_link_jobs(self, response):
        try:
            #self.log(f"------------ get_link_jobs {response.request.url} ----------")
            link_jobs = response.xpath("//div[@class='brows-job-position']/h3/a/@href").extract()
            self.log(f"------------ get_link_jobs detail: {link_jobs} ----------")
            for link in link_jobs:
                yield scrapy.Request(url=link, callback=self.get_type_job_detail)

        except Exception as e:      
            self.save_error_message(repr(e))     


    def get_type_job_detail(self, response):
        try:
            has_warning_cheat = response.xpath("//p[@class='mt-20 alert alert-warning']/strong/text()").extract_first()
            if has_warning_cheat:
                self.log("job type >> get_job_detail_cheat ")
                yield self.get_job_detail_cheat(response)
            else: #job binh thuong
                self.log("job type >> get_job_detail ")
                yield self.get_job_detail(response)
        except Exception as e:      
            self.save_error_message(repr(e))


    def get_job_detail_cheat(self, response):
        try:
            self.log(f"------------ get_job_detail_cheat {response.request.url}----------")       
            item = JobItem()
            url = response.request.url
            id = url.replace(".html", "").split('-')[-1]
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url

            list_property_job = response.xpath("//div[@class='panel-body']/div[@class='row']/div").extract()
            gender = "";  exprience = ""; job_position = ""; datePosted = ""
            statments = range(len(list_property_job))
            for statment in statments:
                if "Ngày đăng tuyển" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()
                    datePosted = context

                elif "Vị trí/chức vụ" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()
                    job_position = context

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
            working_area = []
            address_working = response.xpath("//div[@class='data giaphv']/p/text()").extract_first()
            if address_working:
                arr_address_working.append(address_working)

                if address_working.count(',') > 0 :
                    part_address = address_working.split(',')
                    working_area_string = part_address[len(part_address) - 1]
                    working_area.append(working_area_string)
                else:
                    working_area.append(address_working)

            
            branch = []
            branch_arr = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[6]/div[@class='list']/a/text()").extract()
            if branch_arr:
                branch.extend(branch_arr)
            
            company_name = response.xpath("/html/body/section[1]/div/div/div/div/div[2]/div/div/div/div[1]/div[2]/div[2]/h2/a/text()").extract_first()
            company_description = response.xpath("//div[@class='company-info text-grey']").extract_first()
            job_description = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[7]").extract_first()
            skill_requirements = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[8]").extract_first()
            jobBenefits = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[9]").extract_first()
            

            exp_date = ""
            exp_date_number = response.xpath("//span[@class='deadline text-bold text-orange']/text()").extract_first()
            if exp_date_number:
                exp_date = datetime.datetime.now() + datetime.timedelta(int(exp_date_number))
            
            item['job_title']  = title
            item['working_address'] = arr_address_working
            item['created_date'] = datePosted
            item['exp_date'] = exp_date
            item['company_name'] = company_name
            item['company_description'] = company_description   
            item['job_description'] = job_description
            item['job_position'] = job_position
            item['branch'] = branch
            item['skill_requirements'] = skill_requirements
            item['benefit'] = jobBenefits
            item['contract_type'] =  ""
            item['gender'] = gender
            item['working_area'] = working_area
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = exprience
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = salary
            item['level_of_readiness'] = ""
            item['number_of_vacancies'] = ""
            item['working_form'] = ""

            create_date = datetime.datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')   
            return item
    
        except Exception as e:      
            self.save_error_message(f"id:{id} -- url:{url} -- {repr(e)}") 
    
    def get_job_detail(self, response):
        try:
            self.log(f"------------ get_job_detail {response.request.url}----------")
            item = JobItem()
            url = response.request.url
            
            id = url.replace(".html", "").split('-')[-1]
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url

            res = response.xpath("//script[@type='application/ld+json']/text()").extract_first()
            res = json.loads(res)
            self.log(res) ## get detail job

            list_property_job = response.xpath("//div[@class='panel-body']/div[@class='row']/div").extract()
            gender = "";  exprience = ""; job_position = ""
            statments = range(len(list_property_job))
            for statment in statments:
                if "Ngày đăng tuyển" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()

                elif "Vị trí/chức vụ" in list_property_job[statment]: 
                    path = f"//div[@class='panel-body']/div[@class='row']/div[{statment + 1}]/p[2]/text()"
                    context = response.xpath(path).extract_first()
                    job_position = context

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
            working_area = []
            locationArr = res.get('jobLocation', '')
            if locationArr:
                for location in locationArr:
                    arr_address_working.append(location["address"]["streetAddress"])
                    working_area.append(location["address"]["addressRegion"])           
            item['working_address'] = arr_address_working

            item['job_title']  = title
            job_description = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[7]").extract_first()
            skill_requirements = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[8]").extract_first()
            jobBenefits = response.xpath("/html/body/section[1]/div/div/div/div/div[1]/div/div/div[9]").extract_first()
            item['created_date'] = res["datePosted"]
            item['exp_date'] = res["validThrough"]
            item['company_name'] = res["hiringOrganization"]["name"]
            item['company_description'] = res["employerOverview"]       
            item['job_description'] = job_description
            item['job_position'] = job_position
            item['branch'] = res["industry"]
            item['skill_requirements'] = skill_requirements
            item['benefit'] = jobBenefits
            item['contract_type'] =  ""
            item['gender'] = gender
            item['working_area'] = working_area
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
            return item
    
        except Exception as e:      
            self.save_error_message(f"id:{id} -- url:{url} -- {repr(e)}") 
    
    def save_error_message(self, error_message):
        item = ErrorItem()
        create_date = datetime.datetime.now()
        item['id_error'] = str(uuid.uuid4())
        item['source'] = _source
        item['error_message'] = error_message 
        item['created_date'] = create_date
        item['created_date_string'] = create_date.strftime('%d/%m/%Y')
        self.collection_error.insert_one(dict(item))
        #send_email("notification [spider jobsgo] - [error]", str(repr(error_message))) 
        return item
