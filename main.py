from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
import json
import os
import sys
import mutagen
from mutagen.id3 import APIC, TRCK, TPE1, TALB

soup = BeautifulSoup(urlopen(sys.argv[1]), 'html.parser')

artist_name = soup.find("div", { "id": "name-section" }).find("a").text
album_title = soup.find("div", { "id": "name-section" }).find("h2").text.strip()
directory_name = ('%s - %s' % (album_title, artist_name)).replace('/', ' - ').replace('|', ' - ').replace('\u200b', '')
print(directory_name)

# mkdir
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, directory_name)
if not os.path.exists(final_directory):
  os.makedirs(final_directory)

# download cover
cover_href = soup.find("a", { "class": "popupImage" })["href"]
cover_path = os.path.join(final_directory, cover_href.split("/").pop()) 
urlretrieve(cover_href, cover_path)
print('Cover image downloaded!')

tracks = json.loads(soup.find(attrs={ "data-tralbum": True })['data-tralbum'])

# download tracks
for x in tracks["trackinfo"]:
  song_path = os.path.join(final_directory, "%s.mp3" % x["title"].replace('/', ' '))
  urlretrieve(x['file']['mp3-128'], song_path)
  audio = mutagen.File(song_path)
  try:
    audio.add_tags()
  except:
    pass
  audio["TRCK"] = TRCK(encoding=3, text=str(x["track_num"]))
  audio["TPE1"] = TPE1(encoding=3, text=artist_name)
  audio["TALB"] = TALB(encoding=3, text=album_title)
  audio['APIC'] = APIC(
    encoding=3,
    mime='image/jpeg',
    type=3,
    desc=u'Cover',
    data=open(cover_path, 'rb').read()
  )
  audio.save()
  print("%d %s downloaded!" % (x["track_num"], x["title"]))

print("All songs of [%s] downloaded!" % directory_name)
