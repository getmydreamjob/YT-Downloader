import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import os
import traceback

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.sidebar.header("Optional: Cookies")
cookies_file = st.sidebar.file_uploader("Upload your YouTube cookies.txt", type=["txt"])
cookie_path = None
if cookies_file:
    cookie_path = os.path.join(DOWNLOAD_FOLDER, "cookies.txt")
    with open(cookie_path, "wb") as f:
        f.write(cookies_file.getbuffer())

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 YouTube Video Downloader")
video_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Download Video"):
    if not video_url.strip():
        st.warning("Enter a valid YouTube URL.")
    else:
        with st.spinner("Downloading..."):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                    'merge_output_format': 'mp4',
                    # pretend to be Chrome
                    'http_headers': {
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/115.0.0.0 Safari/537.36'
                        ),
                        'Referer': 'https://www.youtube.com',
                        'Accept-Language': 'en-US,en;q=0.9',
                    },
                    # Bypass geo-restriction
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    # retry a few times
                    'retries': 3,
                }
                if cookie_path:
                    ydl_opts['cookiefile'] = cookie_path

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    if info.get('is_live'):
                        st.warning("Live streams are not supported.")
                        st.stop()

                    info = ydl.extract_info(video_url, download=True)
                    file_name = ydl.prepare_filename(info)
                    if not file_name.endswith(".mp4"):
                        file_name += ".mp4"

                st.success("Download completed!")
                st.write(f"**Title:** {info.get('title','Unknown')}")

                size_mb = os.path.getsize(file_name)/(1024*1024)
                st.write(f"**Size:** {size_mb:.1f} MB")

                if size_mb <= 500:
                    with open(file_name,"rb") as f:
                        st.download_button("Download", data=f, file_name=os.path.basename(file_name))
                else:
                    st.info(f"File is large ({size_mb:.1f} MB). Fetch it from `{DOWNLOAD_FOLDER}` on the server.")

                if size_mb <= 200:
                    st.video(file_name)

            except DownloadError as de:
                st.error(f"Download failed: {de}")
                st.info(
                    "403 means YouTube blocked access. Ensure your cookies.txt is from a logged-in account "
                    "and try again, or the video may be private/age-restricted."
                )
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.text(traceback.format_exc())
