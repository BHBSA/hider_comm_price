from login_fgg import Login
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
import random
import json
import requests

r = Rabbit('192.168.0.190', 5673)
connection = r.connection
channel = connection.channel()
channel.queue_declare(queue='fgg_all_city_code')

m = Mongo('192.168.0.235', 27017)
connect = m.connect
coll = connect['fgg']['user_info']

login = Login()

ips = [
    "192.168.0.90:4234",
    "192.168.0.93:4234",
    "192.168.0.94:4234",
    "192.168.0.96:4234",
    "192.168.0.98:4234",
    "192.168.0.99:4234",
    "192.168.0.100:4234",
    "192.168.0.101:4234",
    "192.168.0.102:4234",
    "192.168.0.103:4234"
]

known = '上海 35484,北京 20866,广州 16641,深圳 23559,大连 20751,厦门 15265,银川 17000,成都 13000,杭州 13000'


def put_queue_comm_id():
    headers = {
        'Cookie': 'jrbqiantai=F7CC7B6CB3323E1BDFECFFEEE4B829E1',
        'Referer': 'http://www.fungugu.com/JinRongGuZhi/toIndex',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
    }
    url = 'http://www.fungugu.com/api/findChengShiLink'
    for i in coll.find():
        user = i['user_name']
        print(user)
        jrbqiantai = login.update_mongo(user)
        headers['Cookie'] = 'jrbqiantai=' + jrbqiantai
        ip = random.choice(ips)
        proxies = {
            'http': ip
        }
        response = requests.post(url=url, headers=headers, proxies=proxies)
        if 'MingCheng' in response.text:
            json_ = json.loads(response.text)
            for i in json_['data']:
                data = i['data']
                for i in data:
                    dict_ = {}
                    city_name = i['MingCheng']
                    if city_name in ['上海', '北京']:
                        for i in range(0, 40000):
                            dict_['city_num'] = i
                            dict_['city_name'] = city_name
                            print(dict_)
                            channel.basic_publish(exchange='',
                                                  routing_key='fgg_all_city_code',
                                                  body=json.dumps(dict_))
                    elif city_name in ['深圳', '大连']:
                        for i in range(0, 25000):
                            dict_['city_num'] = i
                            dict_['city_name'] = city_name
                            print(dict_)
                            channel.basic_publish(exchange='',
                                                  routing_key='fgg_all_city_code',
                                                  body=json.dumps(dict_))
                    elif city_name in ['广州', '厦门', '银川']:
                        for i in range(0, 25000):
                            dict_['city_num'] = i
                            dict_['city_name'] = city_name
                            print(dict_)
                            channel.basic_publish(exchange='',
                                                  routing_key='fgg_all_city_code',
                                                  body=json.dumps(dict_))
                    elif city_name in ['杭州', '成都']:
                        for i in range(0, 13000):
                            dict_['city_num'] = i
                            dict_['city_name'] = city_name
                            print(dict_)
                            channel.basic_publish(exchange='',
                                                  routing_key='fgg_all_city_code',
                                                  body=json.dumps(dict_))
                    else:
                        for i in range(0, 10000):
                            dict_['city_num'] = i
                            dict_['city_name'] = city_name
                            print(dict_)
                            channel.basic_publish(exchange='',
                                                  routing_key='fgg_all_city_code',
                                                  body=json.dumps(dict_))
            return


if __name__ == '__main__':
    put_queue_comm_id()
