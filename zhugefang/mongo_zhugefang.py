from lib.mongo import Mongo
from lib.standardization import standard_city, standard_block
from pymongo import MongoClient

m = Mongo('192.168.0.235', 27017)
coll_name = m.connect['comm_price']['zhugefang_backup']

n = MongoClient('192.168.0.61', 27017)
save_coll = n['fangjia_tmp']['zhugefang_unitprice_source']


def mongo_chanch():
    for i in coll_name.find({},no_cursor_timeout=True):
        name = i['comm_name']
        city_name_ = i['city']
        DistrictName_ = i['comm_addr']
        UnitPrice = int(i['price'])
        update_time = i['time']
        category = 'district'
        s_date = int(update_time.strftime('%Y%m'))
        city_name = standard_city(city_name_)
        DistrictName = standard_block(DistrictName_)
        data = {
            'category': category,
            'city': city_name,
            'name': name,
            'region': DistrictName,
            's_date': s_date,
            'zhugefang_esf_price': UnitPrice,
        }
        if not data['region']:
            continue
        print(data)
        save_coll.update_one({'region': DistrictName, 'city': city_name, 'name': name}, {'$set': data}, upsert=True)
