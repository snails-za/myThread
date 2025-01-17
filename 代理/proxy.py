"""
案例名称：学习使用ip代理池
需求：从网上找一个代理ip的网站，然后获取网站上的
100个ip，组成代理ip池，然后随机抽取其中一个ip，
并对该ip进行连通性测试，如果该ip可以，我们可以将
该ip作为代理ip来使用

思路：
    1，先获取西刺代理网站上的ip(100)
    2, 随机抽取其中一个ip，并检测其连通性
    3，如果该ip可用，则可以作为代理ip使用
编码：
测试：
"""

import requests
from bs4 import BeautifulSoup
from lxml import etree
import subprocess as sp
import random
import re


"""
函数说明:获取代理ip网站的ip
"""
def get_proxys(page):
    #requests的Session()可以自动保存cookie，
    #不需要自己维护cookie内容
    S = requests.Session()
    #目标网址的url
    target_url = 'http://www.xicidaili.com/nn/%d' %page
    target_headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://www.xicidaili.com/nn/',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    target_response = S.get(url=target_url,
                            headers=target_headers)
    target_response.encoding = 'utf-8'
    target_html = target_response.text
    # print(target_html)

    #解析数据（ip,port,protocol）
    bf1_ip_list = BeautifulSoup(target_html,'lxml')
    bf2_ip_list = BeautifulSoup(str(bf1_ip_list.find_all(id='ip_list')),'lxml')
    ip_list_info = bf2_ip_list.table.contents

    proxys_list = []
    for index in range(len(ip_list_info)):
        if index % 2 == 1 and index != 1:
            dom = etree.HTML(str(ip_list_info[index]))
            ip = dom.xpath('//td[2]')
            port = dom.xpath('//td[3]')
            protocol = dom.xpath('//td[6]')
            proxys_list.append(protocol[0].text.lower()
                               + "#" + ip[0].text
                               + "#" + port[0].text)
    return proxys_list

"""
函数说明:检测代理ip的连通性
参数:
    ip--代理的ip地址
    lose_time--匹配的丢包数
    waste_time--匹配平均时间
返回值:
    average_time--代理ip的平均耗时
"""
def check_ip(ip, lose_time, waste_time):
    cmd = "ping -n 3 -w 3 %s"
    #执行命令
    p = sp.Popen(cmd %ip, stdin=sp.PIPE,
                 stdout=sp.PIPE,
                 stderr=sp.PIPE,
                 shell=True)
    #获取返回结果并解码
    out = p.stdout.read().decode('GBK')
    lose_time = lose_time.findall(out)

    if len(lose_time) == 0:
        lose = 3
    else:
        lose = int(lose_time[0])
    #如果丢包数大于2，那么我们返回平均耗时1000
    if lose > 2:
        #返回false（1000）
        return 1000
    else:
        #平均时间
        average = waste_time.findall(out)
        if len(average) == 0:
            return 1000
        else:
            average_time = int(average[0])
            #返回平均耗时
            return average_time


"""
函数说明:初始化正则表达式
返回值:
    lose_time--匹配丢包数
    waste_time--匹配平均时间
"""
def initpattern():
    #匹配丢包数
    lose_time = re.compile(u"丢失 = (\d+)",re.IGNORECASE)
    #匹配平均时间
    waste_time = re.compile(u"平均 = (\d+)ms",re.IGNORECASE)
    return lose_time, waste_time


if __name__ == '__main__':
    #初始化正则表达式
    lose_time, waste_time = initpattern()
    #获取ip代理
    proxys_list = get_proxys(1)


    #如果平均时间超过200ms，则重新选取ip
    while True:
        #从100个ip中随机选取一个ip作为代理进行网络访问
        proxy = random.choice(proxys_list)
        split_proxy = proxy.split('#')
        #获取ip
        ip = split_proxy[1]
        #检查ip
        average_time = check_ip(ip, lose_time, waste_time)

        if average_time > 200:
            #去掉不能使用的ip
            proxys_list.remove(proxy)
            print("ip链接超时，重新获取中...")
        else:
            break

    proxys_list.remove(proxy)
    proxys_dict = {split_proxy[0]:split_proxy[1]
                    + ":" + split_proxy[2]}
    print("使用代理:", proxys_dict)