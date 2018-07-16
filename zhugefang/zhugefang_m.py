import requests
from lib.mongo import Mongo
from lxml import  etree
import re
import json
import demjson
import datetime
import time
import random
from multiprocessing import Process

m = Mongo('192.168.0.235', 27017)

zhuge = m.connect['comm_price']
coll = zhuge['zhugefang']
class Zhugefang_m():
    def __init__(self):
        self.start_url = 'http://m.zhugefang.com'
        self.headers = {'User-Agent':
                'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                        # 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        }
        self.proxies = [{"http":"http://192.168.0.96:4234"},
                        {"http":"http://192.168.0.93:4234"},
                        {"http":"http://192.168.0.90:4234"},
                        {"http":"http://192.168.0.94:4234"},
                        {"http": "http://192.168.0.98:4234"},
                        {"http": "http://192.168.0.99:4234"},
                        {"http": "http://192.168.0.100:4234"},
                        {"http": "http://192.168.0.101:4234"},
                        {"http": "http://192.168.0.102:4234"},
                        {"http": "http://192.168.0.103:4234"},]

    def crawler(self):
        res = requests.get(self.start_url,headers=self.headers)
        html = etree.HTML(res.text)
        city_list = html.xpath("//li[@class='border-bottom-eeeeee']")
        for city in city_list:
            city_name = city.xpath("./a/text()")[0]
            city_code = city.xpath("./a/@href")[0]
            # self.community(city_name,city_code)
            # self.new_house(city_name,city_code)
            p1 = Process(target=self.community,args=((city_name,city_code)))
            p2 = Process(target=self.new_house,args=((city_name,city_code)))
            p1.start()
            p2.start()
            p1.join()
            p2.join()

    def community(self,city_name,city_code):

        comm_url = self.start_url + city_code + '/house/community'
        s = requests.session()
        res = s.get(comm_url,headers=self.headers,)
        html = etree.HTML(res.text)
        count = html.xpath("//span[@class='count_p']/text()")[0]

        headers = s.headers
        i = 0
        num = 1

        while num <= int(count):
            data = {
                "num":num,
                "isArea":'false',
                "isRecommend":0,
            }
            url = 'http://m.zhugefang.com/get/xqlistHtml'
            retry_time = 0
            while True:
                try:
                    proxy = self.proxies[random.randint(0, 9)]
                    co_res = s.post(url,data=data,headers=headers,proxies=proxy,timeout=10)
                    if co_res.status_code == 200 :
                        con_dict = json.loads(co_res.text)
                        break
                    elif retry_time == 10:
                        break
                    else:
                        retry_time += 1
                        continue
                except Exception as e:
                    print("retry connection",e)
                    retry_time += 1
                    continue
            # print(co_res.text)

            co_str = con_dict["html"]
            co = re.findall('<a(.*?)</a>', co_str, re.S | re.M)
            for m in co:
                try:
                    co_name = re.search('<b>(.*?)</b', m, re.S | re.M).group(1)
                    co_price = re.search('price-title">(.*?)<', m, re.S | re.M).group(1)
                    co_price_measure = re.search('<strong>(.*?)</', m, re.S | re.M).group(1)
                    co_addr = re.search('p1">.*?(.*?)/',co_str,re.S|re.M).group(1)
                    time = datetime.datetime.now()
                    city = city_name
                    # co_id = re.search('(\d+).html',co_str,re.S|re.M).group(1)
                    coll.insert_one(
                        {'comm_name': co_name, 'comm_addr': co_addr,
                         'time':time, 'price': co_price, 'city': city,'measure':co_price_measure})
                except Exception as e:
                    print("小区提取错误",e)
                    continue

            i += 1
            num = 10*i + 1
            print("{}已爬取总数{}".format(city_name,num))

    def new_house(self,city_name,city_code):
        comm_url = self.start_url + city_code + "/newhouse"
        s = requests.session()
        res = s.get(comm_url, headers=self.headers)
        html = etree.HTML(res.text)
        count = html.xpath("//b[@class='count_p']/text()")[0]

        headers = s.headers
        i = 0
        num = 1
        while num <= int(count):
            data = {
                "num":num,
                "isArea":'false',
                "isRecommend":0,
            }
            url = 'http://m.zhugefang.com/get/xqlistHtml'

            while True:
                try:
                    proxy = self.proxies[random.randint(0, 9)]
                    co_res = s.post(url, data=data, headers=headers, proxies=proxy, timeout=10)
                    if co_res.status_code == 200 :
                        con_dict = json.loads(co_res.text)
                        break
                    else:
                        continue
                except Exception as e:
                    print("retry connection",e)
                    continue
            co_str = con_dict["html"]
            co = re.findall('<a(.*?)</a>',co_str,re.S|re.M)
            for m in co:
                try:
                    co_name = re.search('<b>(.*?)</b',m,re.S|re.M).group(1)
                    co_price = re.search('price-title">(.*?)<',m,re.S|re.M).group(1)
                    co_price_measure = re.search('<strong>(.*?)</',m,re.S|re.M).group(1)
                    co_addr = re.search('p1">.*?(.*?)/', co_str, re.S | re.M).group(1)
                    time = datetime.datetime.now()
                    city = city_name
                    # co_id = re.search('(\d+).html', co_str, re.S | re.M).group(1)
                    co_type = 'new'
                    coll.insert_one(
                        {'comm_name': co_name,'comm_addr': co_addr,
                         'time': time, 'price': co_price, 'city': city, 'measure': co_price_measure
                         ,'type':co_type})
                except Exception as e:
                    print("新小区错误",e)
                    continue
            i += 1
            num = 10 * i + 1
            print("{}新小区已爬取总数{}".format(city_name,num))

if __name__ == '__main__':
    zhuge = Zhugefang_m()
    zhuge.crawler()
