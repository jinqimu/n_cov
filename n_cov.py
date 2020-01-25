# -*- coding: utf-8 -*-
'''
感谢数据来源 @丁香园
调用API https://github.com/BlankerL/DXY-2019-nCoV-Crawler
希望大家贡献自己的一份力
jinqimu@outlook.com
'''

import requests
import json
import time
import sys
import os
import sqlite3


## Bark_url
Bark_urls = {
    # "xxxxxxxx"更改为自己iPhone设备的推送码

    ## Bark自带服务器地址
    ## 'https://api.day.app/xxxxxxxxxxxxxxxxxxxxxxxxx/',

    ## jinqimu的服务器地址
    ## 'http://47.100.90.173:8080/xxxxxxxxxxxxxxxxxxx/',
}
## 省份和城市（不要写“省”、“市”两字）
provinces = {
    '浙江',
    '河南'
}
cities = {
    '宁波',
    '台州',
    '郑州',
    '焦作'
}
## data_base_url
base = "http://lab.isaaclin.cn/nCoV/api/"


class redirect():
    content = ""

    def write(self, str):
        self.content += str

    def flush(self):
        self.content = ""


def re(conn):
    current = sys.stdout
    r = redirect()
    sys.stdout = r

    for province in provinces:
        cursor = conn.cursor()
        conn.text_factory = str

        params = "province="+province+"省"
        response = requests.get(base + "area", params=params)
        data = response.text
        data_dict = json.loads(data)
        results = data_dict["results"]

        ## 最新数据
        now_result = results[-1]

        c = cursor.execute("select * from table1 where time={} and province='{}'".format(
            now_result['updateTime'], now_result['provinceName']))
        ro = c.fetchall()
        # print(ro)
        if (len(ro) == 0):
            cursor.execute("insert into table1(time, province) values({}, '{}')".format(
                now_result['updateTime'], now_result['provinceName']))
            # print("2")
            cursor.close()
            conn.commit()
            conn.text_factory = str
            res = {
                '数据更新时间': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_result['updateTime']/1000)),
                '省份': now_result['provinceName'],
                '确诊人数': now_result['confirmedCount'],
                '疑似感染人数': now_result['suspectedCount'],
                '治愈人数': now_result['curedCount'],
                '死亡人数': now_result['deadCount'],
            }

            print(res)

            print('\n其中：', end='  \n')

            city_result = now_result['cities']

            for i in city_result:
                if (i['cityName'] in cities):
                    res = {
                        '\n**城市': i['cityName']+'**',
                        '* 确诊人数': i['confirmedCount'],
                        '* 疑似感染人数': i['suspectedCount'],
                        '* 治愈人数': i['curedCount'],
                        '* 死亡人数': i['deadCount'],
                    }
                    for key in res:
                        print('  ' + key + '：' + str(res[key]), end='  \n')
                    print("")

    sys.stdout = current
    if(r.content != ""):
        bark_t = {'title': '疫情报告！', 'body': r.content}
        for url in Bark_urls:
            requests.post(url, bark_t)


if __name__ == "__main__":
    work_dir = os.path.split(os.path.realpath(__file__))[0]

    conn = sqlite3.connect(os.path.join(work_dir, 'n_cov.db'))
    conn.text_factory = str
    conn.execute(
        "create table if not exists table1(time int key UNIQUE NOT NULL, province text(100) NOT NULL)")

    print("Running now!")
    while(1):
        re(conn)
        time.sleep(60*10)
