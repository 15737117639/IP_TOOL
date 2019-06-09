import redis
from random import choice

MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10
REDIS_HOST = "localhost"
REDIS_PORT = 6379
DB_NUM = 4
REDIS_KEY = 'proxies'


class PoolEmptyError(Exception):
    """自定义ip代理池为空异常"""
    pass


class RedisClient(object):
    """redis数据库客户端类"""

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=DB_NUM):
        """
        初始化
        :param host:Redis 地址
        :param port: Redis 端口
        :param db: Redis 数据库
        """
        self.db = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为初始分数
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, {proxy: score})

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果最高分数不存在，则按照排名获取，否则异常
        :return:随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

    def decrease(self, proxy):
        """
        代理值减一分，分数小于最小值，则代理删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(REDIS_KEY, -1, proxy)
        else:
            print("代理", proxy, "当前分数", score, "移除")
            return self.db.zrem(REDIS_KEY, proxy)

    def exits(self, proxy):
        """
        判断proxy是否存在
        :param proxy: 代理
        :return:是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) is None

    def max(self, proxy):
        """
        将代理在设置为MAX_SCORE
        :param proxy:
        :return:
        """
        print("代理", proxy, "可用, 设置为", MAX_SCORE)
        return self.db.zadd(REDIS_KEY, {proxy:MAX_SCORE})

    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE, withscores=True)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop - 1)


if __name__ == '__main__':
    a = RedisClient()
    # a.add("18218299:415")
    # a.decrease("18218299:415")
    # print(a.random())
    # print(a.exits("18218299:413"))
    a.max("18218299:415")
    print(a.count())
    print(a.all())
