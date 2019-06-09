from utils import get_page
import re
from pyquery import PyQuery as pq
from db import RedisClient


class ProxyMetaclass(type):
    """
    定义元类, 给类添加俩私有类属性__CrawlFunc__, __CrawlFuncCount__
    :return 类创建的引用
    """
    def __new__(cls, name, base, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs["__CrawlFuncCount__"] = count
        return type.__new__(cls, name, base, attrs)


class Crawler(object, metaclass=ProxyMetaclass):
    """
    爬虫类定义
    """
    def get_proxies(self, callback):
        """
        通过crawl获取的到的代理添加到proxies列表中，并返回，这里用到了协程
        :param callback: 下面的crawl_daili66
        :return:
        """
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print("成功获取到代理", proxy)
            proxies.append(proxy)
        return proxies

    def crawl_daili66(self, page_count=20):
        """
        66快代理
        :param page_count:
        :return:
        """
        start_url = 'http://www.66ip.cn/{}.html'
        headers = {
            "Cookie": "__jsluid=d67ba1bf483046976b81a6b33a372b1c; Hm_lvt_1761fabf3c988e7f04bec51acd4073f4=1555505708; Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4=1555508780",
            "Host": "www.66ip.cn",
        }
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        count = page_count
        for url in urls:
            headers_referer = {
                "Referer": "http://www.66ip.cn/{}".format(count - page_count + 1)
            }
            headers.update(headers_referer)
            page_count -= 1
            html = get_page(url, options=headers)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ":".join([ip, port])

    def crawl_kuaidaili(self):
        """
        快代理
        :return:
        """
        for i in range(1, 20):
            start_url = 'http://www.kuaidaili.com/free/inha/{}/'.format(i)
            html = get_page(start_url)
            if html:
                ip_address = re.compile('<td data-title="IP">(.*?)</td>')
                re_ip_address = ip_address.findall(html)
                port = re.compile('<td data-title="PORT">(.*?)</td>')
                re_port = port.findall(html)
                for address, port in zip(re_ip_address, re_port):
                    address_port = address + ':' + port
                    yield address_port.replace(' ', '')

    def crawl_ip3366(self):
        """
        云代理
        :return:
        """
        for page in range(4, 20):
            start_url = 'http://www.ip3366.net/free/?stype=1&page={}'.format(page)
            html = get_page(start_url)
            ip_address = re.compile('<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            # \s * 匹配空格，起到换行作用
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield result.replace(' ', '')

    def crawl_xicidaili(self):
        """
        国内高匿代理IP
        :return:
        """
        for i in range(1, 20):
            start_url = 'http://www.xicidaili.com/nn/{}'.format(i)
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cookie': "_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTcwNzA3MGExODhmY2NjYzAxMzgwNjg0NWZkNGM5MzNkBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUdHMUlnQWlWemwxNjJDNFBqek1zTzd1emtKQkZXR2RjWUZOakgvTmZmUkU9BjsARg%3D%3D--9d6b39b7f78c7ddb4c74b778a3e16731fcaa6526; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1555507341,1555810659,1556011081,1556093193; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1556093193",
                'Host': 'www.xicidaili.com',
                'Referer': 'http://www.xicidaili.com/nn/3',
                'Upgrade-Insecure-Requests': '1',
            }
            html = get_page(start_url, options=headers)
            if html:
                find_trs = re.compile('<tr class.*?>(.*?)</tr>', re.S)
                trs = find_trs.findall(html)
                for tr in trs:
                    find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
                    re_ip_address = find_ip.findall(tr)
                    find_port = re.compile('<td>(\d+)</td>')
                    re_port = find_port.findall(tr)
                    for address, port in zip(re_ip_address, re_port):
                        address_port = address + ':' + port
                        yield address_port.replace(' ', '')

    def crawl_iphai(self):
        """ip海"""
        start_url = 'http://www.iphai.com/'
        html = get_page(start_url)
        if html:
            find_tr = re.compile('<tr>(.*?)</tr>', re.S)
            trs = find_tr.findall(html)
            for s in range(1, len(trs)):
                find_ip = re.compile('<td>\s+(\d+\.\d+\.\d+\.\d+)\s+</td>', re.S)
                re_ip_address = find_ip.findall(trs[s])
                find_port = re.compile('<td>\s+(\d+)\s+</td>', re.S)
                re_port = find_port.findall(trs[s])
                for address, port in zip(re_ip_address, re_port):
                    address_port = address + ':' + port
                    yield address_port.replace(' ', '')

    def crawl_data5u(self):
        """无忧代理"""
        start_url = 'http://www.data5u.com/free/gngn/index.shtml'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=47AA0C887112A2D83EE040405F837A86',
            'Host': 'www.data5u.com',
            'Referer': 'http://www.data5u.com/free/index.shtml',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }
        html = get_page(start_url, options=headers)
        if html:
            ip_address = re.compile('<span><li>(\d+\.\d+\.\d+\.\d+)</li>.*?<li class=\"port.*?>(\d+)</li>', re.S)
            re_ip_address = ip_address.findall(html)
            for address, port in re_ip_address:
                result = address + ':' + port
                yield result.replace(' ', '')


if __name__ == "__main__":
    c = Crawler()
    print(c.get_proxies("crawl_iphai"))
