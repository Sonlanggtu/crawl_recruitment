import scrapy
from pathlib import Path
from vieclam24h.items import JobItem, ErrorItem
#from vietnamworks import gen_alias
from scrapy.utils.project import get_project_settings
import json, time
import datetime 
import json
from scrapy.selector import Selector
import pymongo
import uuid

domain = "https://vieclam24h.vn"

class Vieclam24hSpiderSpider(scrapy.Spider):
    name = "vieclam24h_spider"
    allowed_domains = ["vieclam24h.vn"]
    start_urls = ["https://vieclam24h.vn"]

    global _source
    _source = "vieclam24h" 

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
                url = f"https://vieclam24h.vn/tim-kiem-viec-lam-nhanh?page={page}&sort_q=actived_at_by_box%252Cdesc"
                #print(f"------------ url: {url}----------")
                yield scrapy.Request(url=url, callback=self.get_link_jobs)

            # url = "https://vieclam24h.vn/luat-phap-ly-tuan-thu/vinhomes-chuyen-vien-thu-tuc-bds-c25p122id200352075.html"
            # yield scrapy.Request(url=url, callback=self.get_job_detail)
        except Exception as e:      
            self.save_error_message(repr(e)) 
        
    def get_link_jobs(self, response):
        try:

            print(f"------------ get_link_jobs {response.request.url} ----------")
            link_jobs = response.xpath("//a[@data-content-target]/@data-content-target").extract()
            for link in link_jobs:
                yield scrapy.Request(url=f'{domain}{link}', callback=self.get_job_detail)   

        except Exception as e:      
            self.save_error_message(repr(e))  


    def get_job_detail(self, response):
        try:
                
            print(f"------------ get_job_detail {response.request.url}----------")

            res = response.xpath("//head/script[@type='application/ld+json'][3]/text()").extract_first()
            #print("res")
            res = json.loads(res)
            # with open('data2.json', 'w') as f:
            #    json.dump(res, f)
            #print(res) ## get detail job

            #get json 2
            res2 = response.xpath("//script[@id='__NEXT_DATA__']/text()").extract_first()
            #print("res2")
            res2 = json.loads(res2)
            #print(res2)
            
            #test - write json file
            # with open('data.json', 'w') as f:
            #    json.dump(res2, f)

            company_introdure = ""
            jobDetailHiddenContact = res2['props']['initialState']['api']['jobDetailHiddenContact']
            if(jobDetailHiddenContact['code'] == 200):
                company_introdure = jobDetailHiddenContact['data']['employer_info']['description']
            

            branch = ""; salary =""; area_working=""
            initialProps = res2['props']['initialProps']['pageProps']['metaSeo']['keyReplace']
            for item in initialProps:
                if item['key'] == "{NGANH_NGHE}":
                    branch = item['value'].encode().decode("utf-8")
                elif item['key'] == "{MUC_LUONG}":
                    salary = item['value'].encode().decode("utf-8")
                elif item['key'] == "{TINH_THANH}":
                    area_working = item['value'].encode().decode("utf-8")
            

            item = JobItem()

            gender = "";  exprience = ""; quantity_recruitment = ""; position = ""
            list_property_job = response.xpath("//div[contains(@class, 'flex items-center mb-4')]").extract()

            #print("--------------job_property")
            for job_property in list_property_job:
                #print(html.unescape(job_property))
                header_field = Selector(text=job_property).xpath("//div[contains(@class, 'flex items-center mb-4')]/p[1]/text()").extract_first()
                path_context = f"//div[contains(@class, 'flex items-center mb-4')]/p[2]/text()"

                if "Ngày đăng" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)

                elif "Cấp bậc" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)
                    position = context

                elif "Số lượng tuyển" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    quantity_recruitment = context
                    #print(context)

                elif  "Hình thức làm việc" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)              

                elif "Yêu cầu kinh nghiệm" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)
                    exprience = context

                elif "Yêu cầu bằng cấp" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)

                elif "Thời gian thử việc" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)
                
                elif "Độ tuổi" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)

                elif "Yêu cầu giới tính" in header_field: 
                    context = Selector(text=job_property).xpath(path_context).extract_first()
                    #print(context)
                    gender = context

            #salary = response.xpath("//p[@class='font-semibold text-14 text-[#8B5CF6]']/text()").extract_first()

            arr_address_working = []
            for location in res["jobLocation"]:
                streetAddress = location["address"]["streetAddress"]
                if streetAddress != "Toàn khu vực":
                    streetAddress = f'{streetAddress}, '
                else:
                    streetAddress = ""
                    
                address =f'{streetAddress}{location["address"]["addressLocality"]}, {location["address"]["addressRegion"]}' 
                arr_address_working.append(address)

            # arr_area_working = []
            # for location in res["jobLocation"]:
            #     area_working =f'{location["address"]["addressRegion"]}' 
            #     arr_area_working.append(area_working)

            url = response.request.url
            item['working_address'] = arr_address_working
            id = url.replace(".html", "").split('-')[-1]
            item['id_record'] = id 
            item['source'] = _source
            item['alias'] = str(f"{_source}_{id}")             
            item['url']  = url
            item['position']  = res['title']
            item['created_date'] = res["datePosted"]
            item['exp_date'] = res["validThrough"]
            item['company_name'] = res["hiringOrganization"]["name"]
            item['company_description'] = company_introdure    
            item['job_description'] = res["description"]
            item['job_position'] =  position
            item['branch'] =  branch #res["industry"] #
            item['requirement'] = res['skills']
            item['benefit'] = res["jobBenefits"]
            item['contract_type'] =  ""
            item['gender'] = gender
            item['area_working'] = area_working
            item['current_level'] = ""
            item['desired_level'] = ""
            item['experience'] = exprience
            item['skill_requirements'] = res['skills']
            item['job_group_priority'] = "" 
            item['salary'] = salary
            item['level_of_readiness'] = ""
            item['number_of_vacancies'] = quantity_recruitment
            if(res["employmentType"] == "FULL_TIME"):
                item['working_form'] = "Toàn thời gian cố định"
            else:
                item['working_form'] = ""
            
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