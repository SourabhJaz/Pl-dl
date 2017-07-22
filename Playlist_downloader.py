from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import parse_qs
import sys
import os
import re

def get_input_arguments():
	playlist_url = sys.argv[1]
	if len(sys.argv) > 2:
		start_index = 'current'
	else:
		start_index = 'origin' 
	if len(sys.argv) > 3:
		stream_type = sys.argv[3]
	else:
		stream_type = 'video'   
	return playlist_url, start_index, stream_type

def handle_video_download(playlist_url, start_index, stream_type):
	playlist_section = get_playlist_section(playlist_url)
	videos_to_download = []
	if playlist_section != None:
		playlist_video_urls = get_playlist_video_urls(playlist_section,youtube_domain)
	else:
		playlist_video_urls = [playlist_url]
	videos_to_be_downloaded = get_videos_to_be_dowloaded(playlist_url, playlist_video_urls, start_index)
	for url in videos_to_be_downloaded:
		download_video(url,youtube_domain,stream_type)


def get_playlist_section(playlist_url):
    response = urlopen(playlist_url)
    parsed_page = BeautifulSoup(response,'html.parser')
    playlist = parsed_page.find('div',class_='playlist-videos-container yt-scrollbar-dark yt-scrollbar')
    return playlist

def get_playlist_video_urls(playlist,youtube_domain):
    videos = playlist.find_all('li',class_='yt-uix-scroller-scroll-unit')
    video_urls = []
    for video in videos:
        video_element = video.find('a',class_='playlist-video')
        video_url = youtube_domain + video_element['href']
        video_urls.append(unicode(video_url))
    return video_urls

def get_videos_to_be_dowloaded(playlist_url, video_urls, start_index):
	if start_index == 'origin' or len(video_urls) < 2:
		videos_to_be_downloaded = video_urls
	else:
		current_video_url, _current_video_indexing = playlist_url.split('&',1)
		videos_to_be_downloaded = get_videos_starting_current_url(current_video_url, video_urls)
	return videos_to_be_downloaded    


def get_videos_starting_current_url(current_video_url, video_urls):
	index_of_current_video = get_index_of_current_video(current_video_url, video_urls)
	if index_of_current_video != None:
		videos_from_current_url = video_urls[index_of_current_video :]
	else:
		videos_from_current_url = []
	return videos_from_current_url

def get_index_of_current_video(current_video_url, video_urls):
	number_of_videos = len(video_urls)
	for video_index in range(0, number_of_videos):
		if current_video_url in video_urls[video_index]:
			return video_index
	return None

def write_file(file_name,stream):
    with open(file_name, 'ab', 0) as f:
        while True:
            one_kb = stream.read(1024)
            if not one_kb:
                break
            f.write(one_kb)

def get_download_link(file_info):
    url_map = parse_qs(file_info['url_encoded_fmt_stream_map'][0])
    url_map_split = url_map['url']
    download_url = url_map_split[0]
    return download_url

def get_audio_download_link(file_info):
    adaptive_url_map = parse_qs(file_info['adaptive_fmts'][0])
    url_map_split = adaptive_url_map['url']
    audio_url = url_map_split[-1]
    return audio_url

def get_stream_url(file_info, stream_type):
        if stream_type != 'audio':
            download_url = get_download_link(file_info)
        else:
            download_url = get_audio_download_link(file_info) 
        return download_url

def get_video_size(download):
    download_info = download.info()
    download_size = int(download_info.getheaders("Content-Length")[0])
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
    if 'title' not in file_info:
        raise Exception('Video is copyrighted or restricted')
    title = file_info['title'][0]
    return file_info, title

def get_video_name(title, stream_type):
    if stream_type != 'audio':
        content_name = title+'.mp4'
    else:
        content_name = title+'.mp3'        
    file_name = re.sub(r'[^(a-z)(A-Z)(0-9) .]','',content_name)
    return file_name

def start_download(file_name, download_size, download_file, download_url):
    if os.path.isfile(file_name):
        file_size = os.path.getsize(file_name)
        if file_size < download_size:
            resume_download(file_size,file_name,download_size,download_url)
    else:
        write_file(file_name,download_file)
    print('Download complete!')

def attempt_download(file_info,title,stream_type):
    retry = 0
    while retry < 10:
        download_url = get_stream_url(file_info, stream_type)                       
        download_file = urlopen(download_url)
        download_size = get_video_size(download_file)
        if download_size > 0:
            break
        retry += 1
    if download_size == 0:
        raise Exception('Video is copyrighted or restricted')
    file_name = get_video_name(title, stream_type)
    print("Downloading:{0} \nSize: {1} bytes".format(file_name,download_size))            
    start_download(file_name, download_size, download_file, download_url)    

def download_video(url,youtube_domain,stream_type):
    try:
        file_info,title = get_file_info(url,youtube_domain)
        attempt_download(file_info,title,stream_type)
    except Exception as e:
        print('Download failed! ',e.args)

if __name__ == "__main__":
	youtube_domain = "https://www.youtube.com"
	playlist_url, start_index, stream_type = get_input_arguments()
	handle_video_download(playlist_url, start_index, stream_type)

