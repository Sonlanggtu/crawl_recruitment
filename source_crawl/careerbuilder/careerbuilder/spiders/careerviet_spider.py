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
import base64 , pprint, requests, math
from careerbuilder.utilities  import send_email
from scrapy.http import HtmlResponse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
            #GET_NUMBER_PAGE = int(settings['GET_NUMBER_PAGE'])
            #self.log(f"-------------- GET_NUMBER_PAGE : {GET_NUMBER_PAGE}")
            page_number = 0
            page_number_api = 0
            page_number_xpath = 0
            page_size = 50 # 1 page have 50 job
            headers =  {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    'X-Requested-With': 'XMLHttpRequest'
                }
            

            # get page number total
            url_first = f"https://careerviet.vn/viec-lam/tat-ca-viec-lam-trang-2-vi.html"
            response = requests.get(url_first, headers=headers)
            #self.log(response.text)

            if response.text:
                responseHtml = HtmlResponse(url=url_first, body=response.text, encoding='utf-8')
                #links = responseHtml.xpath("//*[@id='jobs-side-list-content']/div/div/div/a/@href").extract()
                number_total_job = responseHtml.xpath("//div[@class='job-found']/div/h1/text()").extract_first()
                
                

                if number_total_job:
                    number_total_job = number_total_job.replace(" việc làm theo ngày cập nhật mới nhất", "").replace(",", "")
                    number_total_job = int(number_total_job)
                    page_number = math.ceil(number_total_job / page_size)
                #self.log(f"-------- array link: {links}")
                self.log(f"-------- number_total_job: {number_total_job}")
                self.log(f"-------- page_number total: {page_number}")  

                
                # 
                #page_number = 10
                #self.log(f"-------- set page_number total: 4")  
                if page_number != 0:
                    page_number_xpath = page_number
                    page_number_api = page_number


                    # get job by xpath html
                    #=====================================
                    # Define retry strategy
                    retry_strategy = Retry(
                        total=10,                     # Số lần thử lại
                        backoff_factor=1,             # Tăng thời gian chờ giữa mỗi lần retry (1 giây, rồi 2 giây, rồi 4 giây...)
                        status_forcelist=[429, 500, 502, 503, 504],  # Những mã lỗi sẽ kích hoạt retry
                    )

                    # Gắn retry strategy vào adapter
                    adapter = HTTPAdapter(max_retries=retry_strategy)

                    # Tạo session để áp dụng retry logic
                    session = requests.Session()
                    session.mount("https://", adapter)
                    session.mount("http://", adapter)

                    for page in range(page_number_xpath, 0, -1):
                    
                        self.log(f"-------- get xpath page: {page}")
                        url = f"https://careerviet.vn/viec-lam/tat-ca-viec-lam-trang-{page}-vi.html"
                        self.log(f"-------- get xpath url page: {url}")
                        time.sleep(1.5)

                        try:
                            response = session.get(url, headers=headers, timeout=5)  # Giới hạn thời gian chờ
                            response.raise_for_status()  # Kiểm tra lỗi HTTP
                            responseHtml = HtmlResponse(url=url, body=response.text, encoding='utf-8')
                            arrlink = responseHtml.xpath("//*[@id='jobs-side-list-content']/div/div/div[2]/div/h2/a/@href").extract()

                            self.log("arrlink xpath: ")
                            self.log(arrlink)
                            if arrlink:
                                for link_job in arrlink:
                                    self.log(link_job)
                                    time.sleep(1.5)
                                    yield scrapy.Request(url= link_job, callback=self.get_job_detail_xpth)

                            #self.log(f"Success for {url}: {response.status_code}")
                        except requests.exceptions.RequestException as e:
                            self.log(f"Request failed for {url}: {e}")
                        
                        
                        
                        
                        # response = requests.get(url, headers=headers)
                        # #self.log(response.text)
                        # responseHtml = HtmlResponse(url=url, body=response.text, encoding='utf-8')
                        # arrlink = responseHtml.xpath("//*[@id='jobs-side-list-content']/div/div/div[2]/div/h2/a/@href").extract()

                        # self.log("arrlink xpath: ")
                        # self.log(arrlink)
                        # if arrlink:
                        #    for link_job in arrlink:
                        #     self.log(link_job)
                        #     time.sleep(1.5)
                        #     yield scrapy.Request(url= link_job, callback=self.get_job_detail_xpth)

                

                    # get job by api
                    for page in range(page_number_api, 0, -1):
                        self.log(f"-------- get api page: {page}")
                        dataone =""; dataTwo = ""
                        if page <= 9:   # s=1 - dataone = 'a:1:{s:4:"PAGE";s:1:"9";}'
                            dataone = 'a:1:{s:4:"PAGE";s:1:"page_input";}'
                            dataone = dataone.replace("page_input", f"{page}")
                            dataTwo = 'a:0:{}'

                        elif page >=10 and page <= 99:  #s=2
                            dataone = 'a:1:{s:4:"PAGE";s:2:"page_input";}'
                            dataone = dataone.replace("page_input", f"{page}")
                            dataTwo = 'a:0:{}'
                        elif page >=100: #s=3
                            dataone = 'a:1:{s:4:"PAGE";s:3:"page_input";}'
                            dataone = dataone.replace("page_input", f"{page}")
                            dataTwo = 'a:0:{}'

                        # 30 day latest
                        #dataOne: a:2:{s:4:"PAGE";s:3:"250";s:10:"LASTMODIFY";s:2:"30";}
                        #dataOne: a:2:{s:4:"PAGE";s:3:"100";s:10:"LASTMODIFY";s:2:"30";}                
                        #dataOne: a:2:{s:4:"PAGE";s:2:"99";s:10:"LASTMODIFY";s:2:"30";}           
                        #dataOne: a:2:{s:4:"PAGE";s:2:"20";s:10:"LASTMODIFY";s:2:"30";}                       
                        #dataOne: a:2:{s:4:"PAGE";s:2:"10";s:10:"LASTMODIFY";s:2:"30";}                     
                        #dataOne: a:2:{s:4:"PAGE";s:1:"9";s:10:"LASTMODIFY";s:2:"30";}              
                        #dataOne: a:2:{s:4:"PAGE";s:1:"2";s:10:"LASTMODIFY";s:2:"30";}             
                        #dataOne: a:2:{s:4:"PAGE";s:1:"1";s:10:"LASTMODIFY";s:2:"30";}

                        form_data = {
                            'dataOne': dataone,
                            'dataTwo': dataTwo,
                        }

                        #self.log("form_data")
                        #self.log(form_data)
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

            self.log(f"------------ get_link_jobs api {response.request.body} ----------")
            #self.log("-------------- get_link_jobs json result ")
            #time.sleep(1)
            res = json.loads(response.body)
            #self.log(res)
            jobs = res['data']



            # for job in jobs:
            #     link_job = job['LINK_JOB']
            #     self.log(link_job)

            # with open('data2.json', 'w') as f:
            #    json.dump(res, f)
            # self.log(res) ## get detail job
        
        
            for job in jobs:
                link_job = job['LINK_JOB']

                self.log(link_job)
                #time.sleep(3)
                yield scrapy.Request(url= link_job, callback=self.get_job_detail_xpth)


            # link_job = jobs[15]['LINK_JOB']
            # yield scrapy.Request(url= link_job, callback=self.get_job_detail, meta={'job':jobs[15]})
            #yield scrapy.Request(url= "https://careerviet.vn/vi/tim-viec-lam/chuyen-vien-giam-sat-an-ninh-thong-tin.35C0A86F.html", callback=self.get_job_detail_xpth)

        except Exception as e:
            self.save_error_message(repr(e))
            #send_email("notification [spider carreerviet] - [error]", str(repr(e)))   

            
    def get_job_detail_xpth(self, response):
        try:
            self.log(f"------------ get_job_detail {response.request.url}----------")
            self.log("------------ response -------------- ")

            item = JobItem()
            salany = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[1]/p/text()").extract_first() 
            exprience = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[2]/p/text()").extract_first() 
            job_position = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[3]/p/text()").extract_first() 
            exp_date = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[3]/div/ul/li[4]/p/text()").extract_first() 
            tilte = response.xpath("/html/head/meta[@property='og:title']/@content").extract_first() 
            company_name = response.xpath("/html/body/main/section[2]/div/div/div[1]/section/div[2]/div[1]/a/text()").extract_first() 
            update_date_post = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[2]/div/ul/li[1]/p/text()").extract_first() 
            branch = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[2]/div/ul/li[2]/p/a/text()").extract()
            working_form = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[2]/div/ul/li[3]/p/text()").extract_first()
            working_area = response.xpath("//*[@id='tab-1']/section/div[1]/div/div[1]/div/div/p/a/text()").extract_first()
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
            item['job_title']  = tilte
            item['created_date'] = update_date_post
            item['exp_date'] = exp_date
            item['company_name'] = company_name
            item['company_description'] = ""    
            item['job_description'] = description
            item['job_position'] =  job_position
            
            if branch:
                branch_strip = []
                for itemBranch in branch:
                    branch_strip.append(itemBranch.strip().replace(" ", "").replace("\r\n", " "))
                branch = branch_strip
            item['branch'] = branch
            item['skill_requirements'] = skill_requirements
            item['benefit'] = benefit
            item['contract_type'] =  ""
            item['gender'] = ""
            item['working_area'] = working_area
            item['current_level'] = ""
            item['desired_level'] = ""
            if exprience:
                exprience = exprience.strip().replace(" ", "").replace("\r\n", " ")
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
            self.log(repr(e))
            self.save_error_message(repr(e))  




    def get_job_detail_json(self, response):
        try:
            self.log(f"------------ get_job_detail {response.request.url}----------")
            self.log("------------ response -------------- ")

            res_json = response.xpath("//main/script[@type='application/ld+json'][1]/text()").extract_first() 
            #res_json2 = res_json.encode('ascii', 'ignore').rstrip().replace(" ", "")
            
            # with open('data.txt', 'wb') as f:
            #     f.write(res_json2)
            #     f.close()
            
            res = json.loads(res_json)
            #self.log(res)
            # with open('data.json', 'w') as f:
            #     f.write("Woops! I have deleted the content!")
            #     f.close()
                #json.dump(res, f)
                #self.log(res) ## get detail job

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
            self.log(repr(e))
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
        #send_email("notification [spider carreerviet] - [error]", str(repr(error_message)))   
        return item

