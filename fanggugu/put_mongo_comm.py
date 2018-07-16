# from lib.rabbitmq import Rabbit
# from lib.mongo import Mongo
# import json
#
# m = Mongo('192.168.0.235', 27017)
# coll = m.connect['fgg']['fanggugu_price']
#
# r = Rabbit('192.168.0.190', 5673)
# channel = r.get_channel()
#
# for i in coll.find({}, no_cursor_timeout=True):
#     ResidentialAreaID = i['ResidentialAreaID']
#     city_name = i['city_name']
#     name = i['baseinfo']['json'][0]['residentialareaMap']['residentialareaName']
#     data = {
#         'ResidentialAreaID': ResidentialAreaID,
#         'city_name': city_name,
#         'name': name,
#     }
#     print(data)
#     channel.queue_declare(queue='fgg_all_city_code')
#     channel.basic_publish(exchange='',
#                           routing_key='fgg_all_city_code',
#                           body=json.dumps(data))

from fanggugu.comm_dict import comm_dict
from lib.rabbitmq import Rabbit
import json

r = Rabbit('192.168.0.190', 5673)
channel = r.get_channel()

for i in comm_dict:
    city_name = i[0]
    name = i[2]
    ResidentialAreaID = i[3]
    data = {
        'ResidentialAreaID': ResidentialAreaID,
        'city_name': city_name,
        'name': name,
    }
    print(data)
    channel.queue_declare(queue='fgg_all_city_code')
    channel.basic_publish(exchange='',
                          routing_key='fgg_all_city_code',
                          body=json.dumps(data))
