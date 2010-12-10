#!/usr/bin/env python2

from urlparse import urlparse
import urllib
import string
from BeautifulSoup import BeautifulSoup

def getCats():
    u = urllib.urlopen("https://chrome.google.com/webstore")
    html = u.read()
    soup = BeautifulSoup(html)
    l = [ ]
    for x in soup.findAll('a', attrs={'class': 'category'}):
        loc = urlparse(x['href'])
        if string.find(loc['query'], '=app'):
            l.append('https://chrome.google.com/webstore/list/most_popular?' + loc['query'])
    return l

for i in getCats():
    print i


