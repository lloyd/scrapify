#!/usr/bin/env python
#
import tornado.httpserver
import tornado.auth
import tornado.ioloop
import tornado.web
import logging
import os
import urllib
import urlparse
import json
from cStringIO import StringIO
from crxconverter import CRXConverter

SAVE_CRX_DUMPS = True
CRX_DOWNLOAD_BASE = "https://clients2.google.com/service/update2/crx?response=redirect&x=id%%3D%s%%26lang%%3Den-US%%26uc"

MANIFEST_STORAGE_DIR = ".server_manifests"
CRX_DUMP_DIR = ".server_crx_dump"

class InstallCRXHandler(tornado.web.RequestHandler):
  def get(self):
    url = self.get_argument("url", None)
    if not url:
      self.render("error.html", error="Missing required 'url' parameter")
      return
    
    logging.debug("installcrx url is %s" % url)
    parsed = urlparse.urlparse(url)
    path = parsed.path
    hashCheck = path.rfind('#')
    if hashCheck > 0:
      path = path[:hashCheck]
      logging.debug("removed hash %s" % path)
    theID = path[path.rfind("/")+1:]
    logging.debug("id is %s" % theID)

    if not self.manifest_exists(theID):
      self.fetch_crx(theID)
      if not self.manifest_exists(theID):
        self.render("error.html", error="Unable to retrieve application manifest.")
        return
    
    dataFD = open(self.manifest_storage_path(theID), "r")
    manifest = dataFD.read()
    dataFD.close()
    self.render("install.html", manifest=manifest, return_to=url)

  def manifest_storage_path(self, theID):
    return "%s/%s/%s" % (os.env["HOME"], MANIFEST_STORAGE_DIR, theID)

  def manifest_exists(self, theID):
    return os.path.exists(self.manifest_storage_path(theID))

  def fetch_crx(self, theID):
    downloadURL = CRX_DOWNLOAD_BASE % theID

    # Go get it!
    downloadConn = urllib.urlopen(downloadURL)
    downloadBytes = downloadConn.read()
    if SAVE_CRX_DUMPS:
      dumpFile = open("%s/%s/%s.crx" % (os.env["HOME"], CRX_DUMP_DIR, theID), "w")
      dumpFile.write(downloadBytes)
      dumpFile.close()
    
    manifest = CRXConverter().convert(StringIO(downloadBytes))
    outputFile = open(self.manifest_storage_path(theID), "w")
    outputFile.write(json.dumps(manifest))
    outputFile.close()

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "debug":True
}

application = tornado.web.Application([
    (r"/installcrx", InstallCRXHandler) 
	], **settings)


def run():
  try:
    os.mkdir("%s/%s" % (os.env["HOME"], MANIFEST_STORAGE_DIR))
  except:
    pass

  if SAVE_CRX_DUMPS:
    try:
      os.mkdir("%s/%s" % (os.env["HOME"], CRX_DUMP_DIR))
    except:
      pass
      
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8400)
  tornado.ioloop.IOLoop.instance().start()
  
if __name__ == '__main__':
  logging.basicConfig(level = logging.DEBUG)
  run()
	
	
