import zipfile
import json
import base64
import urlparse
import logging

class CRXConverter(object):
  """Extracts the manifest from a Chrome Store .crx-style web app,
  and pulls resources from the .crx as needed to construct a self-contained
  manifest with OpenWebApp syntax."""
  
  def __init__(self):
    pass
  
  def convert(self, inputFile):
    zip = zipfile.ZipFile(inputFile, "r")
    
    manifestFile = zip.open("manifest.json", "r")
    manifest = json.loads(manifestFile.read())

    self.convertURLs(manifest)
    self.convertIcons(zip, manifest)
    self.convertPermissions(manifest)
    self.removeCruft(manifest)
    manifest["manifest_version"] = "0.2"
    manifest["default_locale"] = "en-US"
    return manifest
    
  def convertURLs(self, manifest):
    # CRX uses app: {urls: [url], launch: { web_url: urh } }
    # OWA uses base_url: url and launch_path
    
    # Since we are not scoping these apps (they will be "bookmark apps"
    # in OWA lingo), we ignore the urls parameter and just extract
    # launch.
    
    if "app" in manifest:
      app = manifest["app"]
      if "launch" in app:
        launch = app["launch"]
        if "web_url" in launch:
          web_url = launch["web_url"]
          parsed_url = urlparse.urlparse(web_url)
          path = parsed_url.path
          idx = path.rfind('/')
          if idx >= 0:
            fname = path[idx+1:]
            dir = path[:idx+1]
          base_url = parsed_url.scheme + "://" + parsed_url.netloc + dir
          
          manifest["base_url"] = base_url
          manifest["launch_path"] = fname
          del manifest["app"]
        else:
          raise Exception("Cannot convert; no web_url in app/launch")
      else:
        raise Exception("Cannot convert; no launch in app")
    else:
      raise Exception("Cannot convert; no app in manifest")

    if "update_url" in manifest:
      del manifest["update_url"]
    
  def convertPermissions(self, manifest):
    if "permissions" in manifest:
      manifest["capabilities"] = manifest["permissions"]
      del manifest["permissions"]
      
  def convertIcons(self, zip, manifest):
    if "icons" in manifest:
      for key, value in manifest["icons"].iteritems():
        if value.startswith("data"):
          pass
        elif value.startswith("http"):
          pass
        else:
          try:
            iconFile = zip.open(value, "r")
            iconFile64 = base64.b64encode(iconFile.read())
            
            flavor = value[value.rfind('.')+1:]
            manifest["icons"][key] = "data:image/" + flavor + ";base64," + iconFile64
          except Exception, e:
            logging.warn("Unable to embed icon %s" % value)
  
  def removeCruft(self, manifest):
    if "key" in manifest:
      del manifest["key"]
    if "version" in manifest:
      del manifest["version"]


if __name__ == "__main__":
  import sys
  conv = CRXConverter()
  manifest = conv.convert(open(sys.argv[1], "r"))
  print manifest
