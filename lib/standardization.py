"""
格式化城市区域
"""

import json

with open('lib/city.json', 'r+') as f:
    standard_city_dict = json.loads(f.read())
with open('lib/region.json', 'r+') as f:
    standard_block_dict = json.loads(f.read())


def standard_city(city_name):
    """

    :param city_name: 城市名称
    :return: 城市名称
    """
    for i in standard_city_dict.items():
        for city in i[1]:
            if city and i[0] in city_name:
                print(i[0])
                return i[0]
            else:
                continue
    print("无法标准化")
    return city_name


def standard_block(region_name):
    """

    :param region_name: 区域
    :return: 区域
    """
    for i in standard_block_dict.items():
        for block in i[1]:
            if block in region_name:
                # print(i[0])
                return i[0]
            else:
                continue
    print('无法标准化')
    # print(region_name)
    return region_name


if __name__ == '__main__':
    standard_city('   珠海市  ')
    standard_block('浦东新区            ')
