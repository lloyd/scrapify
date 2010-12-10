#!/usr/bin/env python
#
import tornado.httpserver
import tornado.auth
import tornado.ioloop
import tornado.web
import logging
import os
import urlparse

SAVE_CRX_DUMPS = True
CRX_DOWNLOAD_BASE = "https://clients2.google.com/service/update2/crx?response=redirect&x=id%%3D%s%%26lang%%3Den-US%%26uc"

MANIFEST_STORAGE_DIR = "manifests"
CRX_DUMP_DIR = "crx_dump"

class InstallCRXHandler(WebHandler):
  def get(self):
    url = self.get_argument("url", None)
    if not url:
      self.render("error.html", error="Missing required 'url' parameter")
      return
    
    parsed = urlparse.urlparse(url)
    theID = parsed.path[parsed.path.rfind("/")+1:]

    if not self.manifest_exists(theID):
      self.fetch_crx(theID)
      if not self.manifest_exists(theID):
        self.render("error.html", error="Unable to retrieve application manifest.")
        return
    
    dataFD = open(manifest_storage_path(theID), "r")
    manifest = dataFD.read()
    dataFD.close()
    self.render("install.html", manifest)

  def manifest_storage_path(self, theID):
    return "%s/%s" % (MANIFEST_STORAGE_DIR, theID)

  def manifest_exists(self, theID):
    return os.path.exists(manifest_storage_path(theID))

  def fetch_crx(self, theID):
    downloadURL = CRX_DOWNLOAD_BASE % theID

    # Go get it!
    downloadConn = urllib.urlopen(downloadURL)
    downloadBytes = downloadConn.read()
    if SAVE_CRX_DUMPS:
      dumpFile = open("%s/%s.crx" % (CRX_DUMP_DIR, theID), "w")
      dumpFile.write(downloadBytes)
      dumpFile.close()
    
    manifest = CRXConverter().convert(StringIO(downloadBytes))
    outputFile = open(manifest_storage_path(theID), "w")
    outputFile.write(json.dumps(manifest))
    outputFile.close()

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

application = tornado.web.Application([
    (r"/installcrx", InstallCRXHandler) 
	], **settings)


def run():
  try:
    os.mkdir(MANIFEST_STORAGE_DIR)
  except:
    pass

  if SAVE_CRX_DUMPS:
    try:
      os.mkdir(CRX_DUMP_DIR)
    except:
      pass
      
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8400)
  tornado.ioloop.IOLoop.instance().start()
  
if __name__ == '__main__':
  logging.basicConfig(level = logging.DEBUG)
  run()
	
	
