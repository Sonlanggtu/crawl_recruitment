import scrapy
import scrapy
from pathlib import Path
from careerbuilder.items import JobItem, ErrorItem
#from vietnamworks import gen_alias
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
import pymongo

import json, time
import uuid
import datetime 
import base64 , pprint

class CareervietSpider(scrapy.Spider):
    name = "careerviet_spider"
    allowed_domains = ["careerviet.vn"]
    start_urls = ["https://careerviet.vn"]

    global _source 
    _source = "careerviet"

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

            headers =  {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    'X-Requested-With': 'XMLHttpRequest'
                }
            

            for page in range(1, GET_NUMBER_PAGE + 1, 1):
                print(f"-------- page {page}")
                # dataone = 'a:1:{s:4:"PAGE";s:1:"25";}'
                dataone = f'a%3A1%3A%7Bs%3A4%3A%22PAGE%22%3Bs%3A{page}%3A%2225%22%3B%7D'
                dataTwo = f'a%3A0%3A%7B%7D'
                form_data = {
                    'dataOne': dataone,
                    'dataTwo': dataTwo,
                }
                
                yield scrapy.FormRequest(
                    url="https://careerviet.vn/search-jobs",
                    method='POST',
                    headers= headers,
                    formdata= form_data,
                    callback=self.get_link_jobs
                )

        except Exception as e:      
                self.save_error_message(repr(e))     

    def get_link_jobs(self, response):
        try:

            print(f"------------ get_link_jobs {response.request.url} ----------")
            print("-------------- get_link_jobs json result ")
            res = json.loads(response.body)
            jobs = res['data']



            # for job in jobs:
            #     link_job = job['LINK_JOB']
            #     print(link_job)

            # with open('data2.json', 'w') as f:
            #    json.dump(res, f)
            # print(res) ## get detail job
        
            for job in jobs:
                link_job = job['LINK_JOB']

                #time.sleep(3)
                yield scrapy.Request(url= link_job, callback=self.get_job_detail_xpth)


            # link_job = jobs[15]['LINK_JOB']
            # yield scrapy.Request(url= link_job, callback=self.get_job_detail, meta={'job':jobs[15]})
            #yield scrapy.Request(url= "https://careerviet.vn/vi/tim-viec-lam/chuyen-vien-giam-sat-an-ninh-thong-tin.35C0A86F.html", callback=self.get_job_detail_xpth)

        except Exception as e:
            self.save_error_message(repr(e)) 

            
    def get_job_detail_xpth(self, response):
        try:
            print(f"------------ get_job_detail {response.request.url}----------")
            self.log("------------ response -------------- ")

            item = JobItem()
            salany = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[1]/p/text()").extract_first() 
            exprience = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[2]/p/text()").extract_first() 
            job_position = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[3]/p/text()").extract_first() 
            exp_date = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[4]/p/text()").extract_first() 
            tilte = response.xpath("/html/head/meta[@property='og:title']").extract_first() 
            company_name = response.xpath("/html/body/main/section[2]/div/div/div[1]/section/div[2]/div[1]/a").extract_first() 
            update_date_post = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[2]/div/ul/li[1]/p").extract_first() 
            branch = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[2]/div/ul/li[2]/p/a/text()").extract()
            working_form = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[2]/div/ul/li[3]/p").extract_first()
            working_area = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[1]/div/div/p/a").extract_first()
            benefit = response.xpath("//*[@id='tab-1']/section/div[2]/ul/li/text()").extract()

            description = response.xpath("//*[@id='tab-1']/section/div[@class='detail-row reset-bullet']").extract_first()
            skill_requirements = response.xpath("//*[@id='tab-1']/section/div[4]").extract_first()

            url = response.request.url
            item['working_address'] = ""
            id = url.replace(".html", "").split('-')[-1]
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url
            item['position']  = tilte
            item['created_date'] = update_date_post
            item['exp_date'] = exp_date
            item['company_name'] = company_name
            item['company_description'] = ""    
            item['job_description'] = description
            item['job_position'] =  job_position
            item['branch'] = branch
            item['skill_requirements'] = skill_requirements
            item['benefit'] = benefit
            item['contract_type'] =  ""
            item['gender'] = ""
            item['working_area'] = working_area
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = exprience
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = salany
            item['level_of_readiness'] = ""
            item['number_of_vacancies'] = ""
            item['working_form'] = working_form
            
            create_date = datetime.datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')   
            yield item

        except Exception as e:
            print(repr(e))
            self.save_error_message(repr(e))




    def get_job_detail_json(self, response):
        try:
            print(f"------------ get_job_detail {response.request.url}----------")
            self.log("------------ response -------------- ")

            res_json = response.xpath("//main/script[@type='application/ld+json'][1]/text()").extract_first() 
            #res_json2 = res_json.encode('ascii', 'ignore').rstrip().replace(" ", "")
            
            # with open('data.txt', 'wb') as f:
            #     f.write(res_json2)
            #     f.close()
            
            res = json.loads(res_json)
            #print(res)
            # with open('data.json', 'w') as f:
            #     f.write("Woops! I have deleted the content!")
            #     f.close()
                #json.dump(res, f)
                #print(res) ## get detail job

            # job = response.meta['job']
            # with open('data2.json', 'w') as f:
            #    json.dump(job, f)


            item = JobItem()
            salany = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[1]/p/text()").extract_first() 
            #exprience = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[1]/p/text()").extract_first() 
            url = response.request.url
            item['working_address'] = ""
            id = url.replace(".html", "").split('-')[-1]
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url
            item['position']  = res['title'].encode().decode("utf-8")
            item['created_date'] = res["datePosted"]
            item['exp_date'] = res["validThrough"]
            item['company_name'] = res["hiringOrganization"]["name"]
            item['company_description'] = ""    
            item['job_description'] = res["description"]
            item['job_position'] =  res['occupationalCategory']
            item['branch'] =  res['industry'].encode().decode("utf-8")
            item['skill_requirements'] = res['skills'].encode().decode("utf-8")
            item['benefit'] = res["jobBenefits"].encode().decode("utf-8")
            item['contract_type'] =  ""
            item['gender'] = ""
            item['working_area'] = res['applicantLocationRequirements']['name'].encode().decode("utf-8")
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = res['experienceRequirements']['monthsOfExperience']
            item['skill'] = res['skills']
            item['job_group_priority'] = "" 
            item['salary'] = salany
            item['level_of_readiness'] = ""
            item['number_of_vacancies'] = ""
            if(res["employmentType"] == "FULL_TIME"):
                item['working_form'] = "Nhân viên chính thức"
            else:
                item['working_form'] = ""
            
            create_date = datetime.datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')   
            yield item

        except Exception as e:
            print(repr(e))
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

