import aiohttp
from db import RedisClient
import asyncio
import aiohttp
import time
import sys


VALID_STATUS_CODES = [200]
test_url = 'http://httpbin.org/ip'
BATCH_TEST_SIZE = 100


class Tester(object):
    """检测代理是否能行"""
    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self, proxy):
        """
        测试当个代理
        :param proxy:代理
        :return: Ｎｏｎｅ
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)  # 防止ssl报错
        async with aiohttp.ClientSession(connector=conn) as session:  # 创建session
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = "http://" + proxy
                print("正在尝试:", real_proxy)
                async with session.get(test_url, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print("代理可用", proxy)
                    else:
                        self.redis.decrease(proxy)
                        print("请求响应不合法", proxy)
            except Exception as e:
                self.redis.decrease(proxy)
                print("代理请求失败", proxy, e.args)

    def run(self):
        """
        测试主函数
        :return:
        """
        print('测试器开始运行')
        try:
            count = self.redis.count()
            print('当前剩余', count, '个代理')
            for i in range(0, count, BATCH_TEST_SIZE):
                start = i
                stop = min(i + BATCH_TEST_SIZE, count)
                print('正在测试第', start + 1, '-', stop, '个代理')
                test_proxies = self.redis.batch(start, stop)
                loop = asyncio.get_event_loop()
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)


if __name__ == '__main__':
    a = Tester()
    a.run()
