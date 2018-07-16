"""
房估估开启文件
"""
from fanggugu.fgg_real_time_price import consume_queue
from lib.mongo import Mongo
from multiprocessing import Process

# # 放入队列
# u.put_rabbit()

# 链接 MongoDB
m = Mongo('192.168.0.235', 27017)
fgg = m.connect['fgg']
coll_user = fgg['user_info']

if __name__ == '__main__':
    # 开启房估估均价队列
    for i in coll_user.find():
        user = i['user_name']
        print('user', user)
        consume_queue(user)
        break
        # Process(target=consume_queue, args=(user,)).start()

