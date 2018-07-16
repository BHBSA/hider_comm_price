"""
房估估的登录
"""
import requests
from lib.mongo import Mongo
import random

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


class Login(object):
    def __init__(self):
        m = Mongo('192.168.0.235', 27017)
        self.connection = m.get_connection()

    def to_request(self, user_name):
        s = requests.session()
        parms = {'pwd_login_username': user_name,
                 'pwd_login_password': '4ac9fa21a775e4239e4c72317cdca870',
                 'remembermeVal': 0}
        while True:
            ip = random.choice(IPS)
            proxies = {'http': ip}
            try:
                s.post(url='http://www.fungugu.com/DengLu/doLogin_noLogin', data=parms,
                       proxies=proxies, timeout=15)
                jrbqiantai = s.cookies.get_dict()['jrbqiantai']
                return jrbqiantai
            except Exception as e:
                print(e)

    def put_mongo(self):
        coll_login = self.connection['fgg']['login']
        coll_user = self.connection['fgg']['user_info']
        for i in coll_user.find():
            user_name = i['user_name']
            jrbqiantai = self.to_request(user_name)
            data = {
                'user_name': user_name,
                'jrbqiantai': jrbqiantai
            }
            coll_login.update({'user_name': user_name}, {'$set': data}, True)
            print('cookie', jrbqiantai)
        return 200

    def update_mongo(self, user_name):
        coll_login = self.connection['fgg']['login']
        jrbqiantai = self.to_request(user_name)
        data = {
            'user_name': user_name,
            'jrbqiantai': jrbqiantai
        }
        coll_login.update({'user_name': user_name}, {'$set': data})
        jrbqiantai = coll_login.find_one({'user_name': user_name})['jrbqiantai']
        return jrbqiantai


if __name__ == '__main__':
    login = Login()
    login.put_mongo()
