import scrapy
from pathlib import Path
from timviec365.items import JobItem, ErrorItem
from scrapy.utils.project import get_project_settings
import json, time
import datetime 
import json
from datetime import datetime
import uuid
import pymongo, requests
from timviec365.utilities  import send_email
from scrapy.http import HtmlResponse

###

import scrapy
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import time


domain = "https://timviec365.vn"
class Timviec365SpiderSpider(scrapy.Spider):
    name = "timviec365_spider"
    allowed_domains = ["timviec365.vn"]
    start_urls = ["https://timviec365.vn"]

    global _source
    _source = "timviec365"

    def __init__(self):
        settings = get_project_settings()
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection_error = db[settings['MONGODB_COLLECTION_ERROR']]

        #chrome_options = Options()
        #chrome_options.add_argument('--headless')  # Run in headless mode
        #chrome_service = ChromeService(executable_path='chromedriver_win64.exe')  # Update path to your chromedriver
        #self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        ##self.driver = webdriver.Chrome(options=chrome_options)

    def start_requests(self):
        try:
           settings = get_project_settings()
           # GET_NUMBER_PAGE = int(settings['GET_NUMBER_PAGE'])
           # print(f"-------------- GET_NUMBER_PAGE : {GET_NUMBER_PAGE}")
        #    page_number = 0

        #    # get page number total
        #    self.driver.get('https://timviec365.vn/tim-kiem?keyword=&capnhat=1&type_search=2&page=1')  # Replace with your URL

        #    # Wait for the JavaScript content to load (adjust the timeout and condition as needed)
        #    WebDriverWait(self.driver, 10).until(
        #       EC.presence_of_element_located((By.ID, 'scr_elm'))
        #    )

        #    html_text = self.driver.page_source
        #    if html_text:
        #       response_html = HtmlResponse(url=self.driver.current_url, body=html_text, encoding='utf-8')
        #       if response_html:
        #           page_number_text = response_html.xpath("//*[@id='scr_elm']/ul/li[8]/a/text()").extract_first()
        #           if  page_number_text:
        #               page_number = int(page_number_text)
           
        #   print(f"page_number: {page_number}")
            
           #page_number = 60
           page_number = 186
           print(f"set page_number: {page_number}")
           
            # get link job
           if page_number != 0:
                for page in range(page_number, 1, -1):
                    #url = f"https://timviec365.vn/tim-kiem?keyword=&capnhat=1&type_search=2&page={page}" #type = 2 => job mới nhất
                  
                    #url = f"https://timviec365.vn/tim-kiem?keyword=&capnhat=1&page={page}" #=> Phù hợp nhất  
                    url = f"https://timviec365.vn/tim-kiem?keyword=&capnhat=2&page={page}" #=> job 1 month tro lai 
                    #url = f"https://timviec365.vn/tim-kiem?keyword=&capnhat=1&page={page}&type_search=3" #=> luong tot nhất
                    print(f"------------ Start Page: {page} --- url: {url}----------")
                    yield scrapy.Request(url=url, callback=self.get_link_jobs)

           print("----------- crawl end ")
            #########
            # for page in range(1, GET_NUMBER_PAGE + 1, 1):
            #     url = f"https://timviec365.vn/tim-kiem?keyword=&capnhat=1&type_search=2&page={page}" #type = 2 => job mới nhất
            #     print(f"------------ Start Page: {page} --- url: {url}----------")
            #     yield scrapy.Request(url=url, callback=self.get_link_jobs)
        
        except Exception as e:      
            self.save_error_message(repr(e)) 
        
    def get_link_jobs(self, response):
        try:
            print(f"------------ get_link_jobs {response.request.url} ----------")
            time.sleep(1)
            ## get link job from json
            #res = response.xpath("//script[@type='application/ld+json'][2]/text()").extract_first()
            res = response.xpath("//script[@id='__NEXT_DATA__']/text()").extract_first()
            res = json.loads(res)
            
            # with open('data.json', 'w') as f:
            #    json.dump(res, f)
            # print(res) ## get detail job

            jobs = res['props']['pageProps']['dataSSR']
            for job in jobs:
                alias = job['new_alias']
                id = job['new_id']
                link_job = f'{domain}/{alias}-p{id}.html'
                print(f"------------ get_link_job {link_job} ")
                yield scrapy.Request(url= link_job, callback=self.get_job_detail_xpath, meta={'job':job})


            ## get link job from html xpath
            # linkjobs = response.xpath("//a[@class='item_cate_logo_user_th__xgkX1']/@href").extract()
            # for linkjob in linkjobs:
            #     link_job_full = f'{domain}/{linkjob}'

            #     print(link_job_full)
            #     #print(f"------------ get_link_job {link_job}----------")
            #     #yield scrapy.Request(url= link_job_full, callback=self.get_job_detail)

        except Exception as e:      
            self.save_error_message(repr(e))

    def get_job_detail_xpath(self, response):
        try:
            print(f"------------ get_job_detail_xpath {response.request.url} ")
            jobMeta = response.meta['job']

            branch = response.xpath("//*[@id='detail_new']/div[3]/div/div/div[1]/div[1]/div[1]/div/div[2]/p[1]/a/@title").extract()
            working_address = response.xpath("//span[@class='diachi']/text()").extract_first()
            job_description = response.xpath("//div[@id='tab_ttin']/div[3]").extract_first()
            job_position = response.xpath("//*[@id='tab_ttin']/div[1]/div/div[1]/div[1]/span/text()").extract_first()
            number_of_vacancies = response.xpath("//*[@id='tab_ttin']/div[1]/div/div[2]/div[1]/span/text()").extract_first()
            working_form = response.xpath("//*[@id='tab_ttin']/div[1]/div/div[1]/div[2]/span/text()").extract_first()
            
            item = JobItem()
            
            url = response.request.url
            if working_address:
                working_address = working_address.strip().replace("\r\n", " ")
            item['working_address'] = working_address
            id = jobMeta['new_id']
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url
            item['job_title']  = jobMeta['new_title'].encode().decode("utf-8")
            item['created_date'] = datetime.fromtimestamp(int(jobMeta["new_update_time"]))
            item['exp_date'] = datetime.fromtimestamp(int(jobMeta["new_han_nop"]))
            item['company_name'] = jobMeta["usc_company"].encode().decode("utf-8")
            item['company_description'] = ""    
            item['job_description'] = job_description
            if job_position:
                job_position = job_position.strip().replace("\r\n", " ")
            item['job_position'] =  job_position
            item['branch'] =  branch #res["industry"] #
            item['skill_requirements'] = jobMeta['new_yeucau'].encode().decode("utf-8")
            item['benefit'] = jobMeta["new_quyenloi"].encode().decode("utf-8")
            item['contract_type'] =  ""
            item['gender'] = "" #res['new_gioi_tinh'].encode().decode("utf-8")
            item['working_area'] = jobMeta['new_name_cit'].encode().decode("utf-8")
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = jobMeta['new_exp']
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = jobMeta['new_money_str']
            item['level_of_readiness'] = ""
            if number_of_vacancies:
                number_of_vacancies = number_of_vacancies.strip().replace("\r\n", " ")
            item['number_of_vacancies'] = number_of_vacancies

            if working_form:
                working_form = working_form.strip().replace("\r\n", " ")
            item['working_form'] = working_form
            
            create_date = datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')
            yield item

        except Exception as e:      
            self.save_error_message(repr(e))  




    def get_job_detail_json(self, response):
        try:
            print(f"------------ get_job_detail_json {response.request.url}----------")
            #get res json
            res = response.xpath("//script[@id='__NEXT_DATA__']/text()").extract_first()
            print("------res")
            #s1 = json.dumps(res)
            #d2 = json.loads(s1)

            
            res = json.loads(res)
            res = res['props']['pageProps']['dataDetaisSSR']
            #print(res)
            # print(res)

            item = JobItem()
            branch = response.xpath("//div[@class='main_timviec_com_info__nUS4l ']/p[@class='main_timviec_index__odtVP main_timviec_hidden_mobi__y9Kui']/a[@class='main_timviec_tag__Ohrr1']/@title").extract()
            url = response.request.url
            item['working_address'] = res['new_addr']
            id = res['new_id']
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url
            item['job_title']  = res['new_title'].encode().decode("utf-8")
            item['created_date'] = datetime.fromtimestamp(int(res["new_update_time"]))
            item['exp_date'] = datetime.fromtimestamp(int(res["new_han_nop"]))
            item['company_name'] = res["usc_company"].encode().decode("utf-8")
            item['company_description'] = ""    
            item['job_description'] = res["new_mota"].encode().decode("utf-8")
            position = ''
            if(res["new_cap_bac"] == 2):
                position = "Trưởng phòng"
            elif(res["new_cap_bac"] == 3):
                position = "Nhân viên"
            elif(res["new_cap_bac"] == 5):
                position = "Trưởng Nhóm"
                
            item['job_position'] =  position
            item['branch'] =  branch #res["industry"] #
            item['skill_requirements'] = res['new_yeucau'].encode().decode("utf-8")
            item['benefit'] = res["new_quyenloi"].encode().decode("utf-8")
            item['contract_type'] =  ""
            item['gender'] = res['new_gioi_tinh'].encode().decode("utf-8")
            item['working_area'] = res['name_city'].encode().decode("utf-8")
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = res['new_exp']
            item['skill'] = ""
            item['job_group_priority'] = "" 
            item['salary'] = res['new_money_str']
            item['level_of_readiness'] = ""
            quantity_recruitment = res['new_so_luong']
            item['number_of_vacancies'] = f'{quantity_recruitment} người'
            if(res["new_hinh_thuc"] == 1):
                item['working_form'] = "Toàn thời gian cố định"
            else:
                item['working_form'] = ""
            
            create_date = datetime.now()
            #yesterday = datetime.now() - datetime.timedelta(1)
            item['created_date_crawl_job'] = create_date
            item['created_date_crawl_job_string'] = create_date.strftime('%d/%m/%Y')
            yield item

        except Exception as e:      
            self.save_error_message(repr(e)) 

    def save_error_message(self, error_message):
        item = ErrorItem()
        create_date = datetime.now()
        item['id_error'] = str(uuid.uuid4())
        item['source'] = _source
        item['error_message'] = error_message 
        item['created_date'] = create_date
        item['created_date_string'] = create_date.strftime('%d/%m/%Y')
        self.collection_error.insert_one(dict(item))
        #send_email("notification [spider timviec365] - [error]", str(repr(error_message))) 
        return item
