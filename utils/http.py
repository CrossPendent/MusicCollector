#-*- coding:utf-8 -*-

import urllib.request
import time

from utils import debug


def getHTMLDocument(url, autoRetry=True):
  listAgent = ['Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36']
  retryDelay = [0.1, 0.5, 1, 2, 5, 10, 30, 60, 180, 300]
  conLoop = True
  agentCount = 0
  delayCount = 0
  while(conLoop):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Host', 'www.melon.com'),
                         ('Connection', 'Keep-Alive'),
                         # ('Upgrade-Insecure-Requests', '1'),
                         ('User_agent', listAgent[agentCount]),
                         ('X-Requested-With', 'XMLHttpRequest'),
                         ('Accept', '*/*'),
                         # ('Accept-Encoding', 'gzip, deflate'),
                         ('Accept-Language', 'en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7'),
                         ("Content-Type", "application/x-www-form-urlencoded;charset=utf-8"),
                         ('Cookie', 'SCOUTER=z39vkmg7pd9j91; PCID=15250529259645155634188; WMONID=GxTfcjDmib7; POC=WP10')]
    try:
      html = opener.open(url)
    except ConnectionResetError as e:
      if autoRetry:
        debug.log('Connection denied from \'{}\''.format(url))
        debug.log('Try again using another header after {}sec...'.format(retryDelay[delayCount]))
        agentCount = (agentCount+1) % len(listAgent)
        time.sleep(retryDelay[delayCount])
        delayCount = (delayCount+1) % len(retryDelay)
      else:
        debug.log('Document couldn\'t be get from {}'.format(url))
        return None
    else:
      conLoop = False
  return html.read()
