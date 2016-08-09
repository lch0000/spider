# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
from gevent import queue
from gevent import Timeout

import re
import time
import gevent
import urllib2
from bs4 import BeautifulSoup

urlqueue = queue.Queue(100) # 待抓取队列
urllist = ['https://www.python.org/',
           'https://www.yahoo.com/',
           'http://www.163.com/',
           'http://www.baidu.com',
           'https://github.com'] # 从网页中解析出来的url，去重后放入待抓取队列
finished = set() # 已抓取过的url，保留用于去重

# 设置超时时间
seconds = 100
timeout = Timeout(seconds)
timeout.start()

def fetch(url):
    global urllist
    print('GET: %s' % url)
    resp = urllib2.urlopen(url)
    data = resp.read()
    soup = BeautifulSoup(data)
    newurl = soup.find_all('a')
    for x in newurl:
        href = x.get('href')
        if href:
            if href.startswith('http'):
                urllist.append(href)
    print urllist
    finished.add(url)
    print('%d bytes received from %s.' % (len(data), url))

def urlproducer():
    '''从urllist中去重并放入抓取队列'''
    global urllist
    while True:
        yield len(urllist)
        if urlqueue.full():
            print "队列已满"
        else:
            for url in urllist:
                if url not in finished and not urlqueue.full():
                    urlqueue.put(url)
            print '新增加待抓取网页%s,队列中url数量%d' % (len(urllist), urlqueue.qsize())
    else:
        print "今天不抓了，准备休息了拜拜了！"

def webspider(c):
    global urllist
    c.send(None)
    while True:
        if not urlqueue.empty():
            allurl = []
            while not urlqueue.empty():
                allurl.append(gevent.spawn(fetch, urlqueue.get()))
            gevent.joinall(allurl)
        else:
            print "待抓取url数量不足"
            num = c.next()
    else:
        print "抓的差不多了，准备撤了!"

if __name__ == "__main__":
    c = urlproducer()
    webspider(c)
