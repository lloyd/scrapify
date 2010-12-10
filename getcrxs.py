#!/usr/bin/env python2

import urllib
from BeautifulSoup import BeautifulSoup

def getCats():
    u = urllib.urlopen("https://chrome.google.com/webstore")
    html = u.read()
    soup = BeautifulSoup(html)
    l = [ ]
    for x in soup.findAll('a', attrs={'class': 'category'}):
        l.append(x['href'])
    return l

print getCats()

