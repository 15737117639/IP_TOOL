import requests
from lxml import etree
import re
import redis
from crawler import Crawler


class Redis_Client():
    def __init__(self):
        self.db = redis.StrictRedis(host='localhost', port=6379, db=4, decode_responses=True)

    def add(self, proxy, score=100):
        """
        添加代理，设置分数为初始分数
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not self.db.zscore("proxies", proxy):
            return self.db.zadd("proxies", {proxy: score})


def main():
    c = Crawler()
    a = Redis_Client()
    for ip in c.get_proxies("crawl_xicidaili"):
        print(ip)
        a.add(proxy=ip)


if __name__ == '__main__':
    main()
