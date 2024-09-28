import pymongo
import gzip
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
import os, sys

import json, time
import uuid
import datetime 
import base64 , pprint
from items import ErrorItem
from utilities  import send_email
import argparse

try:  
    parser = argparse.ArgumentParser()
    parser.add_argument('--backdate', dest='backdate', type=str, help='param backdate')
    args = parser.parse_args()
    print(f"args -backdate {args.backdate}")


    with open('env.json', 'r') as file:
        config = json.load(file)
        MONGODB_SERVER = str(config['MONGODB_CONFIG']['MONGODB_SERVER'])
        MONGODB_PORT = str(config['MONGODB_CONFIG']['MONGODB_PORT'])
        MONGODB_DB = str(config['MONGODB_CONFIG']['MONGODB_DB'])
        MONGODB_COLLECTION = str(config['MONGODB_CONFIG']['MONGODB_COLLECTION'])
        MONGODB_COLLECTION_ERROR = str(config['MONGODB_CONFIG']['MONGODB_COLLECTION_ERROR'])

        # connection string Azure Blob
        connection_string =  str(config['BLOB_STORAGE']['CONNECTION_STRING'])
        container_name = str(config['BLOB_STORAGE']['CONTAINER_NAME']) 
    

    client = pymongo.MongoClient(f"mongodb://{MONGODB_SERVER}:{MONGODB_PORT}/")
    db = client[f"{MONGODB_DB}"]
    _dbcollection = db[f"{MONGODB_COLLECTION}"]
    _dbcollectionError = db[f"{MONGODB_COLLECTION_ERROR}"]
    _dateRun = ""

    def check_date_format(date_string): #dd-MM-yyyy
        try:
            # Attempt to parse the date in dd-MM-yyyy format
            dateformat = datetime.datetime.strptime(date_string, "%d-%m-%Y")
            return True
        except Exception as e:  
            print(repr(e))    
            item = ErrorItem()
            create_date = datetime.datetime.now()
            #create_date = datetime.now() version in crawlab
            item['id_error'] = str(uuid.uuid4())
            item['source'] = "sync_data"
            item['error_message'] = repr(e)
            item['created_date'] = create_date
            item['created_date_string'] = create_date.strftime('%d/%m/%Y')
            _dbcollectionError.insert_one(dict(item))
            return False
        
    if args.backdate is not None and check_date_format(args.backdate):
        _dateRun = datetime.datetime.strptime(args.backdate, "%d-%m-%Y")
        print(f"dateformat backdate >> {_dateRun}")   

    elif args.backdate is None:
        #created_date = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=7)
        created_date = datetime.datetime.utcnow() + datetime.timedelta(hours=7) #version crawlab

        print(f"backdate is null & get currentdate: {created_date}")
        _dateRun = created_date


    if _dateRun:    
        #created_date = datetime.datetime.utcnow() + datetime.timedelta(hours=7) #version in crawlab
        print(f"dateRun >> {_dateRun}")

        arr_source = ["topcv", "careerviet", "jobsgo", "timviec365", "vieclam24h", "vietnamwork"]
        pathFolderBaseAzure = "OJV Data"
        path_folder = os.path.join(f"{os.getcwd()}/{pathFolderBaseAzure}", f"{_dateRun.strftime('%Y%m%d')}")
        for source in arr_source:
            sub_path_folder = os.path.join(f"{os.getcwd()}/{pathFolderBaseAzure}/{_dateRun.strftime('%Y%m%d')}", f"{source}")
            print(f"source sub_path_folder >>> {sub_path_folder}")
            if not os.path.exists(sub_path_folder):
                os.makedirs(sub_path_folder)


        for source in arr_source:
            print(f"source >> {source}")
            query = {
                "$and": [
                    {"created_date_crawl_job_string": f"{_dateRun.strftime('%d/%m/%Y')}"},
                    {"source": f"{source}"}
                ]
            }
            
            jobs = _dbcollection.find(query) #.limit(1)
            listJob = list(jobs)
            ##print("data")
            
            arrJob = []
            for item in listJob:
                item['_id'] = str(item['_id'])
                item['created_date_crawl_job'] = str(item['created_date_crawl_job'])
                item['created_date'] = str(item['created_date'])
                item['exp_date'] = str(item['exp_date'])
                arrJob.append(item)
            print(arrJob)


            blob_name = f"{source}_{_dateRun.strftime('%Y%m%d_%H%M%S')}.json"
            path_file = f"{path_folder}/{source}/{blob_name}"
            with open(path_file, 'w', encoding='utf-8') as f:
                json.dump(arrJob, f, ensure_ascii=False, indent=4)


        # Nén dữ liệu thành file JSON
        # with gzip.open('data.json.gz', 'wt') as f:
        #     json.dump(data, f)
        
        #created_date = datetime.datetime.now()
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create container if not exsist
        #container_client = blob_service_client.get_container_client(container_name)
        #container_client.create_container()

        # Crate BlobClient - upload file Blob Storage
        #blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # with open(local_file_path, "rb") as data:
        #     blob_client.upload_blob(data) #, overwrite=True
        #     print(f" Uploaded File is Sucess -  File Name: {local_file_path} - Blob name: {blob_name} - Container name: {container_name}.")

        # with open(path_file, 'rb') as data:
        #     #json.dump(arrJob, data, ensure_ascii=False, indent=4)
        #     blob_client.upload_blob(data) #, overwrite=True
        #     print(f" Uploaded File is Sucess - Blob name: {path_file} - Container name: {container_name}.")



        overwrite = False
        for folder in os.walk(path_folder):
            for file in folder[-1]:
                try:
                    blob_path = os.path.join(folder[0].replace(os.getcwd() + '/', ''), file)
                    blob_obj = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
                    
                    with open(os.path.join(f"{folder[0]}", file), mode='rb') as file_data:
                        blob_obj.upload_blob(file_data, overwrite=overwrite)
                        noti_success = (f" Uploaded File is Sucess - Blob name: {blob_path} - Container name: {container_name}.")
                        print(noti_success)
                        #send_email("notification [service syncdata to azure blob] - [infor]", noti_success)
                except ResourceExistsError:
                    print('Blob "{0}" already exists'.format(blob_path))
                    #send_email("notification [service syncdata to azure blob] - [error]", str(repr(e))) 
                    continue

        

        # #update flag db
        # #_dbcollection.update_many({ 'working_address': '' }, { '$set': { 'working_address': '1' } })
    


except Exception as e:
    print(repr(e))   
    item = ErrorItem()
    create_date = datetime.datetime.now()
    #create_date = datetime.now() version in crawlab
    item['id_error'] = str(uuid.uuid4())
    item['source'] = "sync_data"
    item['error_message'] = str(repr(e)) 
    item['created_date'] = create_date
    item['created_date_string'] = create_date.strftime('%d/%m/%Y')
    _dbcollectionError.insert_one(dict(item))
    #send_email("notification [service syncdata to azure blob] - [error]", str(repr(e))) 
