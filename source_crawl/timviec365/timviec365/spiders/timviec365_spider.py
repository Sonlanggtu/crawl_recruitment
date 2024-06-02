import scrapy
from pathlib import Path
from timviec365.items import JobItem, ErrorItem
from scrapy.utils.project import get_project_settings
import json, time
import datetime 
import json
from datetime import datetime
import uuid
import pymongo

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

    def start_requests(self):
        try:
            settings = get_project_settings()
            GET_NUMBER_PAGE = int(settings['GET_NUMBER_PAGE'])
            print(f"-------------- GET_NUMBER_PAGE : {GET_NUMBER_PAGE}")
            for page in range(1, GET_NUMBER_PAGE + 1, 1):
                url = f"https://timviec365.vn/tim-kiem?keyword=&capnhat=1&type_search=2&page={page}" #type = 2 => job mới nhất
                print(f"------------ Start Page: {page} --- url: {url}----------")
                yield scrapy.Request(url=url, callback=self.get_link_jobs)
        
        except Exception as e:      
            self.save_error_message(repr(e)) 
        
    def get_link_jobs(self, response):
        try:
            print(f"------------ get_link_jobs {response.request.url} ----------")

            ## get link job from json
            #res = response.xpath("//script[@type='application/ld+json'][2]/text()").extract_first()
            res = response.xpath("//script[@id='__NEXT_DATA__']/text()").extract_first()
            res = json.loads(res)
            
            with open('data.json', 'w') as f:
               json.dump(res, f)
            print(res) ## get detail job

            jobs = res['props']['pageProps']['dataSSR']
            for job in jobs:
                alias = job['new_alias']
                id = job['new_id']
                link_job = f'{domain}/{alias}-p{id}.html'
                #print(f"------------ get_link_job {link_job}----------")
                yield scrapy.Request(url= link_job, callback=self.get_job_detail)


            ## get link job from html xpath
            # linkjobs = response.xpath("//a[@class='item_cate_logo_user_th__xgkX1']/@href").extract()
            # for linkjob in linkjobs:
            #     link_job_full = f'{domain}/{linkjob}'

            #     print(link_job_full)
            #     #print(f"------------ get_link_job {link_job}----------")
            #     #yield scrapy.Request(url= link_job_full, callback=self.get_job_detail)

        except Exception as e:      
            self.save_error_message(repr(e)) 

    def get_job_detail(self, response):
        try:
            print(f"------------ get_job_detail {response.request.url}----------")
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
            item['position']  = res['new_title'].encode().decode("utf-8")
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
        return item
