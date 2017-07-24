from bs4 import BeautifulSoup
from urllib import urlopen
from urlparse import parse_qs
import sys
import os
import re
sys.path.append('/usr/local/lib/python2.7/site-packages')
from PyQt4 import QtCore, QtGui 
from Pl_layout import Ui_MainWindow

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
    while retry < 5:
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

def parse_input_arguments(video_url, media_type, start_index):
    youtube_domain = "https://www.youtube.com"
    handle_video_download(video_url, start_index, media_type)

class AppGui(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)    
        self.ui.pushButton.clicked.connect(self.pass_inputs_to_downloader)

    def pass_inputs_to_downloader(self):
        video_url = self.ui.lineEdit.text()
        media_type = self.get_media_type()
        start_index = self.get_start_index()
        parse_input_arguments(video_url, media_type, start_index)

    def get_media_type(self):
        media_type_video_button = self.ui.radioButton
        media_type_audio_button = self.ui.radioButton_2
        if media_type_video_button.isChecked():
            media_type = 'video'
        else:
            media_type = 'audio'
        return media_type

    def get_start_index(self):
        start_index_playlist_button = self.ui.radioButton_3
        start_index_current_button = self.ui.radioButton_4
        if start_index_playlist_button.isChecked():
            start_index = 'origin'
        else:
            start_index = 'current'
        return start_index

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = AppGui()
    window.show()
    app.exec_()
