# -*- coding: utf-8 -*-
import os
import time
import requests
import urllib
import threading
import socket
import sys
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")

target_url = []
aim_ip = []
for i in range(1, 2):
    url = 'http://www.xicidaili.com/nn/%d' % i
    target_url.append(url)

all_message = []


class ipGet(threading.Thread):
    def __init__(self, target):
        threading.Thread.__init__(self)
        self.target = target

    def Get_ip(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
        html = requests.get(self.target, headers=headers)
        soup = BeautifulSoup(html.text, "html.parser")
        trs = soup.find('table', id='ip_list').find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            ip = tds[1].text.strip()
            opening = tds[2].text.strip()
            message = [ip, opening]
            all_message.append(message)
            #print ip, opening

    def run(self):
        self.Get_ip()


class ipCheck(threading.Thread):
    def __init__(self, ipList):
        threading.Thread.__init__(self)
        self.ipList = ipList
        self.timeout = 3
        self.test_url = 'http://www.jd.com/?cu=true&utm_source=click.linktech.cn&utm_medium=tuiguang&utm_campaign=t_4_A100220955&utm_term=7e7c13a102664ab3a6886ccefa66d930&abt=3'
        self.another_url = 'https://www.taobao.com/'

    def Check_ip(self):
        socket.setdefaulttimeout(3)
        for ip in self.ipList:
            try:
                proxy_host = "http://" + ip[0] + ":" + ip[1]
                proxy_temp = {"http": proxy_host}
                t_start = time.time()
                res = urllib.urlopen(self.test_url, proxies=proxy_temp).read()
                res2 = urllib.urlopen(self.another_url, proxies=proxy_temp).read()
                t_use = time.time() - t_start
                soup = BeautifulSoup(res, "html.parser")
                soup2 = BeautifulSoup(res2, "html.parser")
                ans = soup.find('link', rel='dns-prefetch')
                ans2 = soup2.find('link', rel='dns-prefetch')
                if ans != None and ans2 != None:
                    aim_ip.append((ip[0].encode("utf-8"), ip[1].encode("utf-8")))
                else:
                    continue
            except Exception, e:
                continue

    def run(self):
        self.Check_ip()


class save_csv():
    def __init__(self, SaveList):
        self.savelist = SaveList

    def Save_ip(self):
        counts = 0
        BASE_DIR = os.path.dirname(__file__)
        file_path = os.path.join(BASE_DIR, 'Proxyips.txt')
        f=open(file_path, 'w+')
        for each in self.savelist:
            f.write(each.__str__())
            f.write('\n')
            counts += 1
        return counts


if __name__ == '__main__':
    GetThreading = []
    CheckThreading = []

    for i in range(len(target_url)):
        t = ipGet(target_url[i])
        GetThreading.append(t)
    for i in range(len(GetThreading)):
        GetThreading[i].start()
        print GetThreading[i].is_alive()
    for i in range(len(GetThreading)):
        GetThreading[i].join()

    print '@' * 3 + ' ' * 2 + "总共抓取了%s个代理" % len(all_message) + ' ' * 2 + '@' * 3

    for i in range(20):
        t = ipCheck(all_message[((len(all_message) + 19) / 20) * i:((len(all_message) + 19) / 20) * (i + 1)])
        CheckThreading.append(t)
    for i in range(len(CheckThreading)):
        CheckThreading[i].start()
        print CheckThreading[i].is_alive()
    for i in range(len(CheckThreading)):
        CheckThreading[i].join()

    print '@' * 3 + ' ' * 2 + "总共有%s个代理通过校验" % len(aim_ip) + ' ' * 2 + '@' * 3

    t = save_csv(aim_ip)
    counts = t.Save_ip()

    print '@' * 3 + ' ' * 2 + "总共新增%s个代理" % (len(aim_ip) - counts) + ' ' * 2 + '@' * 3