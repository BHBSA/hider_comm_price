"""
    实时的更新小区均价
    <<<新页面，cookie已更新，需要重新开发>>>
"""

import json, requests, datetime
from lib.mongo import Mongo
from lib.rabbitmq import Rabbit
from fanggugu.login_fgg import Login
import random
import yaml

setting = yaml.load(open('config.yaml'))

# 链接 MongoDB
m = Mongo(setting['fgg_price_mongo']['host'], setting['fgg_price_mongo']['port'])

fgg = m.connect[setting['fgg_price_mongo']['db']]
coll = fgg[setting['fgg_price_mongo']['coll_fanggugu_price']]

fgg = m.connect[setting['fgg_price_mongo']['db']]
coll_test = fgg[setting['fgg_price_mongo']['coll_fanggugu_price_update']]

fgg = m.connect[setting['fgg_price_mongo']['db']]
coll_user = fgg[setting['fgg_price_mongo']['coll_user_info']]

fgg = m.connect[setting['fgg_price_mongo']['db']]
coll_login = fgg[setting['fgg_price_mongo']['coll_login']]

# 链接 rabbit
r = Rabbit(setting['fgg_price_rabbit']['host'], setting['fgg_price_rabbit']['port'], )

channel = r.get_channel()
channel.queue_declare(queue='fgg_comm_id')

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


def put_rabbit():
    # 从price表中查id和城市放入rabbit
    for i in coll.find():
        ResidentialAreaID = i['ResidentialAreaID']
        city_name = i['city_name']
        data = {
            'ResidentialAreaID': ResidentialAreaID,
            'city_name': city_name,
        }
        channel.basic_publish(exchange='',
                              routing_key='fgg_comm_id',
                              body=json.dumps(data))
        print(data)


def request_post(url, headers, city_name, ResidentialAreaID, user_name):
    querystring = {
        'CityName': city_name,
        'ResidentialAreaID': ResidentialAreaID
    }
    while True:
        # ip = random.choice(IPS)
        ip = '118.114.77.47:8080'
        proxies = {'http': ip, 'https': ip}
        try:
            result = requests.post(url=url, headers=headers, data=querystring,
                                   proxies=proxies, timeout=15)
            # 登录失效，重新登录
            if 'login' in result.text:
                jrbqiantai = login.update_mongo(user_name)
                headers['Cookie'] = 'jrbqiantai=' + jrbqiantai
                result = requests.post(url=url, headers=headers, data=querystring,
                                       proxies=proxies, timeout=15)
            if 'UnitPrice' in result.text:
                print('ip can use')
                return result
            else:
                print('错误')

        except Exception as e:
            print(e)


def start_community_info(ch, method, properties, body):
    user_name = method.consumer_tag
    jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
    headers = {
        'Cookie': 'jrbqiantai=' + jrbqiantai,
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Content-Length': "51",
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Host': "www.fungugu.com",
        'Origin': "http://www.fungugu.com",
        'Proxy-Connection': "keep-alive",
        'Referer': "http://www.fungugu.com/JinRongGuZhi/toJinRongGuZhi_s?xqmc=%E4%B8%9C%E8%8B%91%E7%BB%BF%E4%B8%96%E7%95%8C%E4%B8%89%E6%9C%9F&gjdx=%E4%B8%9C%E8%8B%91%E7%BB%BF%E4%B8%96%E7%95%8C%E4%B8%89%E6%9C%9F&residentialName=%E4%B8%9C%E8%8B%91%E7%BB%BF%E4%B8%96%E7%95%8C%E4%B8%89%E6%9C%9F&realName=%E4%B8%9C%E8%8B%91%E7%BB%BF%E4%B8%96%E7%95%8C%E4%B8%89%E6%9C%9F&dz=%E4%B8%9C%E8%8B%91%E7%BB%BF%E4%B8%96%E7%95%8C%E4%B8%89%E6%9C%9F&xzq=%E9%97%B5%E8%A1%8C%E5%8C%BA&xqid=27396&ldid=&dyid=&hid=&loudong=&danyuan=&hu=&retrievalMethod=%E6%99%AE%E9%80%9A%E6%A3%80%E7%B4%A2&originalInputItem=%E4%B8%9C%E8%8B%91%E7%BB%BF%E4%B8%96%E7%95%8C%E4%BA%8C&address=&source=&guid=c3178d4f-292c-11e5-ac2c-288023a0e898",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        'X-Requested-With': "XMLHttpRequest",
    }
    body_dict = json.loads(body.decode())
    city_name = body_dict['city_name']
    name = body_dict['name']
    ResidentialAreaID = body_dict['ResidentialAreaID']
    print(city_name, ResidentialAreaID, name)
    try:
        url = 'http://www.fungugu.com/JinRongGuZhi/getXiaoQuJiChuXinXi'
        response = request_post(url, headers, city_name, ResidentialAreaID, user_name)
        data = json.loads(response.text)
        data['ResidentialAreaID'] = ResidentialAreaID
        data['city_name'] = city_name
        data['update_time'] = datetime.datetime.now()
        data['name'] = name
        print(data)
        coll_test.update({'city_name': city_name, 'ResidentialAreaID': ResidentialAreaID}, {'$set': data}, True)
        # 挑出
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print('页面错误')
        channel.basic_publish(exchange='',
                              routing_key='fgg_all_city_code',
                              body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_queue(name):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(consumer_callback=start_community_info, queue='fgg_all_city_code',
                          consumer_tag=name)
    channel.start_consuming()
