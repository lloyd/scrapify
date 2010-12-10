#!/usr/bin/env python2

import urlparse
import re
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
    soup = BeautifulSoup(urllib.urlopen(url).read())
    for x in soup.findAll('a', attrs={'class': 'category'}):
      loc = urlparse.urlparse(x['href'])
      if string.find(loc.query, '=app') != -1:
        url = 'https://chrome.google.com/webstore/list/most_popular/1?' + loc.query
        self.pageQueue.put(("directory", url))

  def processDirectory(self, url):
    print("processing directory: " + url)
    soup = BeautifulSoup(urllib.urlopen(url).read())

    # parse out all app urls
    for x in soup.findAll('a', attrs={'class': 'title-a'}):
      app_url = 'https://chrome.google.com' + x['href']
      self.pageQueue.put(("app", app_url))

    # now next page in pagination if required - if it's X of Y then there's another
    # page!

    paginationDeets = soup.find('div', text=re.compile("\d+ of \d+"))
    if (paginationDeets):
      nextPage = str(1 + int(re.search('/(\d+)\?', url).group(1)))
      nxt = re.sub('/\d+\?', "/" + nextPage + "?", url)
      self.pageQueue.put(("directory", nxt))

  def processApp(self, url):
    print("processing app: " + url)
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
