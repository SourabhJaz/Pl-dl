from bs4 import BeautifulSoup
from urllib import urlopen
from urlparse import parse_qs
import os
import re

def get_playlist(parsed_page):
    playlist = parsed_page.find('div',class_='playlist-videos-container yt-scrollbar-dark yt-scrollbar')
    return playlist

def get_video_urls(playlist,youtube_domain):
    videos = playlist.find_all('li',class_='yt-uix-scroller-scroll-unit')
    video_urls = []
    for video in videos:
        video_element = video.find('a',class_='playlist-video')
        video_url = youtube_domain + video_element['href']
        video_urls.append(unicode(video_url))
    return video_urls

def write_file(file_name,stream):
    with open(file_name, 'ab') as f:
        f.write(stream.read())

def get_download_link(file_info):
    url_map = parse_qs(file_info['url_encoded_fmt_stream_map'][0])
    url_map_split = url_map['url']
    download_url = url_map_split[0]
    return download_url

def get_video_size(download):
    download_info = download.info()
    download_size = download_info.getheaders("Content-Length")[0]
    return download_size

def resume_download(file_size, file_name, download_size, download_url):
    print("Resuming download...")
    resume_url = "{0}&range={1}-{2}".format(download_url,file_size,download_size)
    download = urlopen(resume_url)
    write_file(file_name,download)

def get_file_info(url,youtube_domain):
    video_id = url.split('?v=')[1]
    file_info_url = youtube_domain+'/get_video_info?video_id='+video_id
    response_file = urlopen(file_info_url)
    file_info_coded = response_file.read()
    file_info = parse_qs(file_info_coded)
    title = file_info['title'][0]
    return file_info, title

def get_video_name(title):
    video_name = title+'.mp4'
    file_name = re.sub(r'[\\&,\'|"]','',video_name)
    return file_name

def start_download(file_name, download_size, download_file, download_url):
    print("Downloading:{0} \nSize: {1} bytes".format(file_name,download_size))    
    if os.path.isfile(file_name):
        file_size = os.path.getsize(file_name)
        if file_size < download_size:
            resume_download(file_size,file_name,download_size,download_url)
    else:
        write_file(file_name,download_file)
    print('Download complete!')

def download_video(url,youtube_domain):
    try:
        file_info, title = get_file_info(url,youtube_domain)
        download_url = get_download_link(file_info)
        download_file = urlopen(download_url)
        download_size = get_video_size(download_file)
        file_name = get_video_name(title)
        start_download(file_name, download_size, download_file, download_url)
    except Exception as e:
        print('Download failed! ',e)

playlist_url = "https://www.youtube.com/watch?v=yL36kgWHkAM"
youtube_domain = "https://www.youtube.com"
response = urlopen(playlist_url)
parsed_page = BeautifulSoup(response,'html.parser')
playlist = get_playlist(parsed_page)
if playlist != None:
    video_urls = get_video_urls(playlist,youtube_domain)
else:
    video_urls = [playlist_url]

for url in video_urls:
    download_video(url,youtube_domain)

# https://www.youtube.com/watch?v=nhQb1QRsSgs
# https://www.youtube.com/watch?v=BAhRc5u_yO4
# https://www.youtube.com/watch?v=z-diRlyLGzo
# https://www.youtube.com/watch?v=AR-QHXaAaJU
# https://www.youtube.com/watch?v=yL36kgWHkAM

"""
#   audio download   
    audio_url_map = parse_qs(file_info['adaptive_fmts'][0])
    url_map_split = audio_url_map['url']
""" 