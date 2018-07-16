import json
import requests
import random
from fanggugu.login_fgg import Login
from lib.rabbitmq import Rabbit
from lib.mongo import Mongo
import datetime
import yaml

setting = yaml.load(open('config.yaml'))

# 连接 MongoDB
m = Mongo(setting['comm_price']['host'], setting['comm_price']['port'])
fgg = m.connect[setting['comm_price']['db']]
coll = fgg[setting['comm_price']['fgg_coll']]

coll_login = fgg[setting['fgg']['user_info']]

# 连接rabbit
r = Rabbit('192.168.0.235', 5673)
channel = r.get_channel()

IPS = ["192.168.0.90:4234",
       "192.168.0.93:4234",
       "192.168.0.94:4234",
       "192.168.0.96:4234",
       "192.168.0.98:4234",
       "192.168.0.99:4234",
       "192.168.0.100:4234",
       "192.168.0.101:4234",
       "192.168.0.102:4234",
       "192.168.0.103:4234"]

login = Login()


def request_post(url, headers, city_name, ResidentialAreaID, user_name):
    querystring = {
        'CityName': city_name,
        'ResidentialAreaID': ResidentialAreaID
    }
    while True:
        ip = random.choice(IPS)
        proxies = {'http': ip}

        result = requests.post(url=url, headers=headers, data=querystring,
                               proxies=proxies, timeout=5)
        # 登录失效，重新登录
        if 'login' in result.text:
            jrbqiantai = login.update_mongo(user_name)
            headers['Cookie'] = 'jrbqiantai=' + jrbqiantai
            result = requests.post(url=url, headers=headers, data=querystring,
                                   proxies=proxies, timeout=5)
        if 'UnitPrice' in result.text:
            print('ip can use')
            return result
        else:
            print('错误')


def req_price(user_name, city_name, ResidentialAreaID):
    jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
    headers = {
        'Cookie': 'jrbqiantai=' + jrbqiantai,
        'Referer': 'http://www.fungugu.com/',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
    }
    try:
        url = 'http://www.fungugu.com/JinRongGuZhi/getXiaoQuJiChuXinXi'
        response = request_post(url, headers, city_name, ResidentialAreaID, user_name)
        data = json.loads(response.text)
        data['ResidentialAreaID'] = ResidentialAreaID
        data['city_name'] = city_name
        data['update_time'] = datetime.datetime.now()
        print(data)
        coll.update({'city_name': city_name, 'ResidentialAreaID': ResidentialAreaID}, {'$set': data})
    except Exception as e:
        return False


def callback(ch, method, properties, body):
    user_name = method.consumer_tag
    dict_body = json.loads(body)
    city_name = dict_body['city_name']
    ResidentialAreaID = dict_body['city_num']
    can = coll.find_one({'city_name': city_name, 'ResidentialAreaID': ResidentialAreaID})
    if can:
        code = req_price(user_name, city_name, ResidentialAreaID)
        # todo 判断comm_id错误还是ip错误，ip错误就放回队列，comm_id错误就直接扔掉
        # if not code:
        #     print('页面错误')
        #     channel.basic_publish(exchange='',
        #                           routing_key='fgg_all_city_code',
        #                           body=body,
        #                           )
        #     ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        # todo 没有查到库，就请求小区详情和小区均价
        pass


# name 为fgg登录的用户名
def consume_queue(name):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=callback, queue='fgg_all_city_code',
                          consumer_tag=name)
    channel.start_consuming()
