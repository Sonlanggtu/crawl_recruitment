# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
import pymongo
from scrapy.exceptions import DropItem


class Vieclam24HPipeline:
    
    def __init__(self):
        settings = get_project_settings()
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        #print(f"_pipeline__________")
        ids_record = self.collection.find_one({'alias': adapter["alias"]})

        if ids_record:
           print(f"----------- Duplicate alias: {item['alias']} ------------------")
            
        else:
            self.collection.insert_one(dict(item))
        return item
