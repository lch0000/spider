# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
from gevent import queue
from gevent import Timeout

import re
import time
import gevent
import urllib2
import requests
import threading
from random import choice

urlqueue = queue.Queue(100)
mylock =  threading.RLock()
urllist = ['https://www.python.org/',
           'https://www.yahoo.com/',
           'http://www.163.com/',
           'http://www.baidu.com',
           'https://github.com']

# 设置超时时间
seconds = 10
timeout = Timeout(seconds)
timeout.start()

def fetch(url):
    print('GET: %s' % url)
    resp = urllib2.urlopen(url)
    data = resp.read()
    print('%d bytes received from %s.' % (len(data), url))

class Urlproducer(threading.Thread):
    '''产生待抓取的url'''
    def __init__(self, theadName):
        threading.Thread.__init__(self)
        self.isRunable = True
        self.threadName =  theadName

    def run(self):
        global urlqueue
        while True and self.isRunable:
            # time.sleep(1)
            gevent.sleep(0.5)
            mylock.acquire();
            if urlqueue.full():
                print "队列已满"
            else:
                newurl = choice(urllist)
                urlqueue.put(newurl)
                print '新增加待抓取网页%s,队列中url数量%d' % (newurl, urlqueue.qsize())
            mylock.release()
        else:
            print "今天不抓了，准备休息了拜拜了！"

    def stop(self):
        self.isRunable = False

class Webparser(threading.Thread):

    def __init__(self, theadName):
        threading.Thread.__init__(self)
        self.isRunable = True
        self.threadName =  theadName

    def run(self):
        global urlqueue
        while True and self.isRunable:
            # time.sleep(5)
            gevent.sleep(5)
            mylock.acquire();
            if not urlqueue.empty():
                allurl = []
                while not urlqueue.empty():
                    allurl.append(gevent.spawn(fetch, urlqueue.get()))
                gevent.joinall(allurl)
            else:
                print "待抓取url数量不足"
            mylock.release()
        else:
            print "抓的差不多了，准备撤了!"

    def stop(self):
        self.isRunable = False


if __name__ == "__main__":
    p1 = Urlproducer("url产生器")
    p1.start()
    c1 =  Webparser("网页抓取器")
    c1.start()
    time.sleep(2*60)
    p1.stop()
    c1.stop()
