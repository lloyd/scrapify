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
  
  def hasMore(self):
    return not self.pageQueue.empty()
  
  def processRoot(self, url):
    u = urllib.urlopen(url)
    html = u.read()
    soup = BeautifulSoup(html)
    for x in soup.findAll('a', attrs={'class': 'category'}):
      loc = urlparse(x['href'])
      if string.find(loc.query, '=app') != -1:
        url = 'https://chrome.google.com/webstore/list/most_popular?' + loc.query
        self.pageQueue.put(("directory", url))

  def processDirectory(self, url):
    print("processing directory: " + url)
    pass

  def processApp(self, url):
    u = urllib.urlopen(url)
    html = u.read()
    u.close()

    soup = BeautifulSoup(html)

    # The page must contain a button with an id of
    # "cx-install-free-btn" for us to process it.
    button = soup.findAll('a', attrs={'id': 'cx-install-free-btn'})
    if button and len(button) > 0:
      # Okay, we can process it.
      pass

crawler = ChromeCrawler()
while (crawler.hasMore()):
  crawler.step()
