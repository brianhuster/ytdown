# Python
import streamlit as st
from pytube import YouTube
import base64
import os
import re

def is_valid_youtube_url(url):
    youtube_url_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return re.match(youtube_url_pattern, url) is not None

def get_streams(url, download_type):
    if not is_valid_youtube_url(url):
        st.error('Invalid YouTube URL')
        return [], []
    
    yt = YouTube(url)
    if download_type == 'Video':
        streams = yt.streams.filter(progressive=True)
        options = [(stream.resolution) for stream in streams]
    elif download_type == 'Audio':
        streams = yt.streams.filter(only_audio=True)
        options = [(stream.abr) for stream in streams]
    elif download_type == 'Subtitles':
        yt.bypass_age_gate()
        streams = yt.captions
        print(streams)
        options = [(caption.name) for caption in streams]
    return streams, options

def get_download_link(file_path):
    with open(file_path, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">Click here to download</a>'
        return href

st.title('YouTube Video Downloader')

url = st.text_input('Enter YouTube video URL')

download_type = st.selectbox('Select download type', ['Video', 'Audio', 'Subtitles'])

streams, options = get_streams(url, download_type) if url else ([], [])

stream = st.selectbox('Select stream', options)

if stream:
    if st.button('Get download link'):
        index=options.index(stream)
        try:
            if download_type == 'Subtitles':
                file_path = 'subtitles.srt'
                with open(file_path, 'w') as f:
                    f.write(streams[index].generate_srt_captions())
            else:
                file_path = streams[index].download()
            
            st.success('Successfully get download link!')
            st.markdown(get_download_link(file_path), unsafe_allow_html=True)
            
            os.remove(file_path)
        except Exception as e:
            st.error(f'Error: {e}')