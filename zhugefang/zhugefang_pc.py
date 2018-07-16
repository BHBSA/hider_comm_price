import requests
from lib.mongo import Mongo
from lxml import  etree
import re
import datetime
import time
import random
from multiprocessing import Process
from proxy_connection import Proxy_contact

m = Mongo('192.168.0.235', 27017)

zhuge = m.connect['comm_price']
coll = zhuge['zhugefang']

class Zhugefang():
    def __init__(self):
        self.start_url = 'http://zhugefang.com'
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
        self.test_proxy = {
            "http": "http://192.168.0.94:4234"
        }
    def community(self):
        res = requests.get(self.start_url,headers=self.headers)
        html = etree.HTML(res.text)
        city_urllist = html.xpath("//ul[@style='width:1200px;']/li/a")
        city_urllist = sorted(city_urllist,key=city_urllist.index,reverse=True)
        for i in city_urllist:
            city_url = i.xpath("./@href")[0]
            comm_city = i.xpath("./text()")[0]
            city_comm = city_url+"/community"
            # while True:
            #     try:
                    # proxies = self.proxies[random.randint(0,9)]
                    # ci_res = requests.get(city_comm,headers=self.headers,proxies=proxies)
            proxy_page = Proxy_contact(app_name="zhuge", method='get', url=city_comm)
            ci_res = proxy_page.contact()
                    # if ci_res.status_code !=200:
                    #     print("{}小区请求失败，ip无效".format(comm_city))
                    #     continue
                    # else:
                    #     break
                # except Exception as e:
                #     print("{}小区请求失败".format(comm_city),e)
                #     continue
            page = re.findall('/community/page/(\d+)',ci_res.text)[-2]
            for i in range(1,int(page)+1):
                if i == 1:
                    url = city_comm
                else:
                    url = city_comm + "/page/" + str(i)
                # while True:
                #     try:
                #         proxies = self.proxies[random.randint(0, 9)]
                #         response = requests.get(url,headers=self.headers,proxies=proxies)
                #         if response.status_code !=200:
                #             continue
                #         else:
                #             break
                #     except Exception as e:
                #         print(e)
                #         continue
                proxy_page = Proxy_contact(app_name="zhuge", method='get', url=url)
                response = proxy_page.contact()

                con = response.text
                comm_html = etree.HTML(con)
                tag = comm_html.xpath("//ul[@id='listTableBox']/li")
                self.comm_info(tag,comm_city)

    def comm_info(self,tag,comm_city):
        for li in tag:
            try:
                comm_name = li.xpath(".//p[@class='house-name']/a/text()")[0]
                comm_str = etree.tounicode(li)
                comm_id = re.findall('href=.*?(\d+).html',comm_str,re.S|re.M)[0]
                try:
                    comm_addr = re.search('\](.*?)</p>',comm_str,re.S|re.M).group(1)
                    comm_area = re.search('\[(.*?)-',comm_str,re.S|re.M).group(1)
                except:
                    comm_area = None
                    comm_addr = re.search('adr f14">(.*?)</p',comm_str,re.S|re.M).group(1)
                date_time = datetime.datetime.now()
                comm_price = re.search('<span>(\d+)</span>(.*?)</p>',comm_str).group()
            except Exception as e:
                print("{}小区信息错误".format(comm_city),e)
                continue
            coll.insert_one({'comm_name':comm_name,'comm_id':comm_id,'comm_addr':comm_addr,'comm_area':comm_area,
                         'time':date_time,'price':comm_price,'city':comm_city})
            print("插入成功")

    def new_comm(self):
        res = requests.get(self.start_url, headers=self.headers)
        html = etree.HTML(res.text)
        city_urllist = html.xpath("//ul[@style='width:1200px;']/li/a")
        # print(city_urllist.index)
        city_urllist = sorted(city_urllist, key=city_urllist.index, reverse=True)
        for i in city_urllist:
            city_url = i.xpath("./@href")[0]
            comm_city = i.xpath("./text()")[0]
            city_comm = city_url.replace('.zhu','.newhouse.zhu')
            # try:
            #     while True:
            #         # proxies = self.proxies[random.randint(0, 9)]
            #         ci_res = requests.get(city_comm, proxies=self.test_proxy)
            #         if ci_res.status_code != 200:
            #             print("{}新房请求失败，ip无效".format(comm_city))
            #             continue
            #         else:
            #             break
            # except Exception as e:
            #     print("{}新房请求失败".format(comm_city),e)
            #     continue
            proxy_page = Proxy_contact(app_name="zhuge", method='get', url=city_comm)
            ci_res = proxy_page.contact()

            page = re.findall(';/page/(\d+)/&#34', ci_res.text)[-2]
            for i in range(1, int(page) + 1):
                if i == 1:
                    url = city_comm
                else:
                    url = city_comm + "/page/" + str(i)
                # while True:
                #     try:
                #         # proxies = self.proxies[random.randint(0, 9)]
                #         response = requests.get(url, headers=self.headers,proxies=self.test_proxy)
                #         if response.status_code !=200:
                #             continue
                #         else:
                #             break
                #     except Exception as e:
                #         print(e)
                #         continue
                proxy_page = Proxy_contact(app_name="zhuge", method='get', url=url)
                response = proxy_page.contact()

                con = response.text
                comm_html = etree.HTML(con)
                tag = comm_html.xpath("//div[@class='list']/div")[1:]
                self.new_comm_info(tag,comm_city)

    def new_comm_info(self,tag,comm_city):
        for li in tag:
            try:
                comm_name = li.xpath(".//span[@class='tit']/text()")[0]
                comm_str = etree.tounicode(li)
                comm_id = re.findall('href=.*?(\d+).html',comm_str,re.S|re.M)[0]
                try:
                    comm_addr = re.search('\](.*?)</div>',comm_str,re.S|re.M).group(1)
                    comm_area = li.xpath(".//a[@class='area_class']/text()")
                except:
                    comm_area = None
                    comm_addr = re.search('address">(.*?)</div',comm_str,re.S|re.M).group(1)
                date_time = datetime.datetime.now()
                comm_price = re.search('price">.*?<span>(.*?)</span>',comm_str,re.S|re.M).group(1)
                house_type = 'new'
            except Exception as e:
                print("{}新房信息错误".format(comm_city),e)
                continue
            coll.insert_one({'city':comm_city,'comm_name':comm_name,'comm_id':comm_id,'comm_addr':comm_addr,'comm_area':comm_area,
                            'time':date_time,'price':comm_price,'house_type':house_type})
            print("插入成功")


if __name__ == '__main__':
    zhuge = Zhugefang()
    Process(target=zhuge.new_comm).start()
    Process(target=zhuge.community).start()