import zipfile
import json
import base64

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
    self.convertIcons(zip, manifest)
    return manifest
    
    
  def convertIcons(self, zip, manifest):
    if "icons" in manifest:
      for key, value in manifest["icons"].iteritems():
        if value.startswith("data"):
          pass
        elif value.startswith("http"):
          pass
        else:
          iconFile = zip.open(value, "r")
          iconFile64 = base64.b64encode(iconFile.read())
          
          flavor = value[value.rfind('.')+1:]
          manifest["icons"][key] = "data:image/" + flavor + ";base64," + iconFile64
    


conv = CRXConverter()
manifest = conv.convert(open("test.crx", "r"))

print manifest
  