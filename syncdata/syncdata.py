import pymongo
import gzip
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
import os

import json, time
import uuid
import datetime 
import base64 , pprint
from items import ErrorItem

try:  
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
    
    created_date = datetime.datetime.now()


    client = pymongo.MongoClient(f"mongodb://{MONGODB_SERVER}:{MONGODB_PORT}/")
    db = client[f"{MONGODB_DB}"]
    _dbcollection = db[f"{MONGODB_COLLECTION}"]
    _dbcollectionError = db[f"{MONGODB_COLLECTION_ERROR}"]
    # get data from MongoDB

    current_date = f'{created_date.strftime('%d/%m/%Y')}'
    print(f"ss >> {current_date}")

    arr_source = ["topcv", "careerviet", "jobsgo", "timviec365", "vieclam24h", "vietnamwork"]

    pathFolderBaseAzure = "OJV Data"
    path_folder = os.path.join(f'{os.getcwd()}\{pathFolderBaseAzure}', f'{created_date.strftime('%Y%m%d')}')
    for source in arr_source:
        sub_path_folder = os.path.join(f'{os.getcwd()}\{pathFolderBaseAzure}\{created_date.strftime('%Y%m%d')}', f'{source}')
        print(f"source cre >>> {sub_path_folder}")
        if not os.path.exists(sub_path_folder):
            os.makedirs(sub_path_folder)
        

    
    for source in arr_source:
        print(f"source >> {source}")
        query = {
            "$and": [
                {"created_date_crawl_job_string": f'{current_date}'},
                {"source": f"{source}"}
            ]
        }
        
        jobs = _dbcollection.find(query).limit(1)
        listJob = list(jobs)
        ##print("data")
        
        arrJob = []
        for item in listJob:
            item['_id'] = str(item['_id'])
            item['created_date_crawl_job'] = str(item['created_date_crawl_job'])
            arrJob.append(item)
        print(arrJob)


        blob_name = f"{source}_{created_date.strftime('%Y%m%d_%H%M%S')}.json"
        path_file = f'{path_folder}\{source}\{blob_name}'
        with open(path_file, 'w', encoding='utf-8') as f:
            json.dump(arrJob, f, ensure_ascii=False, indent=4)

    
    
    # Nén dữ liệu thành file JSON
    # with gzip.open('data.json.gz', 'wt') as f:
    #     json.dump(data, f)
    
    created_date = datetime.datetime.now()
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
                blob_path = os.path.join(folder[0].replace(os.getcwd() + '\\', ''), file)
                blob_obj = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
                
                with open(os.path.join(f"{folder[0]}", file), mode='rb') as file_data:
                    blob_obj.upload_blob(file_data, overwrite=overwrite)
                    print(f" Uploaded File is Sucess - Blob name: {blob_path} - Container name: {container_name}.")
            except ResourceExistsError:
                print('Blob "{0}" already exists'.format(blob_path))
                print()
                continue

    

    #update flag db
    #_dbcollection.update_many({ 'working_address': '' }, { '$set': { 'working_address': '1' } })
    


except Exception as e:
    print(repr(e))   
    item = ErrorItem()
    create_date = datetime.datetime.now()
    item['id_error'] = str(uuid.uuid4())
    item['source'] = "sync_data"
    item['error_message'] = str(repr(e)) 
    item['created_date'] = create_date
    item['created_date_string'] = create_date.strftime('%d/%m/%Y')
    _dbcollectionError.insert_one(dict(item)) 
