from bs4 import BeautifulSoup
from urllib import urlopen, urlencode
from time import sleep
from urlparse import parse_qs
import os
import re

playlist_url = "https://www.youtube.com/watch?v=6LedYr5tQUs&list=PLTB0eCoUXErZe2pMrH3qO4tHtw-K0QKb_"
response = urlopen(playlist_url)
parsed_page = BeautifulSoup(response,'html.parser')
playlist = parsed_page.find('div',class_='playlist-videos-container yt-scrollbar-dark yt-scrollbar')

videos = playlist.find_all('li',class_='yt-uix-scroller-scroll-unit')
video_urls = []
youtube_domain = "https://www.youtube.com"
for video in videos:
    video_element = video.find('a',class_='playlist-video')
    video_url = youtube_domain + video_element['href']
    video_urls.append(unicode(video_url))

for url in video_urls:
    video_id = url.split('?v=')[1]
    file_info_url = youtube_domain+'/get_video_info?video_id='+video_id
    response_file = urlopen(file_info_url)
    file_info_coded = response_file.read()
    file_info = parse_qs(file_info_coded)
    title = file_info['title'][0]
    url_map = parse_qs(file_info['url_encoded_fmt_stream_map'][0])
    url_map_split = url_map['url']
    download_url = url_map_split[0]
    download = urlopen(download_url)
    download_info = download.info()
    download_size = download_info.getheaders("Content-Length")[0]
    video_name = title+'.mp4'
    file_name = re.sub(r'[\\&,\'|]','',video_name)
    print("Downloading:{0} {1}bytes".format(file_name,download_size))    
    if os.path.isfile(file_name):
        print("File already present!")
        file_size = os.path.getsize(file_name)
        if file_size < download_size:
          print("Resuming download...")
          download_url = "{0}&range={1}-{2}".format(download_url,file_size,download_size)
          download = urlopen(download_url)
          with open(file_name, 'ab') as f:
          	f.write(download.read())
        print('Download complete!')
        continue
    with open(file_name, 'wb',0) as f:
    	f.write(download.read())


