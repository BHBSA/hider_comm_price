from lib.mongo import Mongo
from lib.standardization import standard_city, standard_block
from pymongo import MongoClient
from lib.log import LogHandler

log = LogHandler('fanggugu')

m = Mongo('192.168.0.235', 27017)
coll_name = m.connect['fgg']['fanggugu_price']
coll_price = m.connect['fgg']['fanggugu_price_update']

n = MongoClient('192.168.0.61', 27017)
save_coll = n['fangjia_tmp']['fangguguUnitprice']


def mongo_chanch():
    for i in coll_price.find({}, no_cursor_timeout=True):
        try:
            ResidentialAreaID = i['ResidentialAreaID']
            city_name_ = i['city_name']
            DistrictName_ = i['DistrictName']
            UnitPrice = i['UnitPrice']
            update_time = i['update_time']
            name = \
                coll_name.find_one(
                    {'ResidentialAreaID': ResidentialAreaID, 'city_name': city_name_, 'DistrictName': DistrictName_})[
                    'baseinfo']['json'][0]['residentialareaMap']['residentialareaName']
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
                'fanggugu_esf_price': UnitPrice,
            }
            print(data)
            save_coll.update_one({'region': DistrictName, 'city': city_name, 'name': name}, {'$set': data}, upsert=True)
        except Exception as e:
            log.info(i)
