import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import subprocess
import os
import traceback

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="YouTube Downloader with Mirroring",
    page_icon="🎬",
    layout="centered"
)

st.sidebar.header("Optional: Cookies")
cookies_file = st.sidebar.file_uploader("Upload your YouTube cookies.txt", type=["txt"])
cookie_path = None
if cookies_file:
    cookie_path = os.path.join(DOWNLOAD_FOLDER, "cookies.txt")
    with open(cookie_path, "wb") as f:
        f.write(cookies_file.getbuffer())

st.title("🎬 YouTube Video Downloader with Mirroring")
video_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Download Video"):
    if not video_url.strip():
        st.warning("Enter a valid YouTube URL.")
    else:
        with st.spinner("Downloading..."):
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title).100s.%(ext)s'),
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'retries': 5,
                    'quiet': False,
                    'ignoreerrors': True,
                    'noplaylist': True,
                    'geo_bypass': True,
                    'nocheckcertificate': True,
                    'concurrent_fragment_downloads': 1,
                    'http_headers': {
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/117.0.0.0 Safari/537.36'
                        ),
                        'Referer': 'https://www.youtube.com/',
                        'Accept-Language': 'en-US,en;q=0.9'
                    }
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

                if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
                    st.error("Download failed or YouTube blocked the video (0 bytes). Try with cookies.txt.")
                    st.stop()

                st.success("✅ Download completed!")
                st.write(f"**Title:** {info.get('title','Unknown')}")
                st.write(f"**Size:** {os.path.getsize(file_name) / (1024 * 1024):.2f} MB")

                with open(file_name, "rb") as f:
                    st.download_button("⬇ Download Original", data=f, file_name=os.path.basename(file_name))
                try:
                    st.video(file_name)
                except:
                    st.warning("Video preview not available.")

                # Mirroring
                mirrored_file = file_name.replace(".mp4", "_mirrored.mp4")
                if not os.path.exists(mirrored_file):
                    st.info("Mirroring with ffmpeg...")
                    try:
                        subprocess.run([
                            "ffmpeg", "-y",
                            "-i", file_name,
                            "-vf", "hflip",
                            "-c:a", "copy",
                            mirrored_file
                        ], check=True)
                        st.success("✅ Mirrored version created!")
                    except subprocess.CalledProcessError as e:
                        st.error("❌ ffmpeg mirroring failed.")
                        st.text(e)

                if os.path.exists(mirrored_file):
                    with open(mirrored_file, "rb") as f:
                        st.download_button("⬇ Download Mirrored", data=f, file_name=os.path.basename(mirrored_file))
                    try:
                        st.video(mirrored_file)
                    except:
                        st.warning("Mirrored preview not available.")

            except DownloadError as de:
                st.error(f"❌ yt-dlp error: {de}")
            except Exception as e:
                st.error("❌ Unexpected error occurred.")
                st.text(traceback.format_exc())
