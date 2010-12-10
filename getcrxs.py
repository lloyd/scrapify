#!/usr/bin/env python2

from urlparse import urlparse
import urllib
import string
from BeautifulSoup import BeautifulSoup
from Queue import Queue

class ChromeCrawler(object):
  def __init__(self):
    self.pageQueue = Queue()
    self.pageQueue.put(("root", "https://chrome.google.com/webstore"))
    
  def step(self):
    if not self.pageQueue.empty():
      page = self.pageQueue.get()
      if page[0] == "root":
        self.processRoot(page[1])
      elif page[0] == "directory":
        self.processDirectory(page[1])
      elif page[0] == "app":
        self.processApp(page[1])
  
  def processRoot(self, url):
    u = urllib.urlopen("https://chrome.google.com/webstore")
    html = u.read()
    soup = BeautifulSoup(html)
    l = [ ]
    for x in soup.findAll('a', attrs={'class': 'category'}):
        loc = urlparse(x['href'])
        if string.find(loc['query'], '=app'):
            l.append('https://chrome.google.com/webstore/list/most_popular?' + loc['query'])

    # put 'em in the queue
    return l
  
  def processDirectory(self, url):
    pass

  def processApp(self, url):
    pass
    

for i in getCats():
    print i


