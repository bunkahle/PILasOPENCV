from __future__ import print_function
import PILasOPENCV as Image
# from PIL import Image
import sys

if sys.version[0] == "2":
    py3 = False
else:
    py3 = True

url = 'https://raw.githubusercontent.com/bunkahle/PILasOPENCV/master/tests/lena.jpg'

if py3:
    try:
        import requests
        resp = requests.get(url, stream=True).raw
    except requests.exceptions.RequestException as e:
        print("Unable to retrieve image")
        sys.exit(1)
else:
    try:
        import urllib2, cStringIO
        resp = cStringIO.StringIO(urllib2.urlopen(url).read())
    except:
        print("Unable to retrieve image")
        sys.exit(1)
try:
    img = Image.open(resp)
except IOError:
    print("Unable to open image")
    sys.exit(1)

img.show()