from lib.mongo import Mongo
from lib.standardization import standard_city, standard_block
from lib.log import LogHandler

log = LogHandler('zhugefang')

m = Mongo('192.168.0.235', 27017)
connect = m.connect
coll_zhugefang = connect['comm_price']['zhugefang']
coll_save = connect['comm_price']['zhugefang_backup']


def start():
    for i in coll_zhugefang.find():
        try:
            if i['price'] == 0:
                i['price'] = '0'
            i['price'] = i['price'].strip()
            i['city'] = standard_city(i['city'])
            i['comm_addr'] = standard_block(i['comm_addr']).strip()
            print(i)
            if not i['comm_addr']:
                continue
            coll_save.insert_one(i)
        except Exception as e:
            log.info(i)

