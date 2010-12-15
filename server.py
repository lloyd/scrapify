#!/usr/bin/env python
#
import tornado.httpserver
import tornado.auth
import tornado.ioloop
import tornado.httpclient
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
    return "%s/%s/%s" % (os.environ["HOME"], MANIFEST_STORAGE_DIR, theID)

  def manifest_exists(self, theID):
    return os.path.exists(self.manifest_storage_path(theID))

  def fetch_crx(self, theID):
    downloadURL = CRX_DOWNLOAD_BASE % theID

    # Go get it!
    downloadConn = urllib.urlopen(downloadURL)
    downloadBytes = downloadConn.read()
    if SAVE_CRX_DUMPS:
      dumpFile = open("%s/%s/%s.crx" % (os.environ["HOME"], CRX_DUMP_DIR, theID), "w")
      dumpFile.write(downloadBytes)
      dumpFile.close()
    
    manifest = CRXConverter().convert(StringIO(downloadBytes))
    outputFile = open(self.manifest_storage_path(theID), "w")
    outputFile.write(json.dumps(manifest))
    outputFile.close()




class ConvertCRXHandler(tornado.web.RequestHandler):
  def manifest_storage_path(self, theID):
    return "%s/%s/%s" % (os.environ["HOME"], MANIFEST_STORAGE_DIR, theID)

  def manifest_exists(self, theID):
    return os.path.exists(self.manifest_storage_path(theID))


  @tornado.web.asynchronous
  def get(self):
    url = self.get_argument("url", None)
    if not url: 
      logging.error("Missing required 'url' parameter")
      raise tornado.web.HTTPError(400)
    
    # Extract the ID from CRX URL
    logging.debug("convertcrx url is %s" % url)
    parsed = urlparse.urlparse(url)
    path = parsed.path
    hashCheck = path.rfind('#')
    if hashCheck > 0:
      path = path[:hashCheck]
    theID = path[path.rfind("/")+1:]
    logging.debug("id is %s" % theID)

    # See if we have a cached one
    if not self.manifest_exists(theID):
      # If not, go get it
      self.fetch_crx(theID)
    else:
      dataFD = open(self.manifest_storage_path(theID), "r")
      manifest = json.loads(dataFD.read())
      dataFD.close()
      self.on_manifest_available(manifest)

  def fetch_crx(self, theID):
    downloadURL = CRX_DOWNLOAD_BASE % theID

    http = tornado.httpclient.AsyncHTTPClient()
    crxRequest = tornado.httpclient.HTTPRequest(downloadURL)
    crxRequest.crxid = theID
    http.fetch(crxRequest, callback=self.on_fetch_response)
    
  def on_fetch_response(self, response):
    if response.error:
      logging.error("%s %s" % (response.error, response.body))
      logging.error("Unable to retrive application manifest")
      raise tornado.web.HTTPError(500)
    else:
      if SAVE_CRX_DUMPS:
        dumpFile = open("%s/%s/%s.crx" % (os.environ["HOME"], CRX_DUMP_DIR, response.request.crxid), "w")
        dumpFile.write(response.body)
        dumpFile.close()
      manifest = CRXConverter().convert(StringIO(response.body))
      outputFile = open(self.manifest_storage_path(response.request.crxid), "w")
      outputFile.write(json.dumps(manifest))
      outputFile.close()
      self.on_manifest_available(manifest)

  def on_manifest_available(self, manifest):
    self.write(json.dumps(manifest))
    self.finish()

settings = {
  "static_path": os.path.join(os.path.dirname(__file__), "static"),
  "debug":True
}

application = tornado.web.Application([
    (r"/installcrx", InstallCRXHandler),
    (r"/convertcrx", ConvertCRXHandler)
], **settings)


def run():
  try:
    os.mkdir("%s/%s" % (os.environ["HOME"], MANIFEST_STORAGE_DIR))
  except:
    pass

  if SAVE_CRX_DUMPS:
    try:
      os.mkdir("%s/%s" % (os.environ["HOME"], CRX_DUMP_DIR))
    except:
      pass
      
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8600)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  logging.basicConfig(level = logging.DEBUG)
  run()
	
	
